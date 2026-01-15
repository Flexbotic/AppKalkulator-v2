import math

def _to_float(x: str) -> float:
    return float(x.strip().replace(",", "."))

def _split_dims(dim_str: str) -> list[float]:
    parts = dim_str.lower().replace(" ", "").split("x")
    return [_to_float(p) for p in parts if p != ""]

def _kg_per_m_from_area_mm2(area_mm2: float, density_kg_m3: float) -> float:
    return area_mm2 * 1e-6 * density_kg_m3

def _profil_area_mm2(b_mm: float, h_mm: float, t_mm: float) -> float:
    if b_mm <= 0 or h_mm <= 0 or t_mm <= 0:
        raise ValueError("PROFIL: wymiary muszą być dodatnie.")
    if 2 * t_mm >= b_mm or 2 * t_mm >= h_mm:
        raise ValueError("PROFIL: musi być 2*t < szer i 2*t < wys.")
    return b_mm * h_mm - (b_mm - 2 * t_mm) * (h_mm - 2 * t_mm)

def _rura_area_mm2(d_mm: float, t_mm: float) -> float:
    if d_mm <= 0 or t_mm <= 0:
        raise ValueError("RURA: wymiary muszą być dodatnie.")
    if 2 * t_mm >= d_mm:
        raise ValueError("RURA: musi być 2*t < średnica.")
    return (math.pi / 4.0) * (d_mm**2 - (d_mm - 2 * t_mm) ** 2)

def price_mb_to_kg(material_type: str, dim: str, density: float, price_mb: float) -> float:
    material_type = material_type.strip().upper()

    if density <= 0:
        raise ValueError("Gęstość musi być dodatnia.")
    if price_mb < 0:
        raise ValueError("price_mb nie może być ujemne.")

    dims = _split_dims(dim)

    if material_type == "PROFIL":
        if len(dims) != 3:
            raise ValueError('PROFIL oczekuje formatu "szerxwysxgr", np. "40x20x2".')
        szer, wys, gr = dims
        area_mm2 = _profil_area_mm2(szer, wys, gr)
        kg_per_m = _kg_per_m_from_area_mm2(area_mm2, density)
        price_kg = price_mb / kg_per_m if kg_per_m > 0 else 0.0
        return round(price_kg, 2)

    elif material_type == "RURA":
        if len(dims) != 2:
            raise ValueError('RURA oczekuje formatu "srxgr", np. "33.7x2".')
        sr, gr = dims
        area_mm2 = _rura_area_mm2(sr, gr)
        kg_per_m = _kg_per_m_from_area_mm2(area_mm2, density)
        price_kg = price_mb / kg_per_m if kg_per_m > 0 else 0.0
        return round(price_kg, 2)

    else:
        raise ValueError(f"Nieobsługiwany typ materiału: {material_type}")
