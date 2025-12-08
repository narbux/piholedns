#!/usr/bin/env python3
"""Copyright (C) 2025 Marnix Enthoven <mail@marnixenthoven.nl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

---

This script is used to add CNAME entries to a pihole for DNS resolution. It can
be used in a internal homelab to add new services to the DNS. Set the environment
variables `PIHOLEDNS_API_URL` and `PIHOLEDNS_PASSWORD`.
"""

__version__ = "0.1.0"

import argparse
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

PIHOLEDNS_API_URL = os.environ.get("PIHOLEDNS_API_URL", None)
PIHOLEDNS_PASSWORD = os.environ.get("PIHOLEDNS_PASSWORD", None)


def authenticate(password: str) -> str:
    """Authenticates the script

    :param password: password of pihole install
    :returns: str with session ID"""
    with httpx.Client() as client:
        result = client.post(
            f"{PIHOLEDNS_API_URL}/auth", json={"password": password}
        )
        result.raise_for_status()
        return result.json()["session"]["sid"]


def logout(session: httpx.Client) -> None:
    """Invalidates the authenticated session ID. Calling this function is
    not necessary as the session ID has a limited time validity. But nice
    for cleanup."""
    result = session.delete(f"{PIHOLEDNS_API_URL}/auth")
    result.raise_for_status()


def get_cname_records(session: httpx.Client) -> list[str]:
    """Retrieve all registered CNAME records in pihole.

    :param session: authenticated httpx.Client object

    :returns: A list of CNAMEs that are formatted as '$domain,$target'.
    E.g.: `pihole.intranet.domain.com,proxy.internal.domain.com`"""
    result = session.get(f"{PIHOLEDNS_API_URL}/config")
    result.raise_for_status()
    return result.json()["config"]["dns"]["cnameRecords"]


# TODO: Decide if to include this function
# def get_hosts(session: httpx.Client) -> list[str]:
#     """Retrieve all registered dns hosts in pihole.

#     :param session: authenticated httpx.Client object

#     :returns: A list of strings that are formatted as '$ipaddress $domain'.
#     E.g.: `192.168.1.45 server.internal.domain.com`"""
#     result = session.get(f"{API_URL}/config")
#     result.raise_for_status()
#     return result.json()["config"]["dns"]["hosts"]


def add_cname(domain: str, target: str, session: httpx.Client) -> None:
    """Function to add CNAME to pihole. This first retrieves the config from
    pihole and adds the new CNAME to that list. Than it re-uploads the config
    to pihole.

    :param domain: new domain to add as CNAME to pihole
    :param target: target domain where CNAME record should point to
    :param session: authenticated httpx.Client object
    """
    cname_list = get_cname_records(session)
    new_cname = f"{domain},{target}"
    cname_list.append(new_cname)
    payload = {"config": {"dns": {"cnameRecords": cname_list}}}
    result = session.patch(f"{PIHOLEDNS_API_URL}/config", json=payload)
    result.raise_for_status()


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="piholedns",
        description="""\
This script is used to add CNAME entries to a pihole for DNS resolution. It can
be used in a internal homelab to add new services to the DNS. Set the environment
variables `PIHOLEDNS_API_URL` and `PIHOLEDNS_PASSWORD`.""",
    )
    parser.add_argument("domain", help="new domain to add as CNAME to pihole")
    parser.add_argument(
        "target", help="target domain where CNAME record should point to"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser.parse_args()


def main():
    args = get_arguments()

    if not PIHOLEDNS_API_URL or not PIHOLEDNS_PASSWORD:
        raise ValueError(
            "Could not read PIHOLEDNS_API_URL or PIHOLEDNS_PASSWORD from environment"
        )

    sid = authenticate(PIHOLEDNS_PASSWORD)

    with httpx.Client(headers={"X-FTL-SID": sid}) as session:
        add_cname(domain=args.domain, target=args.target, session=session)
        logout(session)


if __name__ == "__main__":
    main()
