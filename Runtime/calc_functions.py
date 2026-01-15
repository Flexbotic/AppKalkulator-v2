
import math
from Materials.Type.base import (
    _split_dims,
    _profil_area_mm2,
    _rura_area_mm2,
    _kg_per_m_from_area_mm2,
)

def mb_to_kg(material_type: str, dim: str, density: float, length_m: float) -> float:
    material_type = material_type.strip().upper()

    if density <= 0:
        raise ValueError("Gęstość musi być dodatnia.")
    if length_m < 0:
        raise ValueError("length_m nie może być ujemne.")

    dims = _split_dims(dim)

    if material_type == "PROFIL":
        szer, wys, gr = dims
        area_mm2 = _profil_area_mm2(szer, wys, gr)
        kg_per_m = _kg_per_m_from_area_mm2(area_mm2, density)
        masa = kg_per_m * length_m
        return round(masa, 2)

    elif material_type == "RURA":
        sr, gr = dims
        area_mm2 = _rura_area_mm2(sr, gr)
        kg_per_m = _kg_per_m_from_area_mm2(area_mm2, density)
        masa = kg_per_m * length_m
        return round(masa, 2)

    else:
        raise ValueError(f"Nieobsługiwany typ materiału: {material_type}")
    
def mb_to_dm2(material_type: str, dim: str, length_m: float) -> float:
    material_type = material_type.strip().upper()

    if length_m < 0:
        raise ValueError("length_m nie może być ujemne.")

    dims = _split_dims(dim)

    if material_type == "PROFIL":
        szer, wys, gr = dims
        obwod_mm = 2 * (szer + wys)
        powierzchnia_dm2 = ((obwod_mm / 1000.0) * length_m) * 100
        return round(powierzchnia_dm2, 2)

    elif material_type == "RURA":
        sr = dims[0]
        obwod_mm = math.pi * sr
        powierzchnia_dm2 = ((obwod_mm / 1000.0) * length_m) * 100
        return round(powierzchnia_dm2, 2)

    else:
        raise ValueError(f"Nieobsługiwany typ materiału: {material_type}")
    
def blacha_kg_to_dm2(dim: str, density: float, mass_kg: float) -> float:
    
    dims = _split_dims(dim)
    thickness_mm = dims[2]
    
    if thickness_mm <= 0:
        raise ValueError("Grubość blachy musi być dodatnia.")
    if mass_kg <= 0:
        raise ValueError("Masa musi być dodatnia.")
    if density <= 0:
        raise ValueError("Gęstość musi być dodatnia.")
    
    thickness_m = thickness_mm / 1000
    volume_m3 = mass_kg / density

    powierzchnia_dm2 = (volume_m3 / thickness_m) *  100
    return round(powierzchnia_dm2,2)