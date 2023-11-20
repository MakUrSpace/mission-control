"""admin.py - Flask-Admin configuration"""""
from flask_admin import Admin, menu
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
from flask_login import current_user
from .models import db, Timeline, TimelineSection, TimelineSubsection, Project, Site, Contact, User

# Initialize Flask-Admin
admin = Admin(template_mode='bootstrap3')

admin.add_link(menu.MenuLink(name='Back to Home', category='', url='/'))

class SecureModelView(ModelView):
    """Wrapper for ModelView to provide authentication.

    Args:
        ModelView : Base class for model based views.
    """
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('main.login', next=request.url))
        return redirect(url_for('main.index'))

# Add the views to the admin interface
admin.add_view(SecureModelView(User, db.session, category='Models'))
admin.add_view(SecureModelView(Site, db.session, category='Models'))
admin.add_view(SecureModelView(Timeline, db.session, category='Models'))
admin.add_view(SecureModelView(TimelineSection, db.session, category='Models'))
admin.add_view(SecureModelView(TimelineSubsection, db.session, category='Models'))
admin.add_view(SecureModelView(Project, db.session, category='Models'))
admin.add_view(SecureModelView(Contact, db.session, category='Models'))
