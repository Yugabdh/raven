#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        reverseiplookup
# Purpose:     reverseip lookup module using hackertarget API and yougetsignal
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# -------------------------------------------------------------------------------

import json

from raven.helper.web.webreq import WebRequest
import requests


class ReverseIPLookup(object):
    """
    Perform a reverse IP lookup to find all A records associated with an
    IP address. The results can pinpoint virtual hosts being served from a
    web server. Information gathered can be used to expand the attack
    surface when identifying vulnerabilities on a server.

    Attributes:

        ip: IP address
    """

    def __init__(self, ip: str) -> None:
        """
        :param ip: IP address of target
        """

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
        print(self.ip)
        url = "https://domains.yougetsignal.com/domains.php"
        payload = {
            'remoteAddress': self.ip
        }

        headers = {
            'Host': "domains.yougetsignal.com",
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            'Connection': "keep-alive",
            'Cache-Control': "no-cache",
            'Origin': "http://www.yougetsignal.com",
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/53.0.2785.143 Chrome/53.0.2785.143 Safari/537.36"
        }

        result = requests.post(
            url,
            headers = headers,
            data=payload,
            timeout=7
        ).content
        print(result)
        json_op = json.loads(result)
        domains = []
        if "Success" in json_op['status']:
            if "0" not in json_op['domainCount']:
                domains = json_op['domainArray']

        return domains
