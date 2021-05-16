#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        nmap_auto
# Purpose:     Nmap is one of the most popular and widely used security 
#              auditing tools, its name means "Network Mapper". This is for 
#              automating few scans by Nmap.
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import nmap3


class Nmap_auto(object):
    """
    Helper class for nmap
    This package requires NMAP to be installed on the system.
    To run some methods of this module user needs administrator permissions(superuser)
    """

    def osmap(self, ip):
        """
        OS Mapping done with help of nmap
        Args:
            ip: IP address of nmap

        Returns:
            nmap result
        """
        nmap = nmap3.Nmap()
        os_results = nmap.nmap_os_detection(ip)
        return os_results

    def subnet(self, ip):
        """
        Subnet of give ip is calculated with help of nmap
        Args:
            ip: IP address of nmap

        Returns:
            nmap result
        """
        nmap = nmap3.Nmap()
        results = nmap.nmap_subnet_scan(ip)  # Must be root
        return results

    def topports(self, ip):
        """
        Well known ports are scanned of given IP address
        Args:
            ip: IP address of nmap

        Returns:
            nmap result
        """
        nmap = nmap3.Nmap()
        results = nmap.scan_top_ports(ip)
        return results
