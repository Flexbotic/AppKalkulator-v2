from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from Workcell._workcell_definitions import Workcell, ParamChoice, ParamNumber, ParamTablePick

WORKCELL_DIR = Path(__file__).parent
PROJECT_ROOT = WORKCELL_DIR.parent


@dataclass
class CostData:
    # workcell_id -> choice_value -> param_key -> value
    numbers: dict[int, dict[str, dict[str, float]]]
    # workcell_id -> choice_value -> table_name -> item_key -> value
    tables: dict[int, dict[str, dict[str, dict[str, float]]]]


def _import_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _find_workcells(mod: Any) -> list[Workcell]:
    return [v for v in vars(mod).values() if isinstance(v, Workcell)]


def load_workcell_definitions() -> dict[int, Workcell]:
    """
    Skanuje Workcell/*.py (bez tych od '_') i zwraca mapę: workcell_id -> Workcell
    """
    out: dict[int, Workcell] = {}
    for py in WORKCELL_DIR.glob("*.py"):
        if py.name.startswith("_"):
            continue
        mod = _import_module(py)
        for wc in _find_workcells(mod):
            if wc.id in out:
                raise ValueError(f"Duplicate workcell id={wc.id} ({wc.name}) in {py.name}")
            out[wc.id] = wc
    return out


def _to_float(v: Any) -> float:
    if v is None or (isinstance(v, str) and not v.strip()):
        raise ValueError("Empty cost value")
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        # PL: przecinek dziesiętny
        return float(v.strip().replace(" ", "").replace(",", "."))
    raise ValueError(f"Unsupported value type: {type(v)} ({v!r})")


def load_costs_from_excel(xlsx_path: Path, workcells: dict[int, Workcell]) -> CostData:
    """
    Czyta Koszty_template.xlsx wygenerowany Twoim generatorem.
    Zwraca koszty w strukturze numbers/tables.
    """
    wb = load_workbook(xlsx_path, data_only=True)

    numbers: dict[int, dict[str, dict[str, float]]] = {}
    tables: dict[int, dict[str, dict[str, dict[str, float]]]] = {}

    # Map: sheet "WC__{name}" -> workcell_id
    # Najpewniej po nazwie w INDEX (id + name), a nie po samej nazwie arkusza.
    if "INDEX" not in wb.sheetnames:
        raise ValueError("Excel missing INDEX sheet")

    index_ws = wb["INDEX"]
    # header: workcell_id, name, source_file
    name_to_id: dict[str, int] = {}
    for row in index_ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        wc_id = int(row[0])
        wc_name = str(row[1])
        name_to_id[wc_name] = wc_id

    for sheet_name in wb.sheetnames:
        if not sheet_name.startswith("WC__"):
            continue
        ws = wb[sheet_name]
        wc_name = sheet_name.replace("WC__", "", 1)
        if wc_name not in name_to_id:
            # jeśli ktoś zmieni nazwę arkusza ręcznie, wolę fail fast
            raise ValueError(f"Sheet {sheet_name} not found in INDEX (workcell name mismatch)")
        wc_id = name_to_id[wc_name]

        if wc_id not in workcells:
            raise ValueError(f"Workcell id={wc_id} from INDEX not found in definitions")

        wc_def = workcells[wc_id]
        choice_params = [p for p in wc_def.params if isinstance(p, ParamChoice)]
        if len(choice_params) > 1:
            raise ValueError(f"Workcell '{wc_def.name}' has >1 choice (unsupported by simple loader)")

        if len(choice_params) == 1:
            choice_key = choice_params[0].key
            choice_values = list(choice_params[0].options or [])
        else:
            choice_key = "DEFAULT"
            choice_values = ["DEFAULT"]

        needed_numbers = [
            p for p in wc_def.params if isinstance(p, ParamNumber) and p.source == "cost_table"
        ]
        needed_tables = [
            p for p in wc_def.params if isinstance(p, ParamTablePick) and p.source == "cost_table"
        ]

        numbers.setdefault(wc_id, {})
        tables.setdefault(wc_id, {})

        # Parser arkusza: idziemy wierszami i łapiemy sekcje:
        # - linia z "choice_key = value"
        # - nagłówek tabelki numbers
        # - wiersze numbers aż do pustego / czegoś innego
        # - potem TABLE: X + nagłówek + wiersze itemów
        current_choice: str | None = None
        i = 1
        max_row = ws.max_row

        def cell(r: int, c: int) -> Any:
            return ws.cell(row=r, column=c).value

        while i <= max_row:
            a = cell(i, 1)
            if isinstance(a, str) and a.strip().startswith(f"{choice_key} ="):
                # np. "typ_ocynku = OGNIOWY"
                current_choice = a.split("=", 1)[1].strip()
                if current_choice not in choice_values:
                    # może ktoś zmienił w excelu
                    raise ValueError(f"{sheet_name}: unknown choice '{current_choice}' (expected {choice_values})")

                numbers[wc_id].setdefault(current_choice, {})
                tables[wc_id].setdefault(current_choice, {})
                i += 1
                continue

            # NUMBERS header row: ["param_key","label","unit","value"]
            if current_choice is not None and str(a).strip() == "param_key" and str(cell(i, 4)).strip() == "value":
                i += 1
                # wiersze numbers
                seen_keys = set()
                while i <= max_row:
                    pk = cell(i, 1)
                    val = cell(i, 4)
                    if pk is None:
                        break
                    pk_s = str(pk).strip()
                    if pk_s.startswith("TABLE:"):
                        break
                    # tylko te, które są w definicji (żeby nie połknąć śmieci)
                    if pk_s in {p.key for p in needed_numbers}:
                        if val is None or (isinstance(val, str) and not val.strip()):
                            raise ValueError(f"{sheet_name} ({current_choice}): missing value for {pk_s}")
                        numbers[wc_id][current_choice][pk_s] = _to_float(val)
                        seen_keys.add(pk_s)
                    i += 1

                # walidacja: czy wszystkie koszty są wpisane
                missing = [p.key for p in needed_numbers if p.key not in numbers[wc_id][current_choice]]
                if missing:
                    raise ValueError(f"{sheet_name} ({current_choice}): missing cost values for: {missing}")
                continue

            # TABLE section
            if current_choice is not None and isinstance(a, str) and a.strip().startswith("TABLE:"):
                table_name = a.split(":", 1)[1].strip()
                if table_name not in {t.table_name for t in needed_tables}:
                    # ignoruj nieznane (lub fail fast - jak wolisz)
                    # ja wolę fail fast, bo to literówka w excelu:
                    raise ValueError(f"{sheet_name} ({current_choice}): unknown table '{table_name}'")
                tables[wc_id][current_choice].setdefault(table_name, {})

                # następny wiersz to header item_key/value itd.
                i += 1
                # spodziewamy się nagłówka: item_key ... value
                if str(cell(i, 1)).strip() != "item_key" or str(cell(i, 4)).strip() != "value":
                    raise ValueError(f"{sheet_name} ({current_choice}) TABLE {table_name}: bad header row")
                i += 1

                # czytamy aż do pustego item_key
                while i <= max_row:
                    item_key = cell(i, 1)
                    val = cell(i, 4)
                    if item_key is None or (isinstance(item_key, str) and not item_key.strip()):
                        break
                    item_key_s = str(item_key).strip()
                    if val is None or (isinstance(val, str) and not val.strip()):
                        raise ValueError(f"{sheet_name} ({current_choice}) TABLE {table_name}: missing value for {item_key_s}")
                    tables[wc_id][current_choice][table_name][item_key_s] = _to_float(val)
                    i += 1

                continue

            i += 1

    return CostData(numbers=numbers, tables=tables)


def load_workcells_with_costs():
    workcells = load_workcell_definitions()
    xlsx_path = PROJECT_ROOT / "Koszty_template.xlsx"

    if not xlsx_path.exists():
        raise FileNotFoundError(
            f"Brak pliku kosztów: {xlsx_path}\n"
            f"Najpierw wygeneruj template (_generate_cost_template.py)."
        )

    costs = load_costs_from_excel(xlsx_path, workcells)
    return workcells, costs

