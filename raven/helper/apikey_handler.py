#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        apikey_handler
# Purpose:     Handels API keys: updates, reads api keys
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import json

from pathlib import Path


def get_api_keys():
    """
    :return: API keys from json file
    """

    file_name = Path(__file__).parent.parent / "data/api_keys.json"
    keys = dict()

    with open(file_name) as f:
        data = json.load(f)
        keys.update(data)

    return keys


def update_keys(keys):
    file_name = Path(__file__).parent.parent / "data/api_keys.json"

    with open(file_name, "w") as f:
        json.dump(keys, f)
