from Workcell._workcell_definitions import (Workcell, ParamTablePick, ParamNumber, Formula, Rule)

MALOWANIE = Workcell(
  id=9,
  name="Malowanie",
  description="...",
  choice_param=None,
  formulas=[
    Formula(
      id="by_dm2",
      label="Wycena wg powierzchni",
      expr="dm2 * cena_dm2",
      params=[
        ParamNumber(key="dm2", label="Powierzchnia", source="user", unit="dm2", material_value="powierzchnia", min_value=0),
        ParamTablePick(key="cena_dm2", label="Cena", source="cost_table", unit="zł/dm2", table_name="Rodzaje farby"),
      ],
      enabled_when=[],
      is_default_when=[],
    ),
  ]
)

