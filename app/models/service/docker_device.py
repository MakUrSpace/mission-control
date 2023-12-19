"""Docker Device model for Service."""
from app.extensions import db
from app.models.base_model import BaseModel

class DockerDevice(BaseModel):
    """Device model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "docker_device"
    container_path = db.Column(db.String(250), nullable=False)
    host_path = db.Column(db.String(250), nullable=False)
    cgroup_permissions = db.Column(db.String(25), nullable=False, default="r")
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=False
    )
