# -*- coding: utf-8 -*-

import urllib
import logging
import hashlib
import simplejson as json

from tornado import httpclient
from tornado.httputil import url_concat

class RenrenMixin(object):
    _OAUTH_AUTHORIZE_URL = "https://graph.renren.com/oauth/authorize"
    _OAUTH_TOKEN_URL = "https://graph.renren.com/oauth/token"
    _RENREN_API_URL = "http://api.renren.com/restserver.do"
    def _oauth_consumer_token(self):
        self.require_setting("renren_consumer_key", "Renren OAuth")
        self.require_setting("renren_consumer_secret", "Renren OAuth")
        return dict(key = self.settings['renren_consumer_key'], \
                    secret = self.settings['renren_consumer_secret'])
    def _oauth_access_token_url(self, response_code, callback_uri):
        consumer_token = self._oauth_consumer_token()
        url = self._OAUTH_TOKEN_URL
        args = {
            'grant_type' : 'authorization_code', 
            'client_id'  : consumer_token['key'], 
            'client_secret' : consumer_token['secret'], 
            'redirect_uri' : callback_uri or '', 
            'code' : response_code, 
        }
        return url_concat(url, args)
    def _on_access_token(self, callback, response):
        if response.error:
            logging.warning("Could not fetch access token")
            callback(None)
            return
        access_token = json.loads(response.body)
        callback(access_token)
    def _sig_request(self, args):
        consumer_token = self._oauth_consumer_token()
        s = "".join(["%s=%s" % (k, args[k]) for k in sorted(args.keys())])
        s = s + consumer_token['secret']
        s = unicode(s)
        return hashlib.md5(s.encode("utf-8")).hexdigest()
    def renren_request(self, method, access_token, args = {}, callback = None):
        url = self._RENREN_API_URL
        args['v'] = '1.0'
        args['access_token'] = access_token['access_token']
        args['format'] = 'json'
        args['method'] = method
        args['sig'] = self._sig_request(args)
        http = self.get_auth_http_client()
        http.fetch(url, method = "POST", body = urllib.urlencode(args), callback = callback)
    def authorize_redirect(self, callback_uri=None):
        consumer_token = self._oauth_consumer_token()
        args = {
            'client_id': consumer_token['key'], 
            'redirect_uri': callback_uri or '', 
            'response_type': 'code', 
        }
        self.redirect(url_concat(self._OAUTH_AUTHORIZE_URL, args))
    def get_auth_http_client(self):
        return httpclient.AsyncHTTPClient()
    def get_authenticated_user(self, callback, callback_uri = None):
        code = self.get_argument("code")
        http = self.get_auth_http_client()
        http.fetch(self._oauth_access_token_url(code, callback_uri), 
                   self.async_callback(self._on_access_token, callback))


