from frozendict import frozendict
from bgpy.tests.engine_tests.graphs import graph_019
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import ROVSimpleAS
from bgpy.enums import ASNs
from bgpy.simulation_framework import ScenarioConfig, ValidPrefix


config_025 = EngineTestConfig(
    name="025",
    desc="Test of tiebreak preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=ROVSimpleAS,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    graph=graph_019,
)