from ..extensions import db


class UnidadeHospitalar(db.Model):
    __tablename__ = "unidades_hospitalares"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(120), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(10), nullable=True)
    avaliacao_media = db.Column(db.Float, nullable=False, default=5.0)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    turnos = db.relationship(
        "Turno",
        back_populates="unidade",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_summary(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "avaliacao_media": self.avaliacao_media,
        }

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "endereco": self.endereco,
            "cidade": self.cidade,
            "estado": self.estado,
            "cep": self.cep,
            "avaliacao_media": self.avaliacao_media,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
