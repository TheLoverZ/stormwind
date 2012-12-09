# -*- coding: utf-8 -*-

import httplib
import traceback

import tornado.web
import tornado.locale

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
    @property
    def db(self):
        return self.application.db
    @property
    def jinja2(self):
        return self.application.jinja2
