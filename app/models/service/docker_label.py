"""Docker Label model for Service."""
from app.extensions import db
from app.models.base_model import BaseModel

class DockerLabel(BaseModel):
    """Label model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "docker_label"
    key = db.Column(db.String(60), nullable=False)
    value = db.Column(db.String(60), nullable=False)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=False
    )
