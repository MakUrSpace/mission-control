"""Docker Healthcheck model for Service."""
from app.extensions import db
from app.models.base_model import BaseModel

class DockerHealthcheck(BaseModel):
    """Healthcheck model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "docker_healthcheck"
    test = db.Column(db.String(250), nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    timeout = db.Column(db.Integer, nullable=False)
    retries = db.Column(db.Integer, nullable=False)
    start_period = db.Column(db.Integer, nullable=False)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=True
    )
