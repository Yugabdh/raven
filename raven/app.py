#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        app
# Purpose:     Entry point to application
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import json

from raven.targets.instance import Instance
from raven.web.webreq import WebRequest
from raven.footprinting.passive.whoislookup import Whoislookup
from raven.footprinting.active.traceroute import Traceroute
from raven.footprinting.passive.waybackmachine import WayBackMachine


def run():
    """
    Function which starts chain.
    """

    target = Instance("example.com", True)
    status, reason = target.get_status()
    print(status, reason)
    print(target.get_ip())

    whois_obj = Whoislookup()
    print(whois_obj.whois_query(target.domain))
    print(whois_obj.ip_whois_query(target.ip))

    traceroute = Traceroute(target.ip, no_geoloc=False, country="LO")
    hops = traceroute.traceroute()
    print(json.dumps(hops, indent=4))

    wayback_obj = WayBackMachine("example.com")
    wayback_data = wayback_obj.get_urls()
    print(json.dumps(wayback_data, indent=4))
