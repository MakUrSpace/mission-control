"""admin.py - Flask-Admin configuration""" ""
from flask_admin import Admin, menu
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
from flask_login import current_user
from app.models import BaseModel
from app.extensions import db

# Initialize Flask-Admin
admin = Admin(template_mode="bootstrap3")

admin.add_link(menu.MenuLink(name="Back to Home", category="", url="/"))

class SecureModelView(ModelView):
    """Wrapper for ModelView to provide authentication.

    Args:
        ModelView : Base class for model based views.
    """
    can_export = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("main.login", next=request.url))
        return redirect(url_for("main.index"))


# Reflectively add all models to the admin interface
for model in BaseModel.__subclasses__():
    admin.add_view(SecureModelView(model, db.session, category="Models"))
    