"""Docker Port model for Service."""
from app.extensions import db
from app.models.base_model import BaseModel

class DockerPort(BaseModel):
    """Port model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "docker_port"
    container_port = db.Column(db.Integer, nullable=False)
    host_port = db.Column(db.Integer, nullable=False)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=False
    )
