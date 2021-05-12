#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        cms
# Purpose:     Check what CMS website is using if it have any
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# -------------------------------------------------------------------------------

import json

from raven.helper.web.webreq import WebRequest


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

        url = "https://whatcms.org/API/Tech"
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

        if json_data["result"]["code"] == 101 or json_data["result"]["code"] == 100 or json_data["result"]["code"] == 113:
            cms["msg"] = json_data["result"]["msg"]
            cms["code"] = json_data["result"]["code"]
            print("[!] Failed: API key error")

        elif json_data["result"]["code"] == 201:
            cms["msg"] = json_data["result"]["msg"]
            cms["code"] = json_data["result"]["code"]
            print("[!] Failed: CMS or Host Not Found")

        elif len(json_data["results"]) == 0:
            cms["msg"] = "[!] Failed: CMS or Host Not Found"
            cms["code"] = json_data["result"]["code"]
            print("[!] Failed: CMS or Host Not Found")

        else:
            cms["code"] = json_data["result"]["code"]
            cms["msg"] = json_data["result"]["msg"]
            cms["data"] = json_data["results"]
        return cms
