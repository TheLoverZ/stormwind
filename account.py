# -*- coding: utf-8 -*-

import logging
import simplejson as json

import tornado.web
import tornado.auth

from stormwind.db import MemberDBMixin
from stormwind.db.models import Member
from stormwind.ext.renren import RenrenMixin
from stormwind.base import BaseHandler

class SigninHandler(BaseHandler, MemberDBMixin, tornado.auth.GoogleMixin):
    def get(self):
        self.render("account.signin.html")
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
            if name == "email" and not self.check_email(value):
                error.append(self._("Email address is invaild."))
                continue
        username = args[1][2]
        password = args[2][2]
        member = self.select_member_by_username_lower(username)
        if member.password == self.encrypt_password(password):
            auth = self.create_auth(member.id)
            self.set_secure_cookie("auth", auth.secret)
            self.set_secure_cookie("uid", str(auth.member_id))
            self.redirect("/")
        else:
            error.append(self._("username/password not match"))
            if error:
                self.render("account.signin.html", locals())
                return

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
        self.set_secure_cookie("google_auth", json.dumps(user))
        self.redirect("/signup/google")

class SignupHandler(BaseHandler, MemberDBMixin):
    def _get_google_auth(self):
        try:
            google_auth = json.loads(self.get_secure_cookie("google_auth"))
        except json.JSONDecodeError:
            google_auth = None
        except TypeError:
            google_auth = None
        return google_auth
    def get(self):
        google_auth = self._get_google_auth()
        if not google_auth:
            self.redirect("/signin/google")
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
        self.clear_cookie("google_auth")
        auth = self.create_auth(member.id)
        self.set_secure_cookie("auth", auth.secret)
        self.set_secure_cookie("uid", str(auth.member_id))
        self.redirect("/")

class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect("/")

class SigninRenrenHandler(BaseHandler, RenrenMixin):
    def _on_auth(self, user):
        logging.info(user)
        self.finish()
    @tornado.web.asynchronous
    def get(self):
        callback_uri = self.settings['base_domain'] + '/signin/renren'
        if self.get_argument("code", None):
            self.get_authenticated_user(self.async_callback(self._on_auth), callback_uri)
            return
        self.authorize_redirect(callback_uri = callback_uri)

route = [
    (r'/signin', SigninHandler), 
    (r'/signin/google', SigninGoogleHandler), 
    (r'/signin/renren', SigninRenrenHandler), 
    (r'/signup', SignupHandler), 
    (r'/signup/google', SignupHandler), 
    (r'/signout', SignoutHandler), 
]
