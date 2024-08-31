from typing import TYPE_CHECKING

from bgpy.simulation_engine.policies.rov import ROVFull

from .rovpp_v1_lite import ROVPPV1Lite

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ROVPPV1LiteFull(ROVPPV1Lite, ROVFull):  # type: ignore
    """An Policy that deploys ROV++V1 Lite as defined in the ROV++ paper, and
    has withdrawals, ribs in and out

    ROV++ Improved Deployable Defense against BGP Hijacking
    """

    name: str = "ROV++V1 Lite Full"

    def _add_blackholes_to_local_rib(self, blackholes: tuple["Ann", ...]) -> None:
        """Adds all blackholes to the local RIB"""

        for blackhole in blackholes:
            existing_ann = self._local_rib.get(blackhole.prefix)
            # Don't overwrite valid existing announcements
            if existing_ann is None:
                self._local_rib.add_ann(blackhole)
            elif existing_ann.invalid_by_roa:
                # If you need this feature, please email jfuruness@gmail.com
                # Although I think this case would be very rare that no one will
                # ever come across it so I won't bother with implementing it right now
                raise NotImplementedError(
                    "Need to handle withdrawals for this"
                    " if you need this feature, please email jfuruness@gmail.com"
                )
                self._local_rib.add_ann(blackhole)  # type: ignore
