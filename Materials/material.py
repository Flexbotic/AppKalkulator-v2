from dataclasses import dataclass

@dataclass
class Material:
    id: int
    typ: str
    gatunek: str
    rozmiar: str
    cena_kg: float
    cena_mb: float
    data_aktualizacji: str
    dostawca: str
    gestosc: float
    