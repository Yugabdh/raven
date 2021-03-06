#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        geoip
# Purpose:     GEoIP lookup module using ipstack, ipinfo and, hackertarget API.
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
#
# Created:     -
# Copyright:   -
# Licence:     -
# -------------------------------------------------------------------------------

import json

from raven.helper.web.webreq import WebRequest


class GeoIPLookup(object):
    """
    GeoIPLookup
    GeoIP Lookup to get location and other possible details on IP address.

    Attributes:

        ip: Ip address(str) target
    """
    def __init__(self, ip: str) -> None:
        """

        :param ip: IP address of target
        """

        self.ip = ip
        self.req = WebRequest()

    def ipstack_api(self, key: str = None) -> json:
        """
        IPSTACK API request
        :param key: API key
        :return: Result from API
        """

        url = "http://api.ipstack.com/" + self.ip
        payload = {
            'access_key': key,
        }
        result = self.req.make_request(
            method='GET',
            url=url,
            params=payload
        )
        if 'null' not in result:
            result = json.loads(result.text)
        else:
            result = {}
        return result

    def ipinfo_api(self, key: str = None) -> json:
        """
        IPINFO API request
        :param key: API key
        :return: Result from API
        """

        url = "https://ipinfo.io/" + self.ip + "/json"
        payload = {
            'token': key,
        }
        result = self.req.make_request(
            method='GET',
            url=url,
            params=payload
        )
        if 'error' not in result:
            result = json.loads(result.text)
        else:
            result = {}
        return result

    def hackertarget_api(self) -> json:
        """
        HACKERTARGET GEOIP API request
        :return: Result from API
        """

        url = "https://api.hackertarget.com/geoip/"
        payload = {
            'q': self.ip,
        }
        result = self.req.make_request(
            method='GET',
            url=url,
            params=payload
        )
        result = result.text
        data = {}
        if 'error' not in result:
            result = result.splitlines()
            for line in result:
                _ = line.split(':')
                key = _[0].strip()
                value = _[1].strip()
                data[key] = value

        else:
            print('Outbound Query Exception!')

        return data
