"""Contact component model."""
from app.extensions import db
from app.models.base_model import BaseModel

class Contact(BaseModel):
    """Contact model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "contact"
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    linkedin = db.Column(db.String(250), nullable=True)
    github = db.Column(db.String(250), nullable=True)
    facebook = db.Column(db.String(250), nullable=True)
    twitter = db.Column(db.String(250), nullable=True)
    instagram = db.Column(db.String(250), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", name="fk_user_id"), nullable=True
    )
