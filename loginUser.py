from flask import Flask, request, render_template, redirect, url_for, flash
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUserMixin,
                            confirm_login, fresh_login_required)
class User(UserMixin):
    def __init__(self, name, id, active=True):
        super(User, self).__init__()
        self.name = str(name)
        self.id = id
        self.active = active
        

    def is_active(self):
        return self.active

    def set_authenticated(self, value):
        if value:
            self._authenticated = True

    def is_authenticated(self):
        return self._authenticated

USERS = {
    1: User(u"admin", 1),
    2: User(u"Steve", 2),
    3: User(u"Creeper", 3, False),
}

USER_NAMES = dict((u.name, u) for u in USERS.itervalues())








