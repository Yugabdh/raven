#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        whoislookup
# Purpose:     Gather whois information about registered domain
#              by searching whois server.
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import requests
import json
import signal
import re

from pathlib import Path
from subprocess import Popen, PIPE


class Traceroute(object):
    """
    Multi-source traceroute instance.
    """

    def __init__(self, ip: str, no_geoloc: bool=False,
                 country: str="US", timeout=120) -> None:

        self.ip = ip
        self.country = country
        self.no_geo = no_geoloc
        self.timeout = timeout

        try:
            loc = "data/sources_traceroute.json"
            path = Path(__file__).parent.parent.parent / loc
            json_file = open(path, "r").read()
            sources = json.loads(json_file.replace("_IP_ADDRESS_", self.ip))
            self.source = sources[country]
        except:
            print("Error: Data file not found")
            self.country = "LO"
            self.source = {"url": "traceroute 139.5.31.64"}

        self.locations = {}
        self.data = dict()

    def traceroute(self) -> list:
        """
        Instead of running the actual traceroute command, we will fetch
        standard traceroute results from several publicly available webpages
        that are listed at traceroute.org. For each hop, we will then attach
        geolocation information to it.
        """

        if self.country == "LO":
            status_code, traceroute = self.execute_cmd(self.source["url"])
        else:
            status_code, traceroute = self.get_traceroute_output()

        if status_code != 0 and status_code != 200:
            return {"error": status_code}

        # hop_num, hosts
        hops = self.get_hops(traceroute)

        # hop_num, hostname, ip_address, rtt
        hops = self.get_formatted_hops(hops)

        if not self.no_geo:
            # hop_num, hostname, ip_address, rtt, latitude, longitude
            hops = self.get_geocoded_hops(hops)

        return hops

    def execute_cmd(self, cmd) -> tuple:
        """
        Executes given command using subprocess.Popen().
        """

        stdout = ""
        returncode = -1
        process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            signal.signal(signal.SIGALRM, self.signal_handler)
            signal.alarm(self.timeout)
            stdout = process.communicate()[0]
            returncode = process.returncode
            signal.alarm(0)
        except Exception as err:
            print(str(err))
        return (returncode, stdout.decode('ascii'))

    def get_traceroute_output(self) -> tuple:
        """
        Fetches traceroute output from a webpage.
        """

        url = self.source['url']

        if 'post_data' in self.source:
            context = self.source['post_data']
        else:
            context = None

        status_code, content = self.urlopen(url, context=context)
        content = content.strip()
        regex = r'<pre.*?>(?P<traceroute>.*?)</pre>'
        pattern = re.compile(regex, re.DOTALL | re.IGNORECASE)
        matches = re.findall(pattern, content)

        if not matches:
            # Manually append closing </pre> for partially downloaded page
            content = "{}</pre>".format(content)
            matches = re.findall(pattern, content)

        traceroute = ""

        for match in matches:
            match = match.strip()
            if match and 'ms' in match.lower():
                traceroute = match
                break

        return (status_code, traceroute)

    def get_hops(self, traceroute) -> list:
        """
        Returns hops from traceroute output in an array of dicts each
        with hop number and the associated hosts data.
        """

        hops = []
        regex = r'^(?P<hop_num>\d+)(?P<hosts>.*?)$'
        lines = traceroute.split("\n")

        for line in lines:
            line = line.strip()
            hop = {}
            if not line:
                continue
            try:
                hop = re.match(regex, line).groupdict()
            except AttributeError:
                continue
            hops.append(hop)

        return hops

    def get_formatted_hops(self, hops) -> list:
        """
        Hosts data from get_hops() is represented in a single string.
        We use this function to better represent the hosts data in a dict.
        """

        formatted_hops = []
        regex = r'(' \
                r'(?P<i1>[\d.]+) \((?P<h1>[\w.-]+)\)' \
                r'|' \
                r'(?P<h2>[\w.-]+) \((?P<i2>[\d.]+)\)' \
                r')' \
                r' (?P<r>\d{1,4}.\d{1,4}\s{0,1}ms)'

        for hop in hops:
            hop_num = int(hop['hop_num'].strip())
            hosts = hop['hosts'].replace("  ", " ").strip()
            # Using re.finditer(), we split the hosts, then for each host,
            # we store a tuple of hostname, IP address and the first RTT.
            hosts = re.finditer(regex, hosts)
            for host in hosts:
                hop_context = {
                    "hop_num": hop_num,
                    "hostname": host.group("h1") or host.group("h2"),
                    "ip_address": host.group("i1") or host.group("i2"),
                    "rtt": host.group("r"),
                }
                formatted_hops.append(hop_context)

        return formatted_hops

    def get_geocoded_hops(self, hops) -> list:
        """
        Returns hops from get_formatted_hops() with geolocation information
        for each hop.
        """

        geocoded_hops = []

        for hop in hops:
            ip_address = hop['ip_address']
            if ip_address in self.data:
                data = self.data[ip_address]
            else:
                data = self.get_location(ip_address)
                if "error" in str(data):
                    self.data[ip_address] = {"ip": ip_address}
                else:
                    self.data[ip_address] = data
            geocoded_hops.append(self.data[ip_address])

        return geocoded_hops

    def get_location(self, ip_address):
        """
        Returns geolocation information for the given IP address.
        """

        url = "http://dazzlepod.com/ip/{}.json".format(ip_address)
        status_code, json_data = self.urlopen(url)
        # print(json_data)
        if status_code == 200 and json_data:
            tmp = json.loads(json_data)
        return tmp

    def urlopen(self, url, context=None):
        """
        Fetches webpage.
        """

        user_agent = "Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.3)" \
                     " Gecko/20091020 Ubuntu/9.10 (karmic) Firefox/3.5.3"
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml",
            "user-agent": user_agent,
        }
        response = requests.get(url, headers=headers, verify=False)

        headers['cookie'] = '; '.join(
            [x.name + '=' + x.value for x in response.cookies]
            )
        headers['content-type'] = 'application/x-www-form-urlencoded'

        status_code = 200

        content = ""
        try:
            if context:
                payload = context
                response = requests.post(
                    url,
                    data=payload,
                    headers=headers,
                )
            else:
                response = requests.get(
                    url,
                    headers=headers
                )
            content = response.text
        except requests.exceptions.HTTPError as err:
            status_code = err.errno
        except requests.exceptions.InvalidURL:
            pass

        return (status_code, content)

    def chunked_read(self, response):
        """
        Fetches response in chunks. A signal handler is attached to abort
        reading after set timeout.
        """

        content = ""
        max_bytes = 1 * 1024 * 1024  # Max. page size = 1MB
        read_bytes = 0
        bytes_per_read = 64  # Chunk size = 64 bytes
        try:
            signal.signal(signal.SIGALRM, self.signal_handler)
            signal.alarm(self.timeout)
            while read_bytes <= max_bytes:
                data = response.read(bytes_per_read)
                if not data:
                    break
                content += data
                read_bytes += bytes_per_read
            signal.alarm(0)
        except Exception as err:
            print(str(err))
        return content

    def signal_handler(self, signum, frame):
        """
        Raises exception when signal is caught.
        """

        raise Exception("Caught signal {}".format(signum))
