from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

# ====== ŚCIEŻKI WZGLĘDNE DO STRUKTURY PROJEKTU ======
WORKCELL_DIR = Path(__file__).parent          # Workcell/
PROJECT_ROOT = WORKCELL_DIR.parent            # root projektu
OUTPUT_XLSX = PROJECT_ROOT / "Koszty_template.xlsx"

sys.path.insert(0, str(PROJECT_ROOT))

from Workcell._workcell_definitions import (
    Workcell,
    ParamChoice,
    ParamNumber,
    ParamTablePick,
)

# ====== STYL ======
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF")
BOLD_FONT = Font(bold=True)
SECTION_FILL = PatternFill("solid", fgColor="D9E1F2")
SECTION_FONT = Font(bold=True)

PLACEHOLDER_ROWS = 20


# ---------- helpers ----------

def _safe_sheet_name(name: str) -> str:
    return re.sub(r"[:\\/?*\[\]]", "_", name)[:31]


def _autosize(ws):
    for col in range(1, ws.max_column + 1):
        max_len = 0
        for row in range(1, ws.max_row + 1):
            v = ws.cell(row=row, column=col).value
            if v:
                max_len = max(max_len, len(str(v)))
        ws.column_dimensions[get_column_letter(col)].width = max(12, min(max_len + 2, 50))


def _import_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def _find_workcells(mod) -> list[Workcell]:
    return [v for v in vars(mod).values() if isinstance(v, Workcell)]


# ---------- główna funkcja ----------

def generate_cost_template() -> Path:
    """
    Generuje Koszty_template.xlsx na podstawie definicji gniazd.
    Zwraca ścieżkę do wygenerowanego pliku.
    """
    wb = Workbook()
    index_rows = []

    for py in WORKCELL_DIR.glob("*.py"):
        if py.name.startswith("_"):
            continue

        mod = _import_module(py)
        for wc in _find_workcells(mod):
            _generate_workcell_sheet(wb, wc)
            index_rows.append(_index_row(wc, py.name))

    _generate_index_sheet(wb, index_rows)
    wb.save(OUTPUT_XLSX)
    return OUTPUT_XLSX


# ---------- generowanie arkuszy ----------

def _generate_workcell_sheet(wb: Workbook, wc: Workcell):
    ws = wb.create_sheet(_safe_sheet_name(f"WC__{wc.name}"))

    choices = [p for p in wc.params if isinstance(p, ParamChoice)]
    if len(choices) > 1:
        raise ValueError(f"Gniazdo '{wc.name}' ma >1 ParamChoice")

    if choices:
        choice_key = choices[0].key
        choice_values = choices[0].options
    else:
        choice_key = "DEFAULT"
        choice_values = ["DEFAULT"]

    number_params = [
        p for p in wc.params
        if isinstance(p, ParamNumber) and p.source == "cost_table"
    ]
    table_params = [
        p for p in wc.params
        if isinstance(p, ParamTablePick) and p.source == "cost_table"
    ]

    row = 1
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
    ws.cell(row=row, column=1, value=f"{wc.name} (id={wc.id})").font = Font(bold=True, size=14)
    row += 2

    for cv in choice_values:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
        ws.cell(row=row, column=1, value=f"{choice_key} = {cv}").font = SECTION_FONT
        row += 1

        ws.append(["param_key", "label", "unit", "value"])
        for c in range(1, 5):
            ws.cell(row=row, column=c).fill = HEADER_FILL
            ws.cell(row=row, column=c).font = HEADER_FONT
        row += 1

        for p in number_params:
            ws.append([p.key, p.label, getattr(p, "unit", ""), ""])
            row += 1

        row += 1

        for tp in table_params:
            ws.append([f"TABLE: {tp.table_name}", "", "", ""])
            ws.cell(row=row, column=1).font = BOLD_FONT
            row += 1

            ws.append(["item_key", "label", "unit", "value"])
            for c in range(1, 5):
                ws.cell(row=row, column=c).fill = HEADER_FILL
                ws.cell(row=row, column=c).font = HEADER_FONT
            row += 1

            row += PLACEHOLDER_ROWS

        row += 1

    _autosize(ws)


def _index_row(wc: Workcell, filename: str):
    return [
        wc.id,
        wc.name,
        filename,
    ]


def _generate_index_sheet(wb: Workbook, rows):
    ws = wb.active
    ws.title = "INDEX"
    ws.append(["workcell_id", "name", "source_file"])
    for c in range(1, 4):
        ws.cell(row=1, column=c).fill = HEADER_FILL
        ws.cell(row=1, column=c).font = HEADER_FONT

    for r in rows:
        ws.append(r)

    _autosize(ws)
