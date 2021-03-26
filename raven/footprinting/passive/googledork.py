#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        googledork
# Purpose:     Module to perform google dorking on given query.
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# -------------------------------------------------------------------------------

try:
    from google import search
except ModuleNotFoundError:
    from googlesearch import search
from pathlib import Path
import random
import time
import re


class GoogleDork(object):
    """
    Module to perform google dorking on given query.

    Attributes:

        domain: Domain name of target
    """

    def __init__(self, domain: str) -> None:
        """
        :param domain: Domain name of target
        """

        self.domain = domain
        path = Path(__file__).parent.parent.parent / "data/user_agent.txt"
        try:
            with path.open() as fp:
                self.all_user_agents = fp.readlines()
        except FileNotFoundError:
            print("[!] user_agent.txt file not found")
            self.all_user_agents = ["Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                    "(KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"]

    def single_query(self, dork: str, maxop: int = 30) -> list:
        """
        single_query executes single Google dork
        :param dork: Google dork
        :param maxop: maximum query output to return
        :return: list of urls found using Google dorking
        """

        result = list()
        query = f"site:{self.domain} {dork}"
        # Search string is longer than 32 words.
        if len(query.split(" ")) > 32:
            temp = " ".join(query.split(" ")[32:])
            print("Google limits queries to 32 words (separated by spaces):"
                  " Removing from search query: "
                  f"'{temp}'")

            # Consider only first 32 char of query
            updated_query = " ".join(query.split(" ")[0:32])
            if query.endswith('"'):
                updated_query = f'{updated_query}"'
            query = updated_query

        sleep_for = random.uniform(16.9, 36.9) + random.random() * 10
        user_agent = random.choice(self.all_user_agents).strip()
        print(query)
        for url in search(
            query,
            start=0,
            stop=maxop,
            num=100,
            pause=sleep_for,
            extra_params={"filter": "0"},
            user_agent=user_agent,
            tbs="li:1",  # Doesn't return suggested results with other domains.
        ):
            # Ignore results from exploit-db.com hosting the actual dorks.
            url_to_ignore = "https://www.exploit-db.com/ghdb"
            if re.search(url_to_ignore, url, re.IGNORECASE):
                continue
            else:
                result.append(url)
        return result

    def multi_query(self, query_list: list) -> list:
        """
        multi_query executes multiple Google dorks
        :param query_list: List of Google dorks
        :return: list of urls found using Google dorking
        """

        result = list()
        for query in query_list:
            current_result = self.single_query(query)
            time.sleep(random.uniform(16.9, 36.9))
            result.append(current_result)
        return result
