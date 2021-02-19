#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        reverseiplookup
# Purpose:     reverseip lookup module using hackertarget API and yougetsignal
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# -------------------------------------------------------------------------------

import requests
import json

from raven.web.webreq import WebRequest


class ReverseIPLookup(object):
    """
    Perform a reverse IP lookup to find all A records associated with an
    IP address. The results can pinpoint virtual hosts being served from a
    web server. Information gathered can be used to expand the attack
    surface when identifying vulnerabilities on a server.

    Attributes:

        ip: IP address
        domain: Domain name
    """

    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.req = WebRequest()

    def query_hackertarget(self) -> list:
        """
        queries hackertarget API to get all virtual hosts on server
        """

        url = "http://api.hackertarget.com/reverseiplookup/"
        payload = {
            'q': self.ip,
        }
        other_domain = []

        result = self.req.make_request(
            method='GET',
            url=url,
            params=payload
        )
        result = str(result.text)

        if "error check your search parameter" not in result:
            for domain in result.splitlines():
                other_domain.append(domain)

        return other_domain

    def query_yougetsignal(self) -> list:
        """
        queries yougetsignal API to get all virtual hosts on server
        """

        url = "https://domains.yougetsignal.com/domains.php"
        payload = {
            'remoteAddress': self.ip,
            'key': ''
        }

        result = self.req.make_request(
            method='POST',
            url=url,
            data=payload
        )
        json_op = json.loads(result.text)
        domains = []
        if "Success" in json_op['status']:
            if "0" not in json_op["domainCount"]:
                domains = json_op['domainArray']

        return domains
