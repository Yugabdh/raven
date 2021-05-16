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
    def __init__(self, domain: str):
        """
        Args:
            domain: domain name of target
        """
        self.domain = domain

    def detect(self):
        try:
            r = requests.get(self.domain)
            if 'cloudflare' in r.headers:
                print("The website is behind Cloudflare.")
            data = dict()
            data["raw"] = header
            try:
                data["X-Powered-By"] = r.headers['X-Powered-By']
                data['Server'] = r.headers['Server']
            except Exception:
                pass
        except Exception:
            pass
