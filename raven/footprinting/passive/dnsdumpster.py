#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        dnsdumpster
# Purpose:     This is the (unofficial) Python API for dnsdumpster.com Website.
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# -------------------------------------------------------------------------------

import requests
import re
import sys
import base64

from bs4 import BeautifulSoup


class DNSDumpsterAPI:
    """
    DNSDumpsterAPI scrapes dnsdumster.com

    Methods:

    scrape: Query, Parse and store result of scraping in result.
    retrieve_results: Helper method extract data from tables and return to
                      result to quering function.
    retrieve_txt_record: Helper method extract txt record data from tables
                         and return to result to quering function.
    fetch: Helper method calls scrap and returns result of scraping.
    subdomain: Returns list of subdomain found.

    Attributes:

        domain: Domain to query 'dnsdumster.com'.
        session: Session variable to store current session while scraping.
        result: Stores result of scraping.
    """

    def __init__(self, domain: str) -> None:
        self.domain = domain
        self.session = requests.Session()
        self.result = {}

    def scrape(self):
        """
        Query, Parse and store result of scraping in result.
        """

        dnsdumpster_url = 'https://dnsdumpster.com/'
        req = self.session.get(dnsdumpster_url)

        # Getting csrf_token
        soup = BeautifulSoup(req.content, 'html.parser')
        csrf_inputbox = soup.findAll('input',
                                     attrs={'name': 'csrfmiddlewaretoken'})
        csrf_middleware = csrf_inputbox[0]['value']
        cookies = {'csrftoken': csrf_middleware}
        headers = {'Referer': dnsdumpster_url}
        data = {
            'csrfmiddlewaretoken': csrf_middleware,
            'targetip': self.domain
        }
        req = self.session.post(
            dnsdumpster_url,
            cookies=cookies,
            data=data,
            headers=headers
        )

        error_str = 'There was an error getting results'
        error = error_str in req.content.decode('utf-8')
        if req.status_code != 200 or error:
            # Error getting data
            return []

        soup = BeautifulSoup(req.content, 'html.parser')
        tables = soup.findAll('table')

        res = {}
        res['domain'] = self.domain
        res['dns_records'] = {}
        res['dns_records']['dns'] = self.retrieve_results(tables[0])
        res['dns_records']['mx'] = self.retrieve_results(tables[1])
        res['dns_records']['txt'] = self.retrieve_txt_record(tables[2])
        res['dns_records']['host'] = self.retrieve_results(tables[3])

        # Network mapping image
        try:
            tmp_url = f"https://dnsdumpster.com/static/map/{self.domain}.png"
            image_data = base64.b64encode(self.session.get(tmp_url).content)
        except:
            image_data = None
        finally:
            res['image_data'] = image_data

        self.result = res

    def retrieve_results(self, table) -> list:
        """
        Helper method extract data from tables and return to
        result to quering function.

        Args:

            table: NavigableString object
        """

        res = []
        trs = table.findAll('tr')
        for tr in trs:
            tds = tr.findAll('td')
            pattern_ip = r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'
            try:
                _ = str(tds[0]).split('<br/>')[0]
                domain = _.split('>')[1]
                td_content = tds[0].text.replace('\n', '')
                header = ' '.join(td_content.split(' ')[1:])
                ip = re.findall(pattern_ip, tds[1].text)[0]
                reverse_dns = tds[1].find('span', attrs={}).text

                additional_info = tds[2].text
                country = tds[2].find('span', attrs={}).text
                autonomous_system = additional_info.split(' ')[0]
                provider = ' '.join(additional_info.split(' ')[1:])
                provider = provider.replace(country, '')
                data = {
                    'domain': domain,
                    'ip': ip,
                    'reverse_dns': reverse_dns,
                    'as': autonomous_system,
                    'provider': provider,
                    'country': country,
                    'header': header,
                }
                res.append(data)
            except:
                print("[!] Error while scraping dnsdumster")
                res = []

        return res

    def retrieve_txt_record(self, table) -> list:
        """
        Helper method extract txt record data from tables
        and return to result to quering function.

        Args:

            table: NavigableString object
        """

        res = []
        for td in table.findAll('td'):
            res.append(td.text)
        return res

    def fetch(self) -> dict:
        """
        Helper method calls scrap and returns result of scraping.
        """

        if self.result:
            res = self.result
        else:
            self.scrape()
            res = self.result
        return res

    def subdomain(self) -> list:
        """
        Returns list of subdomains found with help of dns records.
        """

        if self.result:
            res = self.result
        else:
            self.scrape()
            res = self.result

        hosts = []

        for host in res['dns_records']['host']:
            hosts.append(host['domain'])

        return hosts
