"""
Service pour calculer les temps de trajet entre deux lieux
"""

from datetime import timedelta
from typing import Optional, Dict, Tuple
import re


class TravelService:
    """
    Service pour estimer les temps de trajet entre différents lieux
    """
    
    # Cache des temps de trajet calculés
    _travel_cache: Dict[Tuple[str, str], timedelta] = {}
    
    # Temps de trajet par défaut en minutes selon le type de déplacement
    DEFAULT_TRAVEL_TIMES = {
        "same_building": 5,
        "same_neighborhood": 15,
        "same_city": 30,
        "different_city": 60,
        "unknown": 30,
    }
    
    def __init__(self):
        """Initialise le service de calcul de temps de trajet"""
        pass
    
    @classmethod
    def calculate_travel_time(
        cls,
        origin: Optional[str],
        destination: Optional[str]
    ) -> timedelta:
        """
        Calcule le temps de trajet estimé entre deux lieux
        
        Args:
            origin: Lieu de départ (peut être None)
            destination: Lieu d'arrivée (peut être None)
        
        Returns:
            timedelta représentant le temps de trajet estimé
        """
        # Si l'un des deux lieux est manquant, retourner 0
        if not origin or not destination:
            return timedelta(minutes=0)
        
        # Normaliser les adresses
        origin_norm = cls._normalize_location(origin)
        destination_norm = cls._normalize_location(destination)
        
        # Même lieu = pas de déplacement
        if origin_norm == destination_norm:
            return timedelta(minutes=0)
        
        # Vérifier le cache
        cache_key = (origin_norm, destination_norm)
        if cache_key in cls._travel_cache:
            return cls._travel_cache[cache_key]
        
        # Calculer le temps de trajet estimé
        travel_time = cls._estimate_travel_time(origin_norm, destination_norm)
        
        # Mettre en cache
        cls._travel_cache[cache_key] = travel_time
        
        return travel_time
    
    @classmethod
    def _normalize_location(cls, location: str) -> str:
        """
        Normalise un lieu pour la comparaison
        
        Args:
            location: Lieu à normaliser
        
        Returns:
            Lieu normalisé (minuscules, sans espaces superflus)
        """
        return re.sub(r'\s+', ' ', location.lower().strip())
    
    @classmethod
    def _estimate_travel_time(cls, origin: str, destination: str) -> timedelta:
        """
        Estime le temps de trajet entre deux lieux normalisés
        
        Cette méthode utilise des heuristiques simples basées sur les adresses.
        Dans une version plus avancée, on pourrait utiliser une API de géolocalisation.
        
        Args:
            origin: Lieu de départ normalisé
            destination: Lieu d'arrivée normalisé
        
        Returns:
            timedelta représentant le temps de trajet estimé
        """
        # Extraire les informations d'adresse
        origin_parts = origin.split(',')
        dest_parts = destination.split(',')
        
        # Même bâtiment (même adresse complète sauf étage/bureau)
        if len(origin_parts) >= 2 and len(dest_parts) >= 2:
            # Comparer l'adresse principale (sans le dernier élément qui pourrait être le bureau)
            if origin_parts[0].strip() == dest_parts[0].strip():
                return timedelta(minutes=cls.DEFAULT_TRAVEL_TIMES["same_building"])
        
        # Même quartier/arrondissement
        if len(origin_parts) >= 3 and len(dest_parts) >= 3:
            if origin_parts[-2].strip() == dest_parts[-2].strip():
                return timedelta(minutes=cls.DEFAULT_TRAVEL_TIMES["same_neighborhood"])
        
        # Même ville
        if len(origin_parts) >= 2 and len(dest_parts) >= 2:
            if origin_parts[-1].strip() == dest_parts[-1].strip():
                return timedelta(minutes=cls.DEFAULT_TRAVEL_TIMES["same_city"])
        
        # Villes différentes
        return timedelta(minutes=cls.DEFAULT_TRAVEL_TIMES["different_city"])
    
    @classmethod
    def needs_travel_buffer(
        cls,
        origin: Optional[str],
        destination: Optional[str],
        min_threshold_minutes: int = 10
    ) -> bool:
        """
        Détermine si un buffer de temps de trajet est nécessaire
        
        Args:
            origin: Lieu de départ
            destination: Lieu d'arrivée
            min_threshold_minutes: Seuil minimal en minutes pour considérer un déplacement
        
        Returns:
            True si un buffer est nécessaire, False sinon
        """
        travel_time = cls.calculate_travel_time(origin, destination)
        return travel_time.total_seconds() / 60 >= min_threshold_minutes
    
    @classmethod
    def get_travel_info(
        cls,
        origin: Optional[str],
        destination: Optional[str]
    ) -> Dict[str, any]:
        """
        Retourne des informations détaillées sur le trajet
        
        Args:
            origin: Lieu de départ
            destination: Lieu d'arrivée
        
        Returns:
            Dictionnaire avec les informations du trajet
        """
        travel_time = cls.calculate_travel_time(origin, destination)
        minutes = int(travel_time.total_seconds() / 60)
        
        return {
            "origin": origin,
            "destination": destination,
            "travel_time_minutes": minutes,
            "travel_time": travel_time,
            "needs_buffer": cls.needs_travel_buffer(origin, destination),
            "warning_message": (
                f"Votre trajet entre '{origin}' et '{destination}' prend environ {minutes} min"
                if minutes > 0 else None
            )
        }
    
    @classmethod
    def clear_cache(cls):
        """Vide le cache des temps de trajet"""
        cls._travel_cache.clear()
