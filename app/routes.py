"""routes.py - Main routes for the application."""
import os
from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    jsonify,
    request,
    current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from .forms import LoginForm
from .models import User, Site, BaseModel, Service

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
    site = Site.query.first()
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


@bp.route('/update-environment-vars/<int:service_id>', methods=['POST'])
@login_required
def update_environment_vars(service_id):
    service = Service.query.get(service_id)
    if service:
        old_env_values = {ev.key: ev.value for ev in service.environment_vars}
        # Update environment variables and sync DockerPort host_port
        for key, value in request.form.items():
            env_var = next((ev for ev in service.environment_vars if ev.key == key), None)
            if env_var:
                env_var.value = value

            # If the environment variable ends with '_PORT', update the DockerPort
            if key.endswith('_PORT'):
                try:
                    new_port_value = int(value)
                    old_port_value = int(old_env_values.get(key, 0))

                    # Find the corresponding DockerPort and update its host_port
                    for docker_port in service.docker_ports:
                        if docker_port.host_port == int(old_port_value):
                            docker_port.host_port = new_port_value
                except ValueError:
                    # Handle the case where the new port value is not a valid integer
                    return jsonify({'message': 'Invalid port value'}), 400

        db.session.commit()
        return jsonify({'message': 'Environment variables updated successfully'})
    return jsonify({'message': f'Service not found for service_id={service_id}'}), 404


@bp.route('/service/<int:service_id>/start', methods=['POST'])
@login_required
def service_start(service_id):
    service = Service.query.get(service_id)
    if service:
        service.start()
        return jsonify({'message': f'{service.name} started successfully'})
    return jsonify({'message': f'Service not found for service_id={service_id}'}), 404


@bp.route('/service/<int:service_id>/stop', methods=['POST'])
@login_required
def service_stop(service_id):
    service = Service.query.get(service_id)
    if service:
        service.stop()
        return jsonify({'message': f'{service.name} stopped successfully'})
    return jsonify({'message': f'Service not found for service_id={service_id}'}), 404


@bp.route('/service/<int:service_id>/restart', methods=['POST'])
@login_required
def service_restart(service_id):
    service = Service.query.get(service_id)
    if service:
        service.restart()
        return jsonify({'message': f'{service.name} restarted successfully'})
    return jsonify({'message': f'Service not found for service_id={service_id}'}), 404

@bp.route('/service/<int:service_id>/is_running', methods=['GET'])
def is_service_running(service_id):
    service = Service.query.get(service_id)
    if service:
        return jsonify({
            'is_running': service.is_running,
            'url': service.url
        })
    else:
        return jsonify({'error': 'Service not found'}), 404



# Catch all other routes and redirect to the index
# NOTE: Must be last!
@bp.route("/<path:unused_path>")
def catch_all(unused_path):
    return redirect(url_for("main.index"))
