import pandas as pd

from Materials.material import Material
from Materials.Density.base import get_density
from Materials.Type.base import price_mb_to_kg

EXCEL_PATH = "Materialy.xlsx"

def norm_upper(s: str) -> str:
    return s.strip().upper()

def load_materials(filename: str) -> list[Material]:
    df = pd.read_excel(filename)
    material_library : list[Material] = []

    for index, row in df.iterrows():
        typ = norm_upper(row["Typ"])
        gatunek =  norm_upper(row["Gatunek"])
        rozmiar = row["Rozmiar"]
        cena_mb = float(row["Cena/mb"])
        cena_kg = float(row["Cena/kg"])
        data_aktualizacji = row["Data ostatniej aktualizacji"]
        dostawca = row["Dostawca"].strip()
        gestosc = get_density(gatunek)
        if cena_kg == 0:
            cena_kg = price_mb_to_kg(typ, rozmiar, gestosc, cena_mb)
            
        material_library.append(Material(index, typ, gatunek, rozmiar, cena_kg, cena_mb, data_aktualizacji, dostawca, gestosc))
    
    return material_library
