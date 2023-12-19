from bgpy.caida_collector import CustomerProviderLink as CPLink


from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


as_graph_info_043 = ASGraphInfo(
    peer_links=set([]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=10),
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=7, customer_asn=2),
            CPLink(provider_asn=6, customer_asn=7),
            CPLink(provider_asn=6, customer_asn=8),
            CPLink(provider_asn=8, customer_asn=9),
            CPLink(provider_asn=3, customer_asn=7),
            CPLink(provider_asn=3, customer_asn=5),
        ]
    ),
)