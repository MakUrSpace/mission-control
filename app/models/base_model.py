"""BaseModel to be inherited by all models."""
from datetime import datetime
from app.extensions import db

class BaseModel(db.Model):
    """BaseModel to be inherited by all models.

    Args:
        db (Model): Model class from SQLAlchemy, acting as a base.
    """

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    last_modified = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
