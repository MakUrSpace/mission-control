"""routes.py - Main routes for the application."""
from flask import Blueprint, Response, render_template, flash, redirect, url_for, current_app, request
from flask_login import login_user, logout_user, login_required, current_user
import requests
from sqlalchemy.orm import lazyload
from .forms import LoginForm
from .models import User, Site

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
def index():
    """Index page"""
    site = Site.query.options(lazyload(Site.timeline)).first()
    return render_template('index.html', site=site)

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

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login the current user."""
    if current_user.is_authenticated:
        next_page = request.form.get('next') or request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.form.get('next') or request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid username or password.')

    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@bp.route('/<path:unused_path>')
def catch_all(unused_path):
    return redirect(url_for('main.index'))
