from Workcell._workcell_definitions import (Workcell, ParamChoice, ParamNumber, Formula, Rule)

OCYNK = Workcell(
  id=11,
  name="Ocynk",
  description="...",
  global_params=[
    ParamChoice(key="typ_ocynku", label="Typ ocynku", source="user",
               options=["OGNIOWY", "GALWANICZNY"])
  ],
  formulas=[
    Formula(
      id="by_kg",
      label="Wycena (ogniowy) wg masy",
      expr="kg * cena_kg",
      params=[
        ParamNumber(key="kg", label="Masa [kg]", source="user", unit="kg", material_value="masa", min_value=0),
        ParamNumber(key="cena_kg", label="Cena [zł/kg]", source="cost_table", unit="zł/kg", min_value=0),
      ],
      enabled_when=[Rule("typ_ocynku", "OGNIOWY")],
      is_default_when=[Rule("typ_ocynku", "OGNIOWY")],
    ),
    Formula(
      id="by_dm2",
      label="Wycena (galwaniczny) wg powierzchni",
      expr="dm2 * cena_dm2",
      params=[
        ParamNumber(key="dm2", label="Powierzchnia [dm²]", source="user", unit="dm2", material_value="powierzchnia", min_value=0),
        ParamNumber(key="cena_dm2", label="Cena [zł/dm²]", source="cost_table", unit="zł/dm2", min_value=0),
      ],
      enabled_when=[Rule("typ_ocynku", "GALWANICZNY")],
      is_default_when=[Rule("typ_ocynku", "GALWANICZNY")],
    )
  ]
)

