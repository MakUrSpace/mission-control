"""models.py"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()
migrate = Migrate()

class BaseModel(db.Model):
    """BaseModel to be inherited by all models.

    Args:
        db (Model): Model class from SQLAlchemy, acting as a base.
    """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Timeline(BaseModel):
    """Timeline model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """
    __tablename__ = 'timeline'
    title = db.Column(db.String(50), nullable=False)
    sections = db.relationship('TimelineSection', \
        backref='timeline', lazy=True, order_by='asc(TimelineSection.id)')

class TimelineSection(BaseModel):
    """TimelineSection model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """
    __tablename__ = 'timeline_section'
    title = db.Column(db.String(50), nullable=False)
    timeline_id = db.Column(db.Integer, db.ForeignKey('timeline.id', name='fk_timeline_id'), nullable=False)
    subsections = db.relationship('TimelineSubsection', \
        backref='timeline_section', lazy=True, order_by='desc(TimelineSubsection.start_date)')

class TimelineSubsection(BaseModel):
    """TimelineSubsection model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """
    __tablename__ = 'timeline_subsection'
    title = db.Column(db.String(50), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    details = db.Column(db.Text, nullable=True)
    timelinesection_id = db.Column(db.Integer, db.ForeignKey('timeline_section.id', name='fk_timelinesection_id'), nullable=False)
    
class Project(BaseModel):
    """Project model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """
    __tablename__ = 'project'
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id', name='fk_site_id'), nullable=False)

class About(BaseModel):
    """About model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """
    __tablename__ = 'about'
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Site(BaseModel):
    """Site model to represent a website.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """
    __tablename__ = 'site'
    title = db.Column(db.String(50), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    logo = db.Column(db.String(250), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id', name='fk_contact_id'), nullable=False)
    contact = db.relationship('Contact', backref='site', lazy=True, foreign_keys=[contact_id])
    timeline_id = db.Column(db.Integer, db.ForeignKey('timeline.id', name='fk_timeline_id'), unique=True, nullable=True)
    timeline = db.relationship('Timeline', backref=db.backref('site', uselist=False), lazy=True, foreign_keys=[timeline_id])
    projects = db.relationship('Project', backref='site', lazy=True)
    about_id = db.Column(db.Integer, db.ForeignKey('about.id', name='fk_about_id'), nullable=True)
    about = db.relationship('About', backref='site', lazy=True, uselist=False)

class Contact(BaseModel):
    """Contact model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """
    __tablename__ = 'contact'
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    linkedin = db.Column(db.String(250), nullable=True)
    github = db.Column(db.String(250), nullable=True)
    facebook = db.Column(db.String(250), nullable=True)
    twitter = db.Column(db.String(250), nullable=True)
    instagram = db.Column(db.String(250), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_user_id'), nullable=True)

class Metadata(BaseModel):
    """Metadata model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """
    __tablename__ = 'metadata'
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    
class User(UserMixin, BaseModel):
    """User model.

    Args:
        UserMixin : Mixin for implementing Flask-Login user management.
        BaseModel : Custom base model to provide additional standardized functionality.
    """
    __tablename__ = 'user'
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    last_failed_login = db.Column(db.DateTime)
    failed_login_count = db.Column(db.Integer, default=0)
    contacts = db.relationship('Contact', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id
