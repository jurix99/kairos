"""
Modèles SQLAlchemy pour la base de données
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Utilisateur de l'application"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, nullable=False, index=True)  # ID du provider OAuth
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    picture = Column(String(500), nullable=True)  # URL de l'avatar
    provider = Column(String(50), nullable=False)  # google, github, microsoft, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    events = relationship("Event", back_populates="user")
    categories = relationship("Category", back_populates="user")


class Category(Base):
    """Catégorie d'événement avec code couleur"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    color_code = Column(String(7), nullable=False)  # Format hex: #RRGGBB
    description = Column(Text, nullable=True)
    
    # Clé étrangère vers l'utilisateur
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable pour les catégories par défaut
    
    # Relations
    events = relationship("Event", back_populates="category")
    user = relationship("User", back_populates="categories")


class Event(Base):
    """Événement de l'agenda"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=True)
    priority = Column(String(10), nullable=False, default="medium")
    status = Column(String(20), nullable=False, default="pending")  # pending, in-progress, completed, cancelled
    is_flexible = Column(Boolean, default=True)  # Peut être déplacé automatiquement
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Champ pour la récurrence (par exemple, "daily", "weekly", "monthly")
    recurrence_rule = Column(String(50), nullable=True)
    
    # Champ pour lier les événements récurrents à l'événement parent
    parent_event_id = Column(Integer, ForeignKey("events.id"), nullable=True)

    # Clés étrangères
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relations
    category = relationship("Category", back_populates="events")
    user = relationship("User", back_populates="events")
    
    # Relation pour les événements récurrents
    parent_event = relationship("Event", remote_side=[id], backref="children") 