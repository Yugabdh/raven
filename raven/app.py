#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        app
# Purpose:     Entry point to application
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

from raven.targets.initialize import Initialize
from raven.web.webreq import WebRequest


def run():
    """
    Function which starts chain.
    """

    target = Initialize("google.c", True)
    status, reason = target.get_status()
    print(status, reason)
    print(target.get_ip())
