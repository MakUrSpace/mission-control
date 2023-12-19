"""User model."""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db
from app.models.base_model import BaseModel

class User(UserMixin, BaseModel):
    """User model.

    Args:
        UserMixin : Mixin for implementing Flask-Login user management.
        BaseModel : Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "user"
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    last_failed_login = db.Column(db.DateTime)
    failed_login_count = db.Column(db.Integer, default=0)
    contacts = db.relationship("Contact", backref="user", lazy=True)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id
