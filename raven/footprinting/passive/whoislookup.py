#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        whoislookup
# Purpose:     Gather whois information about registered domain
#              by searching whois server.
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import ipwhois
import whois
import json


class Whoislookup:
    """
    Whoislookup

    Methods:

        whois_query: Returns data from Whois.
        ip_whois_query: Returns data with RDAP. Standardized responses.
    """

    def __init__(self) -> None:
        """
        init function
        """

        pass

    def whois_query(self, domain: str) -> str:
        """
        whois_query:

            Queries whois server for whois info.

        Args:

            domain(str): target domain name for target.
        """

        try:
            whois_data = whois.whois(domain)
            if whois_data:
                whois_data_text = whois_data.text
        except Exception as e:
            print("Error occured while querying whois servers. " + str(e))
            whois_data_text = ""

        return whois_data_text

    def ip_whois_query(self, ip: str) -> json:
        """
        ip_whois_query:

            ip_whois_query queries RDAP to get details.
            Results are standardized responses unlike whois.

        Args:

            ip: target IP(str) for query.
        """

        try:
            res = ipwhois.IPWhois(ip)
            ip_whois_data = res.lookup_rdap(depth=1)

        except Exception as e:
            print("Error occured while querying RDAP servers. " + str(e))
            ip_whois_data = {}

        return json.dumps(ip_whois_data, indent=4)
