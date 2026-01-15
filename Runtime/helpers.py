from Materials.material import Material
from Workcell._workcell_definitions import Workcell, ParamNumber, ParamTablePick
from Workcell._workcell_helpers import list_parameters
from Runtime.calc_functions import (
    mb_to_kg,
    mb_to_dm2,
    blacha_kg_to_dm2,
)
from Runtime.runtime import QuoteMaterial, QuoteWorkcell

def create_quote_material(quote_item_id: int, material: Material, length_mm: float | None = None, weight_kg: float | None = None, qty: int = 1) -> QuoteMaterial:
    
    if length_mm is None and weight_kg is None:
        raise ValueError("Musisz podać length_mm albo weight_kg.")

    if material.typ in ("PROFIL", "RURA"):
        if length_mm is None:
            raise ValueError("Dla PROFIL/RURA wymagane length_mm.")

        length_m = length_mm / 1000.0

        masa = mb_to_kg(material_type=material.typ, dim=material.rozmiar, density=material.gestosc, length_m=length_m)

        powierzchnia = mb_to_dm2(material_type=material.typ, dim=material.rozmiar, length_m=length_m)

    elif material.typ == "BLACHA":
        if weight_kg is None:
            raise ValueError("Dla BLACHA wymagane weight_kg.")

        masa = weight_kg

        powierzchnia = blacha_kg_to_dm2(dim=material.rozmiar, density=material.gestosc, mass_kg=weight_kg)
    else:
        raise ValueError(f"Nieobsługiwany typ materiału: {material.typ}")

    return QuoteMaterial(quote_item_id=quote_item_id, material_id=material.id, length_mm=length_mm, weight_kg=weight_kg, powierzchnia=round(powierzchnia, 2), masa=round(masa, 2), qty=qty)

def create_quote_workcell(
    workcells: dict[int, Workcell],
    costs: dict[int, dict[str, dict[str, float]]],  # Zakładamy, że costs są taką strukturą
    workcell_id: int,
    choice_value: str,
    formula_id: str,
    user_values: dict[str, object],
    table_picks: dict[str, str] | None = None,
    material_refs: list[int] | None = None,
) -> dict:
    """
    Tworzy obiekt QuoteWorkcell na podstawie wyborów w GUI.
    """
    table_picks = table_picks or {}
    material_refs = material_refs or []

    wc = workcells[workcell_id]
    formula = next(f for f in wc.formulas if f.id == formula_id)

    values = {}

    # Przetwarzamy parametry z formuły
    for param in formula.params:
        if isinstance(param, ParamNumber):
            if param.source == "user":
                values[param.key] = user_values.get(param.key, None)
            elif param.source == "cost_table":
                values[param.key] = costs[workcell_id][choice_value][formula_id].get(param.key, 0)

        elif isinstance(param, ParamTablePick) and param.source == "cost_table":
            picked_item = table_picks.get(param.key)
            if not picked_item:
                raise ValueError(f"Brak wyboru pozycji tabeli dla '{param.key}' ({param.table_name})")
            # Poprawny sposób uzyskania wartości
            v = costs.get_number(workcell_id, choice_value, formula_id, param.key)  # Dla parametrów liczbowych

            # Jeśli to jest parametr tablicowy, używamy get_table_value
            if isinstance(param, ParamTablePick):
                picked_item = table_picks.get(param.key)
                if picked_item:
                    v = costs.get_table_value(workcell_id, choice_value, formula_id, param.key, picked_item)
                else:
                    v = 0  # Brak wyboru w tabeli, domyślnie 0

            values[param.key] = v

    # Zwróć wynik
    return {
        "workcell_id": workcell_id,
        "choice_value": choice_value,
        "chosen_formula_id": formula_id,
        "values": values,
        "table_picks": table_picks,
        "material_refs": material_refs,
    }



def compute_quote_workcell(quote_wc: dict, workcell: Workcell) -> float:
    """
    Oblicza koszt na podstawie wartości w QuoteWorkcell.
    """
    formula = next(f for f in workcell.formulas if f.id == quote_wc['chosen_formula_id'])
    
    # Użyj eval na wartości przypisane w values
    result = eval(formula.expr, {"__builtins__": {}}, quote_wc["values"])
    
    return round(float(result), 2)