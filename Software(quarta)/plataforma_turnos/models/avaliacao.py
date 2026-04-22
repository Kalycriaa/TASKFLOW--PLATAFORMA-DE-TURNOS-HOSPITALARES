from datetime import datetime

from ..extensions import db
from ..utils import serializar_datetime


class Avaliacao(db.Model):
    __tablename__ = "avaliacoes"
    __table_args__ = (
        db.UniqueConstraint("turno_id", "autor_tipo", name="uq_avaliacao_turno_autor"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    turno_id = db.Column(db.Integer, db.ForeignKey("turnos.id"), nullable=False, index=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id"), nullable=False, index=True)
    unidade_id = db.Column(db.Integer, db.ForeignKey("unidades_hospitalares.id"), nullable=False, index=True)
    autor_tipo = db.Column(db.String(20), nullable=False, index=True)
    nota = db.Column(db.Float, nullable=False)
    comentario = db.Column(db.String(250), nullable=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    turno = db.relationship("Turno", back_populates="avaliacoes")
    profissional = db.relationship("Profissional", foreign_keys=[profissional_id])
    unidade = db.relationship("UnidadeHospitalar", foreign_keys=[unidade_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "turno_id": self.turno_id,
            "profissional_id": self.profissional_id,
            "unidade_id": self.unidade_id,
            "autor_tipo": self.autor_tipo,
            "nota": self.nota,
            "comentario": self.comentario,
            "criado_em": serializar_datetime(self.criado_em),
        }
