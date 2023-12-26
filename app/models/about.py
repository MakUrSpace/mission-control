"""About component model."""
from app.extensions import db
from app.models.base_model import BaseModel

class About(BaseModel):
    """About model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "about"
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
