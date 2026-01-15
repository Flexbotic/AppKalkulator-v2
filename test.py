from Materials.load import load_materials
from Workcell._load_costs import load_workcells_with_costs
from Workcell._workcell_helpers import list_parameters, list_workcells
from Runtime.helpers import create_quote_material, create_quote_workcell, compute_quote_workcell


materialy = load_materials("Materialy.xlsx")
# print(materialy)

material = materialy[2]
# print(material)

qm = create_quote_material(
    quote_item_id=1,
    material=material,
    length_mm=6000,
    qty=1,
)
# print(qm)

workcells, costs = load_workcells_with_costs()

workcells, costs = load_workcells_with_costs()

# Listowanie gniazd i parametrów

workcell_list = list_workcells(workcells)
parameters = list_parameters(workcells, 9)

selected_workcell_id = 9
selected_choice = None
selected_formula = "by_dm2"
user_values = {"dm2": 10, "cena_dm2": 20.5}
table_picks = {"cena_dm2": "ZWYKLA"}

# Wybierz dane do testu
selected_workcell_id = 9  # Przykładowe ID gniazda
selected_choice = None  # Brak wyboru - "DEFAULT"
selected_formula = "by_dm2"  # ID formuły (np. "wycena wg powierzchni")
user_values = {
    "dm2": 10,  # Powierzchnia w m²
    "cena_dm2": 20.5,  # Cena za m²
}
table_picks = {
    "cena_dm2": "FARBA_PROSZKOWA",  # Wybór rodzaju farby
}

# Stwórz QuoteWorkcell
quote = create_quote_workcell(
    workcells, costs, selected_workcell_id, selected_choice, selected_formula, user_values, table_picks
)

# Oblicz koszt na podstawie QuoteWorkcell
result = compute_quote_workcell(quote, workcells[selected_workcell_id])

print(f"Obliczony koszt: {result}")