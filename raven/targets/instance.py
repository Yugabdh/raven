#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        instance
# Purpose:     Intializes target
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import requests
import random
import socket

from raven.web.webreq import WebRequest


class Instance(object):
    """
    Intializes target

    Attributes:

        domain(str): domain name
        https(bool): have https or http
        ip(str): Address for host at domain name

    Methods:

        get_status: Returns status of website
        get_ip: Get IP address for URL
    """

    def __init__(self, domain: str, https: bool=True, ip: str=None) -> None:
        self.domain = domain
        self.https = https
        self.ip = ip

        if https:
            self.url = "https://" + domain
        else:
            self.url = "http://" + domain

    def get_status(self, url: str=None) -> tuple:
        """
        Returns status code for url

        Args:

            url(str): URL to check status. Default is http(s)://domainname.tld

        Returns:

            status code(str), reason(str)
        """

        if url is None:
            url = self.url

        try:
            req = WebRequest()
            response = req.make_request('HEAD', url)
            if response:
                status_code = response.status_code
                reason = response.reason
            else:
                raise Exception()
        except requests.exceptions.ConnectionError:
            status_code = "000"
            reason = "Connection Error"
        except requests.exceptions.ReadTimeout:
            status_code = "001"
            reason = "TimeOut Error"
        except Exception as exp:
            status_code = "002"
            reason = "Error"

        return (str(status_code), reason, )

    def get_ip(self, domain: str=None) -> str:
        """
        Returns IP address for domain

        Args:

            domain(str): Domain name. Default is domainname.tld

        Returns:

            status code(str), reason(str)
        """

        if domain is None:
            domain = self.domain
            if self.ip:
                return self.ip

        try:
            ip = socket.gethostbyname(domain)
        except:
            ip = None

        if domain == self.domain:
            self.ip = ip

        return ip
