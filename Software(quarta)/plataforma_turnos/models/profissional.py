from ..extensions import db


class Profissional(db.Model):
    __tablename__ = "profissionais"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(80), nullable=False, index=True)
    registro_conselho = db.Column(db.String(60), nullable=True)
    endereco = db.Column(db.String(200), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(10), nullable=True)
    preferencia_turno = db.Column(db.String(50), nullable=False, index=True)
    avaliacao_media = db.Column(db.Float, nullable=False, default=5.0)
    taxa_aceitacao = db.Column(db.Float, nullable=False, default=0.5)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    candidaturas = db.relationship(
        "Candidatura",
        back_populates="profissional",
        lazy=True,
        cascade="all, delete-orphan",
    )
    turnos_confirmados = db.relationship(
        "Turno",
        back_populates="profissional_confirmado",
        lazy=True,
        foreign_keys="Turno.profissional_confirmado_id",
    )

    def to_summary(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "avaliacao_media": self.avaliacao_media,
        }

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "registro_conselho": self.registro_conselho,
            "endereco": self.endereco,
            "cidade": self.cidade,
            "estado": self.estado,
            "cep": self.cep,
            "preferencia_turno": self.preferencia_turno,
            "avaliacao_media": self.avaliacao_media,
            "taxa_aceitacao": self.taxa_aceitacao,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
