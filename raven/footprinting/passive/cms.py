#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        cms
# Purpose:     Check what CMS website is using if it have any
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# -------------------------------------------------------------------------------

import json

from raven.web.webreq import WebRequest


class CMSDiscoveryPassive(object):
    """
    CMSDiscoveryPassive

    Attributes:

        key: API key for whatcms.org(str)
        domain: target domain(str)
    """

    def __init__(self, key: str):
        """
        :param key: whatcms.org key
        """
        self.key = key

    def query(self, domain: str):
        """
        Queries whatcms.org with given API key and domain
        :param domain: domain name to query
        :return: CMS Discovered
        """

        url = "https://whatcms.org/APIEndpoint/Detect"
        payload = {
            "url": domain,
            "key": self.key
        }
        cms = {}

        req = WebRequest()
        result = req.make_request(
            method="GET",
            url=url,
            params=payload
        )
        json_data = json.loads(result.text)

        if len(json_data) == 0 or len(json_data["result"]) == 0:
            print("[!] No results found")

        elif json_data["result"]["code"] == 201:
            print("[!] Failed: CMS or Host Not Found")

        else:
            cms = {
                "name": json_data["result"]["name"],
                "confidence": json_data["result"]["confidence"],
                "version": json_data["result"]["version"]
            }
        return cms
