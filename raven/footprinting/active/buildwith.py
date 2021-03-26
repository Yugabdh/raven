#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        buildwith
# Purpose:     Finds out technologies target system is using
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# -------------------------------------------------------------------------------

import builtwith


class BuildWith(object):
    """
    Finds out technologies target system is using
    Attributes:
        domain: domain(str)
    """

    def __init__(self, domain, https):
        """
        :param domain: Domain Name of target
        :param https: Have SSL or not
        """
        if https:
            self.url = "https://" + domain
        else:
            self.url = "http://" + domain

    def discover(self):
        result = dict()
        try:
            result = builtwith.parse(self.url)
        except Exception as e:
            print('[!] Error : {0}'.format(str(e)))

        return result
