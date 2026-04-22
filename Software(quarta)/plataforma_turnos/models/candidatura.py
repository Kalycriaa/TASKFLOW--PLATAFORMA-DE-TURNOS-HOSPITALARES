from datetime import datetime

from ..extensions import db
from ..utils import serializar_datetime


class Candidatura(db.Model):
    __tablename__ = "candidaturas"
    __table_args__ = (
        db.UniqueConstraint("turno_id", "profissional_id", name="uq_candidatura_turno_profissional"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    turno_id = db.Column(db.Integer, db.ForeignKey("turnos.id"), nullable=False, index=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="pendente", index=True)
    pontuacao_match = db.Column(db.Float, nullable=False)
    distancia_km = db.Column(db.Float, nullable=True)
    criada_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    atualizada_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    turno = db.relationship("Turno", back_populates="candidaturas")
    profissional = db.relationship("Profissional", back_populates="candidaturas")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "turno_id": self.turno_id,
            "profissional_id": self.profissional_id,
            "status": self.status,
            "pontuacao_match": round(self.pontuacao_match, 4),
            "distancia_km": round(self.distancia_km, 2) if self.distancia_km is not None else None,
            "criada_em": serializar_datetime(self.criada_em),
            "atualizada_em": serializar_datetime(self.atualizada_em),
            "profissional": self.profissional.to_summary() if self.profissional else None,
            "turno": self.turno.to_dict() if self.turno else None,
        }
