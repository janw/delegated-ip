import re
from ipaddress import IPv6Address
from itertools import chain
from socket import AddressFamily

import psutil

non_word = re.compile(r"[\W_]")

try:
    MAC_ADDR_FAMILY = AddressFamily.AF_PACKET
except AttributeError:
    MAC_ADDR_FAMILY = AddressFamily.AF_LINK


def make_eui64(mac_addr: str) -> str:
    stripped = mac_addr.replace(":", "")
    first_byte = hex(int(stripped[:2], 16) ^ (1 << 1))[2:]
    return first_byte + stripped[2:6] + "fffe" + stripped[6:]


def get_addresses(interface: str | None) -> list[tuple[AddressFamily, str]]:
    _interfaces = psutil.net_if_addrs()
    addresses = (
        _interfaces.get(interface, [])
        if interface
        else chain.from_iterable(_interfaces.values())
    )
    return [(addr.family, addr.address) for addr in addresses]


def get_eui_addr(interface: str) -> str:
    addresses = get_addresses(interface)
    print(addresses)
    for family, addr in addresses:
        if family == MAC_ADDR_FAMILY:
            iface_id = make_eui64(addr)
            break
    else:
        raise ValueError("MAC address not found")

    for family, addr in addresses:
        if family != AddressFamily.AF_INET6:
            continue

        if not (v6addr := IPv6Address(addr)).is_global:
            continue

        if format(v6addr, "x").endswith(iface_id):
            return str(v6addr)
    else:
        raise ValueError("No matching global EUI64 address found")


def get_token_addr(token: str, interface: str | None = None) -> str:
    if "::" in token:
        raise ValueError("Token cannot contain '::'")
    exploded_token = "".join("%04x" % int(v, 16) for v in token.split(":") if v)
    addresses = get_addresses(interface)
    for family, addr in addresses:
        if family != AddressFamily.AF_INET6:
            continue

        if not (v6addr := IPv6Address(addr)).is_global:
            continue

        if format(v6addr, "x").endswith(exploded_token):
            return str(v6addr)

    raise ValueError("No matching global address found")
