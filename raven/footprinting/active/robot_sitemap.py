#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        robot
# Purpose:     Get URLs from robot.txt and sitemap.xml
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

from raven.helper.web.webreq import WebRequest


class Robot_sitemap(object):
    """
    Helper class to get robot and sitemap

    Attributes:

        domain: target domain(str)
        https: Have SSL or not(bool)
    """

    def __init__(self, domain: str, https: bool) -> None:
        """
        :param domain: Domain Name of target
        :param https: Have SSL or not
        """

        if https:
            self.url = "https://" + domain
        else:
            self.url = "http://" + domain

    def robot(self):
        """
        Get URLs from robot.txt
        """

        url = self.url + '/robots.txt'
        req = WebRequest()
        result = req.make_request(
            method="GET",
            url=url
        )
        print(result.text)

    def sitemap(self):
        """
        Get URLs from sitemap.xml
        """

        url = self.url + '/sitemap.xml'
        req = WebRequest()
        result = req.make_request(
            method="GET",
            url=url
        )
        print(result.text)
