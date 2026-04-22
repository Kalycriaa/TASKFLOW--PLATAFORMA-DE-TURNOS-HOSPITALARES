from ..extensions import db
from ..utils import serializar_datetime


class Turno(db.Model):
    __tablename__ = "turnos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unidade_id = db.Column(db.Integer, db.ForeignKey("unidades_hospitalares.id"), nullable=False, index=True)
    profissional_confirmado_id = db.Column(db.Integer, db.ForeignKey("profissionais.id"), nullable=True, index=True)
    categoria = db.Column(db.String(80), nullable=False, index=True)
    tipo_turno = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="aberto", index=True)
    valor = db.Column(db.Float, nullable=True)
    observacoes = db.Column(db.String(250), nullable=True)
    inicio_em = db.Column(db.DateTime, nullable=True)
    fim_em = db.Column(db.DateTime, nullable=True)

    unidade = db.relationship("UnidadeHospitalar", back_populates="turnos")
    profissional_confirmado = db.relationship(
        "Profissional",
        back_populates="turnos_confirmados",
        foreign_keys=[profissional_confirmado_id],
    )
    candidaturas = db.relationship(
        "Candidatura",
        back_populates="turno",
        lazy=True,
        cascade="all, delete-orphan",
    )
    avaliacoes = db.relationship(
        "Avaliacao",
        back_populates="turno",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "unidade_id": self.unidade_id,
            "profissional_confirmado_id": self.profissional_confirmado_id,
            "categoria": self.categoria,
            "tipo_turno": self.tipo_turno,
            "status": self.status,
            "valor": self.valor,
            "observacoes": self.observacoes,
            "inicio_em": serializar_datetime(self.inicio_em),
            "fim_em": serializar_datetime(self.fim_em),
            "unidade": self.unidade.to_summary() if self.unidade else None,
            "profissional_confirmado": self.profissional_confirmado.to_summary() if self.profissional_confirmado else None,
        }
