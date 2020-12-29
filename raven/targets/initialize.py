#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        initailize
# Purpose:     Intializes target
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------
import requests
import random
import socket

from pathlib import Path


class Initialize(object):
    """
    Intializes target

    Attributes:

        domain(str): domain name
        https(bool): have https or http
        ip(str): Address for host at domain name
    """

    def __init__(self, domain: str, https: bool=True, ip: str=None) -> None:
        self.domain = domain
        self.https = https
        self.ip = ip

        if https:
            self.url = "https://" + domain
        else:
            self.url = "http://" + domain
        path = Path(__file__).parent.parent / "data/user_agent.txt"

        try:
            with path.open() as fp:
                self.all_user_agents = fp.readlines()
        except:
            self.all_user_agents = None

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

        if self.all_user_agents is None:
            user_agent = "Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.3)"\
                         " Gecko/20091020 Ubuntu/9.10 (karmic) Firefox/3.5.3"
        else:
            user_agent = random.choice(self.all_user_agents).strip()

        headers = {
            'User-Agent': user_agent,
        }

        try:
            response = requests.head(
                url,
                timeout=5,
                allow_redirects=True,
                headers=headers
            )
            status_code = response.status_code
            reason = response.reason
        except requests.exceptions.ConnectionError:
            status_code = '000'
            reason = 'ConnectionError'
        except requests.exceptions.ReadTimeout:
            status_code = '001'
            reason = 'TimeOut'

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
