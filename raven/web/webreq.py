#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        webreq
# Purpose:     Fetch, request websites with requests module
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import requests
import random
import json

from pathlib import Path
from requests.exceptions import HTTPError, ConnectionError
from requests import Response


class WebRequest(object):
    """
    WebRequest

    Methods:

        make_request: Returns Response object for URL
    """

    def __init__(self) -> None:
        path = Path(__file__).parent.parent / "data/user_agent.txt"

        try:
            with path.open() as fp:
                self.all_user_agents = fp.readlines()
        except:
            self.all_user_agents = None

    def get_user_agent(self) -> str:
        """
        Returns user-agent string
        """

        if self.all_user_agents is None:
            user_agent = "Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.3)"\
                         " Gecko/20091020 Ubuntu/9.10 (karmic) Firefox/3.5.3"
        else:
            user_agent = random.choice(self.all_user_agents).strip()

        return user_agent

    def make_request(
            self,
            method: str,
            url: str,
            headers: dict=dict(),
            params: dict=dict(),
            data: dict=dict(),
            allow_redirects: bool=True,
            verify: bool=True,
            timeout: int=10
            ) -> Response:
        """
        Returns response from get request to target

        Args:

            method(str): GET, POST
            url(str): URL to make GET request
            header(dict)(Optional): Custom header to pass while making request
            params(dict)(Optional): Parameters to pass while making request
            data(dict)(Optional): Data to send
            allow_redirects(bool): Allow redirect. Default True.
            verify(bool)(default: True): Verify if host have SSL
            timeout(int)(Optional): Request timeout
        """

        user_agent = self.get_user_agent()
        headers['User-Agent'] = user_agent
        headers['Accept-Language'] = 'en-US;'

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                data=json.dumps(data) if data else data,
                allow_redirects=allow_redirects,
                verify=verify,
                timeout=timeout
            )
            response.raise_for_status()
        except HTTPError as http_err:
            print(f"[!] HTTP error occurred: {http_err}")
            response = None
        except ConnectionError:
            print("[!] Connection Error: "
                  "Possible reasons: Bad URL, Connection Blocked")
            response = None
        except Exception as err:
            print(f"[!] Error occurred: {err}")
            response = None

        return response
