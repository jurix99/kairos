"""
Service pour calculer les temps de trajet entre deux lieux
"""

from datetime import timedelta
from typing import Optional, Dict, Tuple, Literal
import re
import logging
import httpx

logger = logging.getLogger(__name__)


class TravelService:
    """
    Service pour estimer les temps de trajet entre différents lieux.
    Supporte à la fois des estimations heuristiques et des calculs via API.
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
    
    def __init__(
        self,
        api_provider: Optional[Literal["google", "mapbox", "openroute"]] = None,
        api_key: Optional[str] = None,
        use_api: bool = False
    ):
        """
        Initialise le service de calcul de temps de trajet
        
        Args:
            api_provider: Fournisseur d'API ("google", "mapbox", "openroute")
            api_key: Clé API pour le fournisseur choisi
            use_api: Si True, utilise l'API pour les calculs (avec fallback heuristique)
        """
        self.api_provider = api_provider
        self.api_key = api_key
        self.use_api = use_api and api_provider and api_key
    
    def calculate_travel_time(
        self,
        origin: Optional[str],
        destination: Optional[str],
        use_api: Optional[bool] = None
    ) -> timedelta:
        """
        Calcule le temps de trajet estimé entre deux lieux
        
        Args:
            origin: Lieu de départ (peut être None)
            destination: Lieu d'arrivée (peut être None)
            use_api: Si spécifié, force l'utilisation (ou non) de l'API
        
        Returns:
            timedelta représentant le temps de trajet estimé
        """
        # Si l'un des deux lieux est manquant, retourner 0
        if not origin or not destination:
            return timedelta(minutes=0)
        
        # Normaliser les adresses
        origin_norm = self._normalize_location(origin)
        destination_norm = self._normalize_location(destination)
        
        # Même lieu = pas de déplacement
        if origin_norm == destination_norm:
            return timedelta(minutes=0)
        
        # Vérifier le cache
        cache_key = (origin_norm, destination_norm)
        if cache_key in self._travel_cache:
            return self._travel_cache[cache_key]
        
        # Déterminer si on utilise l'API
        should_use_api = use_api if use_api is not None else self.use_api
        
        # Essayer d'abord l'API si activée
        if should_use_api:
            try:
                travel_time = self._calculate_via_api(origin, destination)
                if travel_time:
                    # Mettre en cache
                    self._travel_cache[cache_key] = travel_time
                    return travel_time
                else:
                    logger.warning(f"API returned no result, falling back to heuristics")
            except Exception as e:
                logger.error(f"Error calculating travel time via API: {e}, falling back to heuristics")
        
        # Fallback sur les heuristiques
        travel_time = self._estimate_travel_time(origin_norm, destination_norm)
        
        # Mettre en cache
        self._travel_cache[cache_key] = travel_time
        
        return travel_time
    
    def _calculate_via_api(
        self,
        origin: str,
        destination: str
    ) -> Optional[timedelta]:
        """
        Calcule le temps de trajet via une API externe
        
        Args:
            origin: Lieu de départ
            destination: Lieu d'arrivée
        
        Returns:
            timedelta représentant le temps de trajet, ou None si échec
        """
        if not self.api_provider or not self.api_key:
            return None
        
        try:
            if self.api_provider == "google":
                return self._google_maps_api(origin, destination)
            elif self.api_provider == "mapbox":
                return self._mapbox_api(origin, destination)
            elif self.api_provider == "openroute":
                return self._openroute_api(origin, destination)
            else:
                logger.error(f"Unknown API provider: {self.api_provider}")
                return None
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return None
    
    def _google_maps_api(
        self,
        origin: str,
        destination: str
    ) -> Optional[timedelta]:
        """
        Calcule via Google Maps Distance Matrix API
        
        Args:
            origin: Lieu de départ
            destination: Lieu d'arrivée
        
        Returns:
            timedelta ou None si échec
        """
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": "driving",
            "key": self.api_key
        }
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "OK":
                rows = data.get("rows", [])
                if rows and rows[0].get("elements"):
                    element = rows[0]["elements"][0]
                    if element.get("status") == "OK":
                        duration_seconds = element.get("duration", {}).get("value", 0)
                        return timedelta(seconds=duration_seconds)
        
        return None
    
    def _mapbox_api(
        self,
        origin: str,
        destination: str
    ) -> Optional[timedelta]:
        """
        Calcule via Mapbox Directions API
        
        Note: Nécessite des coordonnées. Pour MVP, on pourrait d'abord géocoder.
        
        Args:
            origin: Lieu de départ
            destination: Lieu d'arrivée
        
        Returns:
            timedelta ou None si échec
        """
        # Pour Mapbox, il faut d'abord géocoder les adresses
        # Implémentation simplifiée - en production, ajouter le géocodage
        logger.info("Mapbox API requires geocoding - not fully implemented yet")
        return None
    
    def _openroute_api(
        self,
        origin: str,
        destination: str
    ) -> Optional[timedelta]:
        """
        Calcule via OpenRouteService API
        
        Note: Nécessite des coordonnées. Pour MVP, on pourrait d'abord géocoder.
        
        Args:
            origin: Lieu de départ
            destination: Lieu d'arrivée
        
        Returns:
            timedelta ou None si échec
        """
        # Pour OpenRouteService, il faut d'abord géocoder les adresses
        # Implémentation simplifiée - en production, ajouter le géocodage
        logger.info("OpenRouteService API requires geocoding - not fully implemented yet")
        return None
    
    @staticmethod
    def _normalize_location(location: str) -> str:
        """
        Normalise un lieu pour la comparaison
        
        Args:
            location: Lieu à normaliser
        
        Returns:
            Lieu normalisé (minuscules, sans espaces superflus)
        """
        return re.sub(r'\s+', ' ', location.lower().strip())
    
    @staticmethod
    def _estimate_travel_time(origin: str, destination: str) -> timedelta:
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
                return timedelta(minutes=TravelService.DEFAULT_TRAVEL_TIMES["same_building"])
        
        # Même quartier/arrondissement
        if len(origin_parts) >= 3 and len(dest_parts) >= 3:
            if origin_parts[-2].strip() == dest_parts[-2].strip():
                return timedelta(minutes=TravelService.DEFAULT_TRAVEL_TIMES["same_neighborhood"])
        
        # Même ville
        if len(origin_parts) >= 2 and len(dest_parts) >= 2:
            if origin_parts[-1].strip() == dest_parts[-1].strip():
                return timedelta(minutes=TravelService.DEFAULT_TRAVEL_TIMES["same_city"])
        
        # Villes différentes
        return timedelta(minutes=TravelService.DEFAULT_TRAVEL_TIMES["different_city"])
    
    def needs_travel_buffer(
        self,
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
        travel_time = self.calculate_travel_time(origin, destination)
        return travel_time.total_seconds() / 60 >= min_threshold_minutes
    
    def get_travel_info(
        self,
        origin: Optional[str],
        destination: Optional[str],
        use_api: Optional[bool] = None
    ) -> Dict[str, any]:
        """
        Retourne des informations détaillées sur le trajet
        
        Args:
            origin: Lieu de départ
            destination: Lieu d'arrivée
            use_api: Si spécifié, force l'utilisation (ou non) de l'API
        
        Returns:
            Dictionnaire avec les informations du trajet
        """
        travel_time = self.calculate_travel_time(origin, destination, use_api=use_api)
        minutes = int(travel_time.total_seconds() / 60)
        
        return {
            "origin": origin,
            "destination": destination,
            "travel_time_minutes": minutes,
            "travel_time": travel_time,
            "needs_buffer": self.needs_travel_buffer(origin, destination),
            "method": "api" if (use_api if use_api is not None else self.use_api) else "heuristic",
            "warning_message": (
                f"Votre trajet entre '{origin}' et '{destination}' prend environ {minutes} min"
                if minutes > 0 else None
            )
        }
    
    @classmethod
    def clear_cache(cls):
        """Vide le cache des temps de trajet"""
        cls._travel_cache.clear()
