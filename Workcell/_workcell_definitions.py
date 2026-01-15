from dataclasses import dataclass
from typing import Literal, Optional

@dataclass
class Workcell:
    id: int
    name: str
    description: str
    global_params: list["ParamDef"]
    formulas: list["Formula"]

@dataclass
class ParamDef:
    key: str
    label: str
    source: Literal["user", "cost_table"]
    required: bool = True

@dataclass
class ParamNumber(ParamDef):
    unit: str = ""
    material_value: Literal["none", "masa", "powierzchnia"] = "none"
    min_value: float | None = None

@dataclass
class ParamChoice(ParamDef):
    options: list[str] = None 

@dataclass
class ParamTablePick(ParamDef):
    table_name: str = ""

@dataclass
class Formula:
    id: str
    label: str
    expr: str
    params: list["ParamDef"]
    enabled_when: list["Rule"]
    is_default_when: list["Rule"]

@dataclass
class Rule:
    param_key: str
    equals: str
