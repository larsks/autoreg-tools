#!/usr/bin/python

# The plan:
# - Read credentials from a configuration file
# - Authenticate to autoreg
# - Request
#   https://autoreg.fas.harvard.edu/tools/scopes.html?scope=<scope>
# - Parse result into structured form

import os
import sys
import csv
import optparse
import urllib
import urllib2

import lxml.etree as ET

import configdict

csv_fields = [ 'junk', 'hostname', 'ipaddr', 'macaddr', 'owner' ]

class AutoregError (Exception):
    def __init__ (self, msg=None, request=None, response=None):
        super(AutoregError, self).__init__(msg)
        self.request = request
        self.response = response

class HTTPError(AutoregError):
    pass

class LoginError(AutoregError):
    pass

class LoginRequired(AutoregError):
    pass

class Autoreg (object):
    base_url    = 'https://autoreg.fas.harvard.edu'

    login_url   = '%s/home/index.html'          % base_url
    scope_url   = '%s/tools/scopes.html'        % base_url
    client_url  = '%s/tools/client/client.html' % base_url

    def __init__ (self, config):
        self.config = config['autoreg']
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        self.authenticated = False

    def login(self):
        params = {
                'username': self.config['username'],
                'password': self.config['password'],
                }
        data = '&'.join(['%s=%s' % (k,v) for k,v in params.items()])
        req = urllib2.Request(self.login_url, data)
        response = self.opener.open(req)

        if response.getcode() != 200:
            raise HTTPError('%s: %s' % (r.getcode(), r.msg),
                    request=req,
                    response=response)

        doc = ET.parse(response, ET.HTMLParser())
        error = doc.find('//p[@class="error"]')
        if error is not None:
            raise LoginError('Login failed: %s' % error.text,
                    request=req, response=response)

        self.authenticated = True

    def scope(self, scope):
        if not self.authenticated:
            raise LoginRequired()

        params = {
                'scope': scope,
                }
        data = urllib.urlencode(params)
        req = urllib2.Request(self.scope_url, data)
        response = self.opener.open(req)

        return self.parse_scopes(response)

    def parse_scopes (self, response):
        doc = ET.parse(response, ET.HTMLParser())
        rows = doc.xpath('/html/body//table/tr[th = "Host Name"]/..//tr')

        data = []
        for row in rows:
            cells = row.findall('td')

            # This skips the header row, which has only <th>
            # elements.
            if not cells:
                continue

            cells_text = []
            for cell in cells:
                if cell.find('a') is not None:
                    cells_text.append(cell.find('a').text.strip())
                else:
                    cells_text.append(cell.text.strip())
            data.append(dict(zip(csv_fields, cells_text)))

        return data

def parse_args():
    p = optparse.OptionParser()
    p.add_option('-f', '--config', default='autoreg.conf')
    return p.parse_args()

if __name__ == '__main__':
    opts, args = parse_args()
    config = configdict.ConfigDict(opts.config)
    print config

    ar = Autoreg(config)

