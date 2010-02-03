#!/usr/bin/python

import os
import sys
import csv
import optparse
import urllib
import urllib2

import lxml.etree as ET

import configdict
import iptools

csv_fields = [ 'hostname', 'ipaddr', 'macaddr', 'owner' ]

class AutoregError (Exception):
    def __init__ (self, msg=None, request=None, response=None, doc=None):
        super(AutoregError, self).__init__(msg)
        self.request    = request
        self.response   = response
        self.doc        = doc

class HTTPError(AutoregError):
    pass

class LoginError(AutoregError):
    pass

class LoginRequired(AutoregError):
    pass

def cmp_ip (a, b):
    a = iptools.ip2long(a['ipaddr'])
    b = iptools.ip2long(b['ipaddr'])

    return cmp(a,b)

def authenticated(func):
    def _ (self, *args, **kwargs):
        if not self.authenticated:
            raise LoginRequired()

        return func(self, *args, **kwargs)

    return _

class Autoreg (object):
    base_url    = 'https://autoreg.fas.harvard.edu'

    login_url   = '%s/home/index.html'          % base_url
    scope_url   = '%s/tools/scopes.html'        % base_url
    bulk_url   = '%s/admin/bulk.html'           % base_url
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

        if response.code != 200:
            raise HTTPError('%s: %s' % (r.getcode(), r.msg),
                    request=req,
                    response=response)

        doc = ET.parse(response, ET.HTMLParser())
        error = doc.find('//p[@class="error"]')
        if error is not None:
            raise LoginError('Login failed: %s' % error.text,
                    req, response, doc)

        self.authenticated = True

    @authenticated
    def scope(self, scope):
        '''Return all registrations in a given scope.'''

        params = {
                'scope': scope,
                }
        data = urllib.urlencode(params)
        req = urllib2.Request(self.scope_url, data)
        response = self.opener.open(req)

        return self._parse_scopes(response)

    @authenticated
    def unregister(self, *args):
        '''Unregister one or more clients, identified by MAC address.'''

        params = {
                'clients': '\n'.join([x.strip() for x in args]),
                'action': 'unregisterClients',
                'type': 'unregister',
                }

        data = urllib.urlencode(params)
        req = urllib2.Request(self.bulk_url, data)
        response = self.opener.open(req)

        doc = ET.parse(response, ET.HTMLParser())
        error = doc.find('//p[@class="error"]')
        if error is not None:
            raise AutoregError(error.text, req, response, doc)

    def _parse_scopes (self, response):
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

            # remove first element, which is an <input> field.
            cells_text.pop(0)
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

