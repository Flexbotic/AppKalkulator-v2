from Workcell._workcell_definitions import Workcell, ParamNumber, ParamTablePick

# helper - listowanie wszystkich gniazd
def list_workcells(workcells: dict[int, Workcell]) -> list[dict]:
    """
    Zwraca listę gniazd (workcells) w prostym formacie.
    """
    out = []
    for wc in workcells.values():
        out.append(
            {
                "id": wc.id,
                "name": wc.name,
                "description": getattr(wc, "description", ""),
            }
        )

    out.sort(key=lambda x: x["name"].lower())
    return out


# helper - listowanie parametrów dla gniazda
def list_parameters(workcells: dict[int, Workcell], workcell_id: int) -> dict:
    """
    Zwraca parametry gniazda (parametry "user" i "cost_table").
    """
    if workcell_id not in workcells:
        raise KeyError(f"Workcell id={workcell_id} not found")

    wc = workcells[workcell_id]

    user_numbers = {}
    cost_numbers = {}
    cost_tables = {}

    for formula in wc.formulas:
        for p in formula.params:
            if isinstance(p, ParamNumber):
                entry = {
                    "key": p.key,
                    "label": p.label,
                    "unit": getattr(p, "unit", ""),
                    "source": p.source,
                }
                if p.source == "user":
                    user_numbers[p.key] = entry
                elif p.source == "cost_table":
                    cost_numbers[p.key] = entry

            elif isinstance(p, ParamTablePick) and p.source == "cost_table":
                cost_tables[p.key] = {
                    "key": p.key,
                    "label": p.label,
                    "unit": getattr(p, "unit", ""),
                    "table_name": p.table_name,
                }

    return {
        "user_numbers": list(user_numbers.values()),
        "cost_numbers": list(cost_numbers.values()),
        "cost_tables": list(cost_tables.values()),
    }
