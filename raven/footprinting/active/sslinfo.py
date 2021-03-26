#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        sslinfo
# Purpose:     Get info on website's certificate.
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import socket
import ssl


class SSL(object):
    """
    Get info on website's certificate.
    """

    def __init__(self, domain: str, https: bool = True):
        """
        :param domain: Domain Name of target
        :param https: Have SSL or not
        """
        self.domain = domain
        self.https = https

    def context(self):
        context = ssl.create_default_context()
        ex = context.wrap_socket(socket.socket(), server_hostname=self.domain)
        return ex

    def get_ssl(self):
        try:
            s = self.context()
            s.connect((self.domain, 443))
            info = s.getpeercert()
            cipher = s.cipher()
            ssl.get_server_certificate((self.domain, 443))

            info_dic = {
                "certSNo": str(info.get('serialNumber')),
                "version": str(info.get('version')),
                "cipherSuit": str(cipher[0]),
                "encProtocol": str(cipher[1]),
                "encType": str(cipher[2]) + ' bit',
                "certRaw": info,
            }
            return info_dic
        except Exception as e:
            print(e)
            return dict()
