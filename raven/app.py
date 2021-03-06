#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        app
# Purpose:     Entry point to application
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

from raven.gui import app


def run():
    """
    Function which starts chain.
    """

    app.run(debug=True)
