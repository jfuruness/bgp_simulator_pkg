from typing import Optional, TYPE_CHECKING

from bgpy.simulation_engine.policies.custom_attackers.first_asn_stripping_aspa_attacker import (  # noqa
    FirstASNStrippingASPAAttacker,
)
from bgpy.simulation_framework.scenarios.custom_scenarios.victims_prefix import (
    VictimsPrefix,
)
from .shortest_path_hijack import ShortestPathHijack

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann, BaseSimulationEngine


class FirstASNStrippingHijack(ShortestPathHijack):
    """An extension of the shortest path hijack that strips the first ASN"""

    RequiredASPAAttackerCls = FirstASNStrippingASPAAttacker

    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns the two announcements seeded for this engine input

        This engine input is for a prefix hijack,
        consisting of a valid prefix and invalid prefix with path manipulation
        """

        # First get the victims prefix
        victim_anns = VictimsPrefix._get_announcements(self, engine=engine)
        attacker_anns = self._get_first_asn_stripped_attacker_anns(engine=engine)
        return victim_anns + attacker_anns

    def _get_first_asn_stripped_attacker_anns(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        attacker_anns = self._get_shortest_path_attacker_anns()
        stripped_anns: list["Ann"] = list()
        for ann in attacker_anns:
            # Remove the attacker's ASN
            if len(ann.as_path) > 1:
                stripped_ann = ann.copy({"as_path": ann.as_path[1:]})
            # Can't remove the first asn in a path length of 1
            else:
                stripped_ann = ann
            stripped_anns.append(stripped_ann)
        return tuple(stripped_anns)
