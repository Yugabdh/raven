#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        waybackmachine
# Purpose:     wayback lookup using web.archive.org
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# -------------------------------------------------------------------------------

import json

from raven.web.webreq import WebRequest


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
        """
        :param domain: Domain name of target
        """

        self.domain = domain

    def get_urls(self, start_year: int = None, stop_year: int = None):
        """
        Queries 'web.archive.org' with given domain and returns URLs.
        :param start_year: Query from this year
        :param stop_year: Query to this year
        :return: Result from web.archive.org as JSON object
        """

        webarchive_url = "https://web.archive.org/cdx/search/cdx"
        payload = {
            'url': self.domain,
            'from': start_year,
            'to': stop_year,
            'output': 'json',
            'matchType': 'prefix',
            'collapse': 'urlkey',
            'fl': 'original,mimetype,timestamp,'
                  'endtimestamp,groupcount,uniqcount',
            'ilter': '!statuscode:[45]..',
            'limit': 100000,
            '_': 1547318148315,
        }

        req = WebRequest()
        result = req.make_request(
            method='GET',
            url=webarchive_url,
            params=payload
        )

        if result:
            json_data = json.loads(result.text)
            if len(json_data) == 0:
                print("[!] No results found")
        else:
            json_data = json.loads("")

        return json_data
