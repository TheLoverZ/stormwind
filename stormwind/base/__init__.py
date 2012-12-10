# -*- coding: utf-8 -*-

import re
import bcrypt
import httplib
import traceback

import tornado.web
import tornado.locale

EMAIL_REGEX = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)

class BaseHandler(tornado.web.RequestHandler):
    ''' This is Stormwind Base Handler '''
    _ = lambda self, text: self.locale.translate(text)
    def get_user_locale(self):
        ''' Get user locale '''
        if self.current_user:
            return tornado.locale.get(self.current_user.locale)
        return self.get_browser_locale()
    def render(self, name, kwargs = {}):
        ''' Render page using Jinja2 '''
        if "self" in kwargs.keys():
            kwargs.pop("self")
        template = self.jinja2.get_template(name)
        rendered_page = template.render(page = self, _ = self._, user = self.current_user, **kwargs)
        self.write(rendered_page)
        self.db.close()
        self.finish()
    def write_error(self, status_code, **kwargs):
        ''' Rewrite write_error for customing error page '''
        if status_code == 404:
            self.render("404.html")
            return
        elif status_code == 500:
            error = []
            for line in traceback.format_exception(*kwargs['exc_info']):
                error.append(line)
            error_message = "\n".join(error)
            self.render("500.html", locals())
            return
        msg = httplib.responses[status_code]
        self.render("error.html", locals())
    def get_argument_list(self, names, translated, default = "none"):
        value_list = []
        for name, translate in zip(names, translated):
            if default != "none":
                value_list.append((name, translate, self.get_argument(name, default = default)))
            else:
                value_list.append((name, translate, self.get_argument(name)))
        return value_list
    def check_email(self, email):
        return EMAIL_REGEX.match(email)
    def encrypt_password(self, password):
        return bcrypt.hashpw(password, self.settings['bcrypt_salt'])
    @property
    def db(self):
        return self.application.db
    @property
    def jinja2(self):
        return self.application.jinja2
