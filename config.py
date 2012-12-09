# -*- coding: utf-8 -*-

import os

site_config = {
    'site_title' : u'Stormwind', 
    'base_domain' : '', 
    'login_url' : '/signin', 
    'template_path' : os.path.join(os.path.dirname(__file__), "templates"), 
    'static_path' : os.path.join(os.path.dirname(__file__), "static"), 
    'i18n_path' : os.path.join(os.path.dirname(__file__), "i18n"), 
    'db_path' : '', 
    'xsrf_cookies' : True, 
    'cookie_secret' : '', 
    'bcrypt_salt' : '', # import bcrypt; bcrypt.gensalt(log_rounds=4)
}

try:
    from local_config import site_config
except ImportError:
    pass
