# Importación del módulo de base de datos (db)
from db import db

# Definición del modelo de tipo de artículo
class ItemTypeModel(db.Model):
    """
    Modelo de tipo de artículo en la base de datos.

    Atributos:
    - id: Identificador único del tipo de artículo.
    - type: Nombre/descripción del tipo de artículo.
    - items: Relación con la tabla de artículos (ItemModel).
    """
    __tablename__ = "item_types"

    # Columnas en la tabla de tipos de artículo
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    
    # Relación con la tabla de artículos (ItemModel)
    items = db.relationship('ItemModel', back_populates='item_type')
