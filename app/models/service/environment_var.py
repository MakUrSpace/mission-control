"""Environment Variable model for Service."""
from app.extensions import db
from app.models.base_model import BaseModel

class EnvironmentVar(BaseModel):
    """EnvironmentVar model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "environment_var"
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=False
    )
