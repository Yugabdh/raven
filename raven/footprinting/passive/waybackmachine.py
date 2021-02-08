#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        waybackmachine
# Purpose:     wayback lookup using web.archive.org
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# -------------------------------------------------------------------------------

from raven.web.webreq import WebRequest

import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WayBackMachine(object):
    """
    WayBackMachine

    Fetches data from web.archive.org for all website instances at different
    time. Can be used to find endpoints or passive crawler.

    Methods:

        get_urls: Queries 'web.archive.org' with given domain and returns URLs.

    Attributes:

        domain: Domain to query 'web.archive.org'
    """

    def __init__(self, domain: str) -> None:
        self.domain = domain

    def get_urls(self):
        """
        Queries 'web.archive.org' with given domain and returns URLs.
        """

        webarchive_url = "https://web.archive.org/cdx/search/cdx"
        payload = {
            'url': self.domain,
            'output': 'json',
            'matchType': 'prefix',
            'collapse': 'urlkey',
            'fl': 'original,mimetype,timestamp,endtimestamp,groupcount,uniqcount',
            'ilter': '!statuscode:[45]..',
            'limit': 100000,
            '_': 1547318148315,
        }

        req = WebRequest()
        result = req.make_request(
            method='GET',
            url=webarchive_url,
            params=payload,
            verify=False
        )

        if result:
            json_data = json.loads(result.text)
            if len(json_data) == 0:
                print("[!] No results found")
        else:
            json_data = json.loads([])

        return json_data
