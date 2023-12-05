"""routes.py - Main routes for the application."""
import os
from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import lazyload
from .forms import LoginForm
from .models import User, Site, BaseModel

bp = Blueprint("main", __name__)


@bp.context_processor
def inject_admin_models():
    if current_user.is_authenticated and current_user.is_admin:
        admin_models = [model.__name__ for model in BaseModel.__subclasses__()]
        return {'admin_models': admin_models}
    return {'admin_models': []}


@bp.context_processor
def inject_domains():
    return {
        'mainsail_domain': os.environ.get('MAINSAIL_DOMAIN'),
        'octoprint_domain': os.environ.get('OCTOPRINT_DOMAIN')
    }


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@bp.route("/home", methods=["GET", "POST"])
def index():
    """Index page"""
    site = Site.query.options(lazyload(Site.timeline)).first()
    return render_template("index.html", site=site)


@bp.route('/mainsail', methods=['GET', 'POST'])
@login_required
def mainsail():
    """Mainsail page"""
    mainsail_url = current_app.config.get('MAINSAIL_URL')
    return render_template('mainsail.html', mainsail_url=mainsail_url)


@bp.route('/octoprint', methods=['GET', 'POST'])
@login_required
def octoprint():
    """Octoprint page"""
    octoprint_url = current_app.config.get('OCTOPRINT_URL')
    return render_template('octoprint_redirect.html', octoprint_url=octoprint_url)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login the current user."""
    if current_user.is_authenticated:
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.form.get("next") or request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.index"))
        flash("Invalid username or password.")

    return render_template("login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    site = Site.query.first()
    if request.method == 'POST':
        files = request.files.getlist("file[]")
        for file in files:
            if file:
                # Save each file
                file.save(os.path.join('/MakUrSpace/web-uploads', file.filename))
        return redirect(url_for('main.upload_file'))
    return render_template('upload.html', site=site)


# Catch all other routes and redirect to the index
# NOTE: Must be last!
@bp.route("/<path:unused_path>")
def catch_all(unused_path):
    return redirect(url_for("main.index"))
