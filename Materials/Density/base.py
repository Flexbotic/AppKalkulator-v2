from Materials.Density.define import Density

MATERIAL_DENSITY = {
    Density.STEEL: {
        "S235",
        "S355",
        "DC01",
        "E235 SZEW NA WĄSKIEJ",
        "S235 B/SZW",
        "E235 B/SZW",
        "E355 B/SZW",
        "DD11/S235 TRAWIONA OLIWIONA",
        "S420MC",
        "S235 OCYNK",
    },
    Density.STAINLESS: {
        "1.4404",
        "1.4301",
        "1.4307 / 304L",
    },
    Density.ALUMINIUM: {
        "ALU 5754",
        "ALU 6060",
    }
}

def get_density(gatunek: str) -> float:
    for density, names in MATERIAL_DENSITY.items():
        if gatunek in names:
            return density
    raise ValueError(f"Nieznana gęstość dla materiału: {gatunek}")
