from collections import defaultdict

from lib_caida_collector import AS

from .ann_containers import LocalRib
from .ann_containers import RibsIn, RibsOut
from .ann_containers import SendQueue, RecvQueue
from ..enums import Relationships
from ..announcement import Announcement as Ann
from .bgp_policy import BGPPolicy


class BGPRIBSPolicy(BGPPolicy):
    __slots__ = ["ribs_in", "ribs_out", "recv_q", "send_q", "local_rib"]

    def __init__(self, *args, **kwargs):
        self.local_rib = LocalRib()
        # Ribs in contains unprocessed anns, unchanged from previous AS
        self.ribs_in = RibsIn()
        self.ribs_out = RibsOut()
        self.recv_q = RecvQueue()
        self.send_q = SendQueue()

    def _propagate(policy_self, self, propagate_to: Relationships, send_rels: list):
        """Propogates announcements to other ASes

        send_rels is the relationships that are acceptable to send
        """
        # _policy_propagate and _add_ann_to_q have been overriden
        # So that instead of propagating, announcements end up in the send_q
        # Send q contains both announcements and withdrawals
        policy_self._populate_send_q(self, propagate_to, send_rels)

        # Send announcements/withdrawals and add to ribs out
        policy_self._send_anns(self, propagate_to)

    def _populate_send_q(policy_self, self, propagate_to, send_rels):
        return super(BGPRIBSPolicy, policy_self)._propagate(self, propagate_to, send_rels)

    def _policy_propagate(policy_self, self, propagate_to, send_rels, ann, as_obj):
        """Don't send what we've already sent"""

        ribs_out_ann = policy_self.ribs_out[as_obj.asn].get(ann.prefix)
        return ann.prefix_path_attributes_eq(ribs_out_ann)

    def _add_ann_to_q(policy_self, self, as_obj, ann, propagate_to, send_rels):
        policy_self.send_q.add_ann(as_obj.asn, ann)

    def _send_anns(policy_self, self, propagate_to: Relationships):
        """Sends announcements and populates ribs out"""

        neighbor_prefix_anns = policy_self.send_q.neighbor_prefix_anns(neighbors=getattr(self, propagate_to.name.lower()))

        for (neighbor_obj, prefix, ann) in neighbor_prefix_anns:
            neighbor_obj.policy.recv_q.add_ann(ann, prefix=prefix)
            # Update Ribs out if it's not a withdraw
            if not ann.withdraw:
               policy_self.ribs_out[neighbor_obj.asn][prefix] = ann
            policy_self.send_q.reset_neighbor(neighbor_obj.asn)

    def process_incoming_anns(policy_self,
                              self,
                              recv_relationship: Relationships,
                              *args,
                              propagation_round=None,
                              # Usually None for attack
                              attack=None,
                              reset_q=True,
                              **kwargs):
        """Process all announcements that were incoming from a specific rel"""

        for prefix, ann_list in policy_self.recv_q.prefix_anns():

            # Get announcement currently in local rib
            local_rib_ann = policy_self.local_rib.get_ann(prefix)
            best_ann = local_rib_ann

            # Announcement will never be overriden, so continue
            if best_ann is not None and best_ann.seed_asn is not None:
                continue

            # For each announcement that is incoming
            for ann in ann_list:
                if ann.withdraw:
                    policy_self._process_incoming_withdrawal(self, ann, ann.as_path[0], ann.prefix, recv_relationship)

                else:
                    # BGP Loop Prevention Check
                    if self.asn in ann.as_path:
                        continue

                    policy_self.ribs_in[ann.as_path[0]][prefix] = (ann, recv_relationship)

                    new_ann_is_better = policy_self._new_ann_is_better(self, best_ann, ann, recv_relationship)
                    # If the new priority is higher
                    if new_ann_is_better:
                        if best_ann is not None:
                            withdraw_ann = policy_self._deep_copy_ann(self,
                                                                      ann,
                                                                      recv_relationship,
                                                                      withdraw=True)

                            policy_self._withdraw_ann_from_neighbors(self, withdraw_ann)
                        best_ann = policy_self._deep_copy_ann(self, ann, recv_relationship)
                        # Save to local rib
                        policy_self.local_rib.add_ann(best_ann, prefix=prefix)

        policy_self._reset_q(reset_q)

    def _process_incoming_withdrawal(policy_self, self, ann, neighbor, prefix,
                                     recv_relationship):

        # Return if the current ann was seeded (for an attack)
        local_rib_ann = policy_self.local_rib.get_ann(prefix)
        if (local_rib_ann is not None and
            ann.prefix_path_attributes_eq(local_rib_ann) and
            local_rib_ann.seed_asn is not None):
            return

        current_ann_ribs_in, _ = policy_self.ribs_in[neighbor][prefix]
        assert ann.prefix_path_attributes_eq(current_ann_ribs_in)
        
        # Remove ann from Ribs in
        del policy_self.ribs_in[neighbor][prefix]

        # Remove ann from local rib
        withdraw_ann = policy_self._deep_copy_ann(self, ann, recv_relationship, withdraw=True)
        if withdraw_ann.prefix_path_attributes_eq(policy_self.local_rib.get_ann(prefix)):
            policy_self.local_rib.remove_ann(prefix)

            # Also remove from neighbors
            policy_self._withdraw_ann_from_neighbors(self, withdraw_ann)

        best_ann = policy_self._select_best_ribs_in(self, prefix)
        
        # Put new ann in local rib
        if best_ann is not None:
            policy_self.local_rib.add_ann(best_ann, prefix=prefix)

    def _withdraw_ann_from_neighbors(policy_self, self, withdraw_ann):
        """Withdraw a route from all neighbors.

        This function will not remove an announcement from the local rib, that
        should be done before calling this function.

        Note that withdraw_ann is a deep copied ann
        """

        assert withdraw_ann.withdraw is True
        # Check ribs_out to see where the withdrawn ann was sent
        for send_neighbor, inner_dict in policy_self.ribs_out.items():
            # If the two announcements are equal
            if withdraw_ann.prefix_path_attributes_eq(inner_dict.get(withdraw_ann.prefix)):
                # Delete ann from ribs out
                del policy_self.ribs_out[send_neighbor][withdraw_ann.prefix]

        # Adds withdrawal, or cancels out if we are withdrawing an ann we haven't sent
        for neighbor_obj in self.peers + self.customers + self.providers:
            policy_self.send_q.add_ann(neighbor_obj.asn, withdraw_ann)
            
    def _select_best_ribs_in(policy_self, self, prefix):
        """Selects best ann from ribs in. Remember, ribs in anns are NOT deep copied"""

        ann_list = []
        for neighbor, inner_dict in policy_self.ribs_in.items():
            if prefix in inner_dict:
                ann_list.append(inner_dict[prefix])

        if len(ann_list) == 0:
            return None
        else:
            # Get the best announcement
            best_ann = None
            for ann, recv_relationship in ann_list:
                if policy_self._new_ann_is_better(self, best_ann, ann, recv_relationship):
                    best_ann = policy_self._deep_copy_ann(self, ann, recv_relationship)

            return best_ann
