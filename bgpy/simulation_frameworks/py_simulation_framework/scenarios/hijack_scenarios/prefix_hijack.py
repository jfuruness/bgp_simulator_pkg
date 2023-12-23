from typing import TYPE_CHECKING, Union

from bgpy.simulation_frameworks.py_simulation_framework.scenarios.scenario import (
    Scenario,
)
from bgpy.enums import Prefixes
from bgpy.enums import CPPRelationships
from bgpy.enums import Timestamps


if TYPE_CHECKING:
    from bgpy.simulation_engines.cpp_simulation_engine import CPPAnnouncement as CPPAnn
    from bgpy.simulation_engines.py_simulation_engine import PyAnnouncement as PyAnn


class PrefixHijack(Scenario):
    """Prefix hijack where both attacker and victim compete for a prefix"""

    def _get_announcements(
        self, *args, **kwargs
    ) -> tuple[Union["CPPAnn", "PyAnn"], ...]:
        """Returns the two announcements seeded for this engine input

        This engine input is for a prefix hijack,
        consisting of a valid prefix and invalid prefix

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                    seed_asn=victim_asn,
                    roa_valid_length=True,
                    roa_origin=victim_asn,
                    recv_relationship=CPPRelationships.ORIGIN,
                )
            )

        err: str = "Fix the roa_origins of the " "announcements for multiple victims"
        assert len(self.victim_asns) == 1, err

        roa_origin: int = next(iter(self.victim_asns))

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=True,
                    roa_origin=roa_origin,
                    recv_relationship=CPPRelationships.ORIGIN,
                )
            )

        return tuple(anns)