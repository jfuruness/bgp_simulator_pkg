from typing import TYPE_CHECKING

from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann


class ROV(BGP):
    """An Policy that deploys ROV"""

    name: str = "ROV"

    def _valid_ann(self, ann: "Ann", recv_rel: "Relationships") -> bool:
        """Returns announcement validity

        Returns false if invalid by roa,
        otherwise uses standard BGP (such as no loops, etc)
        to determine validity
        """

        # Invalid by ROA is not valid by ROV
        if ann.invalid_by_roa:
            return False
        # Use standard BGP to determine if the announcement is valid
        else:
            rv = super(ROV, self)._valid_ann(ann=ann, recv_rel=recv_rel)
            assert isinstance(rv, bool), "for mypy"
            return rv
