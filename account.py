# -*- coding: utf-8 -*-

import logging
import simplejson as json

import tornado.web
import tornado.auth
from tornado.web import HTTPError

from stormwind.db import MemberDBMixin
from stormwind.db.models import Member
from stormwind.ext.weibo import WeiboMixin
from stormwind.ext.renren import RenrenMixin
from stormwind.ext.tencent import TencentMixin
from stormwind.base import BaseHandler

class SigninHandler(BaseHandler, MemberDBMixin, tornado.auth.GoogleMixin):
    def get(self):
        self.render("account.signin.html")
    def post(self):
        args = self.get_argument_list(["username", "password"], \
                                      [self._("Username"), self._("Password")], \
                                      None)
        error = []
        for name, translate, value in args:
            if not value:
                error.append(self._("%s is required." % translate))
                continue
            if len(value) < 4:
                error.append(self._("%s is too short." % translate))
                continue
            if len(value) > 32:
                error.append(self._("%s is too long." % translate))
                continue
        username = args[0][2]
        password = args[1][2]
        if '@' in username:
            member = self.select_member_by_email_lower(email.lower())
        else:
            member = self.select_member_by_username_lower(username.lower())
        if member == None:
            error.append(self._("User not exists."))
        elif member.password != self.encrypt_password(password):
            error.append(self._("Wrong Username and password combination."))
        if error:
            self.render("account.signin.html", locals())
            return
        auth = self.create_auth(member.id)
        self.set_secure_cookie("auth", auth.secret)
        self.set_secure_cookie("uid", str(auth.member_id))
        self.redirect("/")

class SigninGoogleHandler(BaseHandler, tornado.auth.GoogleMixin, MemberDBMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        member = self.select_member_by_email_lower(user['email'].lower())
        if member:
            auth = self.create_auth(member.id)
            self.set_secure_cookie("auth", auth.secret)
            self.set_secure_cookie("uid", str(auth.member_id))
            self.redirect("/")
            return
        self.clear_all_cookies()
        self.set_secure_cookie("google_auth", user['email'])
        self.redirect("/signup")

class SignupHandler(BaseHandler, MemberDBMixin):
    def _get_auth(self):
        ''' Return auth_type, auth_key '''
        google = self._get_google_auth()
        if google:
            return "google", google
        weibo = self._get_weibo_auth()
        if weibo:
            return "weibo", weibo
        renren = self._get_renren_auth()
        if renren:
            return "renren", renren
        tencent = self._get_tencent_auth()
        if tencent:
            return "tencent", tencent
        return '', None
    def _get_google_auth(self):
        google_auth = self.get_secure_cookie("google_auth")
        return google_auth
    def _get_weibo_auth(self):
        weibo_auth = self.get_secure_cookie("weibo_auth")
        return weibo_auth
    def _get_renren_auth(self):
        renren_auth = self.get_secure_cookie("renren_auth")
        return renren_auth
    def _get_tencent_auth(self):
        tencent_auth = self.get_secure_cookie("tencent_auth")
        return tencent_auth
    def get(self):
        auth_type, email = self._get_auth()
        if auth_type == "weibo":
            email = email + "@user.weibo.com"
        elif auth_type == "renren":
            email = email + "@user.renren.com"
        elif auth_type == "tencent":
            email = email + "@user.t.qq.com"
        self.render("account.signup.html", locals())
    def post(self):
        args = self.get_argument_list(["email", "username", "password"], \
                                      [self._("Email"), self._("Username"), self._("Password")], \
                                      None)
        error = []
        for name, translate, value in args:
            if not value:
                error.append(self._("%s is required." % translate))
                continue
            if len(value) < 4:
                error.append(self._("%s is too short." % translate))
                continue
            if len(value) > 32:
                error.append(self._("%s is too long." % translate))
                continue
            if name == "username":
                if not value.isalnum():
                    error.append(self._("A username can only contain letters and digits."))
            if name == "email" and not self.check_email(value):
                error.append(self._("Email address is invaild."))
                continue
        email = args[0][2]
        username = args[1][2]
        password = args[2][2]
        if self.select_member_by_email_lower(email):
            error.append(self._("This email is already registered."))
        elif self.select_member_by_username_lower(username):
            error.append(self._("This username is already taken."))
        if error:
            google_auth = self._get_google_auth()
            if not google_auth:
                self.redirect("/signin/google")
            self.render("account.signup.html", locals())
            return
        member = Member(email, username, self.encrypt_password(password), self.get_browser_locale().code) 
        self.db.add(member)
        self.db.commit()
        self.clear_all_cookies()
        auth = self.create_auth(member.id)
        self.set_secure_cookie("auth", auth.secret)
        self.set_secure_cookie("uid", str(auth.member_id))
        self.redirect("/")

class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect("/")

class SigninRenrenHandler(BaseHandler, RenrenMixin, MemberDBMixin):
    def _on_auth(self, user):
        if not user:
            raise HTTPError(500, "Sign in with Renren failed.")
        member = self.select_member_by_renren_id(user['user']['id'])
        if member:
            auth = self.create_auth(member.id)
            self.set_secure_cookie("auth", auth.secret)
            self.set_secure_cookie("uid", str(auth.member_id))
            self.redirect("/")
            return
        self.clear_all_cookies()
        self.set_secure_cookie("renren_auth", str(user['user']['id']))
        self.redirect("/signup")
    @tornado.web.asynchronous
    def get(self):
        callback_uri = self.settings['base_domain'] + '/signin/renren'
        if self.get_argument("code", None):
            self.get_authenticated_user(self.async_callback(self._on_auth), callback_uri)
            return
        self.authorize_redirect(callback_uri = callback_uri)

class SigninTencentHandler(BaseHandler, TencentMixin, MemberDBMixin):
    def _on_auth(self, user):
        if not user:
            raise HTTPError(500, "Sign in with Tencent failed.")
        member = self.select_member_by_tencent_id(user['access_token']['openid'])
        if member:
            auth = self.create_auth(member.id)
            self.set_secure_cookie("auth", auth.secret)
            self.set_secure_cookie("uid", str(auth.member_id))
            self.redirect("/")
            return
        self.clear_all_cookies()
        self.set_secure_cookie("tencent_auth", user['access_token']['openid'])
        self.redirect('/signup')
    @tornado.web.asynchronous
    def get(self):
        redirect_uri = self.settings['base_domain'] + '/signin/tencent'
        if self.get_argument("code", None):
            self.get_authenticated_user(redirect_uri = redirect_uri, \
                                        code = self.get_argument("code", None), \
                                        callback = self.async_callback(self._on_auth))
            return
        self.authorize_redirect(redirect_uri = redirect_uri, \
                                client_id = self.settings["tencent_consumer_key"], \
                                extra_params = {"response_type" : "code"})

class SigninWeiboHandler(BaseHandler, WeiboMixin, MemberDBMixin):
    @tornado.web.asynchronous
    def get(self):
        redirect_uri = self.settings['base_domain'] + '/signin/weibo'
        if self.get_argument("code", False):
            self.get_authenticated_user(
                redirect_uri = redirect_uri,
                client_id=self.settings["weibo_client_id"],
                client_secret=self.settings["weibo_client_secret"],
                code=self.get_argument("code"),
                callback=self.async_callback(self._on_login))
            return
        self.authorize_redirect(redirect_uri=redirect_uri,
                              client_id=self.settings["weibo_client_id"],
                              extra_params={"response_type": "code"})
    def _on_login(self, user):
        if not user:
            raise HTTPError(500, "Sign in with Weibo failed.")
        member = self.select_member_by_weibo_id(user['id'])
        if member:
            auth = self.create_auth(member.id)
            self.set_secure_cookie("auth", auth.secret)
            self.set_secure_cookie("uid", str(auth.member_id))
            self.redirect("/")
            return
        self.clear_all_cookies()
        self.set_secure_cookie("weibo_auth", str(user['id']))
        self.redirect('/signup')

route = [
    (r'/signin', SigninHandler), 
    (r'/signin/google', SigninGoogleHandler), 
    (r'/signin/renren', SigninRenrenHandler), 
    (r'/signin/tencent', SigninTencentHandler), 
    (r'/signin/weibo', SigninWeiboHandler), 
    (r'/signup', SignupHandler), 
    (r'/signout', SignoutHandler), 
]
