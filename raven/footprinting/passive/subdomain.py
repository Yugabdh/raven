#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        subdomain
# Purpose:     Finds sub domains for given target
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
#
# Created:     -
# Copyright:   -
# Licence:     -
# -------------------------------------------------------------------------------

from raven.footprinting.passive.googledork import GoogleDork
from raven.footprinting.passive.dnsdumpster import DNSDumpsterAPI


class Subdomain:
    def __init__(self, domain) -> None:
        self.domain = domain
        self.result = dict()

    def google(self):
        """
        Find subdomains with google
        """
        g = GoogleDork(self.domain)
        urls = g.single_query("")
        temp = set()
        for url in urls:
            domain = url.split("//")[1].split("/")[0]
            temp.add(domain)
        self.result["google_results"] = list(temp)
        return self.result["google_results"]

    def dnsdumpster(self):
        """
        Find subdomains with DNSdumpsterAPI
        """
        dnsdumpster_obj = DNSDumpsterAPI(self.domain)
        result = dnsdumpster_obj.subdomain()
        self.result["dnsdumpster_results"] = result
        return self.result["dnsdumpster_results"]

    def getResult(self):
        return self.result
