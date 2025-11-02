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
    goals = relationship("Goal", back_populates="user")


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
    
    # Champs pour la récurrence
    recurrence_type = Column(String(20), nullable=True)  # daily, weekly, monthly, yearly
    recurrence_interval = Column(Integer, nullable=True, default=1)  # Tous les X jours/semaines/mois
    recurrence_days = Column(String(20), nullable=True)  # Jours de la semaine pour daily (ex: "1,3,5" pour lun,mer,ven)
    recurrence_end_date = Column(DateTime, nullable=True)  # Date limite de récurrence
    recurrence_count = Column(Integer, nullable=True)  # Nombre d'occurrences max (alternative à end_date)
    
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
    
    @property
    def recurrence(self):
        """Reconstituer l'objet RecurrenceRule à partir des champs de base de données"""
        if not self.recurrence_type:
            return None
        
        # Convertir recurrence_days de string vers list
        days_of_week = None
        if self.recurrence_days:
            try:
                days_of_week = [int(d) for d in self.recurrence_days.split(',')]
            except:
                days_of_week = None
        
        # Convertir end_date vers string ISO si présent
        end_date = None
        if self.recurrence_end_date:
            end_date = self.recurrence_end_date.isoformat()
        
        from .schemas import RecurrenceRule
        return RecurrenceRule(
            type=self.recurrence_type,
            interval=self.recurrence_interval or 1,
            days_of_week=days_of_week,
            end_date=end_date,
            count=self.recurrence_count
        )


class Goal(Base):
    """Objectif personnel avec stratégie"""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(DateTime, nullable=True)  # Date cible pour atteindre l'objectif
    priority = Column(String(10), nullable=False, default="medium")  # low, medium, high
    status = Column(String(20), nullable=False, default="active")  # active, completed, paused, cancelled
    category = Column(String(50), nullable=True)  # sport, career, health, education, etc.
    
    # Stratégie et plan d'action
    strategy = Column(Text, nullable=True)  # Description de la stratégie
    success_criteria = Column(Text, nullable=True)  # Critères de réussite
    
    # Métriques optionnelles
    current_value = Column(String(100), nullable=True)  # Valeur actuelle (ex: "5km", "2h/jour")
    target_value = Column(String(100), nullable=True)  # Valeur cible (ex: "42km", "4h/jour")
    unit = Column(String(50), nullable=True)  # Unité de mesure
    
    # Dates de gestion
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)  # Date de completion
    
    # Clé étrangère vers l'utilisateur
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="goals") 