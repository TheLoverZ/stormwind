# -*- coding: utf-8 -*-

import urllib
import logging

import simplejson as json

from tornado import httpclient
from tornado.auth import OAuth2Mixin
from tornado.httputil import url_concat

class TencentMixin(OAuth2Mixin):
    _OAUTH_ACCESS_TOKEN_URL = "https://open.t.qq.com/cgi-bin/oauth2/access_token"
    _OAUTH_AUTHORIZE_URL = "https://open.t.qq.com/cgi-bin/oauth2/authorize"
    _OAUTH_NO_CALLBACKS = False
    _TENCENT_API = "https://open.t.qq.com/api"

    def get_authenticated_user(self, redirect_uri, code, callback):
        consumer_token = self._oauth_consumer_token()
        http = httpclient.AsyncHTTPClient()
        args = {
            "client_id" : consumer_token["key"], 
            "client_secret" : consumer_token["secret"], 
            "code" : code, 
            "redirect_uri" : redirect_uri, 
            "extra_params": {"grant_type": "authorization_code"},
        }

        http.fetch(self._oauth_request_token_url(**args), \
                   callback = self.async_callback(self._on_access_token, redirect_uri, callback))

    def _on_get_user_info(self, access_token, callback, user):
        logging.info(user)
        user['access_token'] = access_token
        callback(user)
    
    def _on_access_token(self, redirect_uri, callback, response):
        if response.error:
            logging.warning("Tencent Weibo auth error: %s" % response.body)
            callback(None)
            return

        access_token = {}
        for field in response.body.split("&"):
            logging.info(field)
            k, v = field.split("=")
            access_token[k] = v

        if 'errorCode' in access_token.keys():
            logging.warning("Tencent Weibo auth error: %s" % response.body)
            callback(None)
            return

        logging.info(access_token)
        self.tencent_request(path = "/user/info", \
                             callback = self.async_callback(self._on_get_user_info, access_token, callback), \
                             access_token = access_token)

    def _oauth_consumer_token(self):
        self.require_setting("tencent_consumer_key", "Tencent Weibo OAuth")
        self.require_setting("tencent_consumer_secret", "Tencent Weibo OAuth")
        return dict(key = self.settings["tencent_consumer_key"], \
                    secret = self.settings["tencent_consumer_secret"])

    def tencent_request(self, path, access_token, callback, post_args = None, **kwargs):
        url = self._TENCENT_API + path
        consumer_token = self._oauth_consumer_token()
        
        args = {}
        args['oauth_consumer_key'] = consumer_token['key']
        args['access_token'] = access_token['access_token']
        args['openid'] = access_token['openid']
        args['oauth_version'] = '2.a'
        args['scope'] = 'all'
        args['clientip'] = self.request.remote_ip
        args['format'] = 'json'
        args.update(kwargs)
        url = url_concat(url, args)
        callback = self.async_callback(self._on_tencent_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(url, method="POST", body = urllib.urlencode(post_args), callback = callback)
        else:
            http.fetch(url, callback)

    def _on_tencent_request(self, callback, response):
        if response.error:
            logging.warning("%s Failed in fetching %s", response.error, response.url)
            callback(None)
            return
        callback(json.loads(response.body))
