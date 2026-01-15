from dataclasses import dataclass

@dataclass
class QuoteMaterial:
    quote_item_id: int
    material_id: int
    length_mm: float | None
    weight_kg: float | None
    powierzchnia: float
    masa: float
    qty: int = 1

@dataclass
class QuoteWorkcell:
    workcell_id: int
    chosen_formula_id: str
    values: dict[str, object]
    material_refs: list[int]