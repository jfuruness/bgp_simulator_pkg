from frozendict import frozendict

from bgpy.enums import ASNs
from bgpy.simulation_engine import ASPA, BGP, ShortestPathPrefixASPAAttacker
from bgpy.simulation_framework import ScenarioConfig, ShortestPathPrefixHijack
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = (
    "shortest path export all against ASPASimple from a customer\n"
    "AS 5 fails to detect the shortest path export all"
)

ex_config_025 = EngineTestConfig(
    name="ex_025_shortest_path_export_all_aspa_simple_customer",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=ShortestPathPrefixHijack,
        AttackerBasePolicyCls=ShortestPathPrefixASPAAttacker,
        BasePolicyCls=BGP,
        AdoptPolicyCls=ASPA,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(
            {
                2: ASPA,
                5: ASPA,
                10: ASPA,
                ASNs.VICTIM.value: ASPA,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
