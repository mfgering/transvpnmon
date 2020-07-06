import re

stuff = """
tun224: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun225: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun226: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun227: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun228: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun229: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun230: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun231: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun232: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun233: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun234: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun235: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
        options=80000<LINKSTATE>
        nd6 options=1<PERFORMNUD>
        groups: tun
tun236: flags=8010<POINTOPOINT,MULTICAST> metric 0 mtu 1500
"""

x = [t[1] for t in re.finditer(r'(tun\d+):', stuff)]
for t in re.finditer(r'(tun\d+):', stuff):
    x = t
tuns = re.findall(r'tun\d+:', stuff)

print(stuff)