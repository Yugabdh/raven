#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        webserver_detect
# Purpose:     Detects webserver by inspecting headers
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import requests


class Webserver_detect(object):
    def __init__(self, https: bool, domain: str):
        """
        Args:
            domain: domain name of target
        """
        if https:
            self.url = "https://" + domain
        else:
            self.url = "http://" + domain

    def detect(self):
        data = dict()
        try:
            r = requests.get(self.url)
            print(r)
            if 'cloudflare' in r.headers:
                print("The website is behind Cloudflare.")
            data["raw"] = dict(r.headers)
            if 'Server' in data["raw"].keys():
                data['Server'] = r.headers['Server']
            try:
                data["X-Powered-By"] = r.headers['X-Powered-By']
            except Exception:
                pass
        except Exception:
            pass
        return data
