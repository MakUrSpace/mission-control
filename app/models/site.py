"""Site model that reflects an instance of the web app."""
from app.extensions import db
from app.models.base_model import BaseModel

class Site(BaseModel):
    """Site model to represent a website.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "site"
    title = db.Column(db.String(50), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    logo = db.Column(db.String(250), nullable=False)
    contact_id = db.Column(
        db.Integer, db.ForeignKey("contact.id", name="fk_contact_id"), nullable=False
    )
    contact = db.relationship(
        "Contact", backref="site", lazy=True, foreign_keys=[contact_id]
    )
    about_id = db.Column(
        db.Integer, db.ForeignKey("about.id", name="fk_about_id"), nullable=True
    )
    about = db.relationship("About", backref="site", lazy=True, uselist=False)
    services = db.relationship("Service", backref="site", lazy=True)

