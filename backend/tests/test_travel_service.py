"""
Tests pour le service de calcul des temps de trajet
"""

import pytest
from datetime import timedelta
from backend.services.travel_service import TravelService


class TestTravelService:
    """Tests pour TravelService"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        TravelService.clear_cache()
    
    def test_same_location_zero_travel_time(self):
        """Test: même lieu = pas de déplacement"""
        travel_time = TravelService.calculate_travel_time(
            "123 Main St, Paris",
            "123 Main St, Paris"
        )
        assert travel_time == timedelta(minutes=0)
    
    def test_none_location_zero_travel_time(self):
        """Test: lieu manquant = pas de déplacement"""
        travel_time = TravelService.calculate_travel_time(None, "123 Main St")
        assert travel_time == timedelta(minutes=0)
        
        travel_time = TravelService.calculate_travel_time("123 Main St", None)
        assert travel_time == timedelta(minutes=0)
    
    def test_same_building_travel_time(self):
        """Test: même bâtiment = 5 minutes"""
        travel_time = TravelService.calculate_travel_time(
            "123 Main St, Bureau 101, Paris",
            "123 Main St, Bureau 205, Paris"
        )
        assert travel_time == timedelta(minutes=5)
    
    def test_same_neighborhood_travel_time(self):
        """Test: même quartier = 15 minutes"""
        travel_time = TravelService.calculate_travel_time(
            "10 Rue A, 5ème arrondissement, Paris",
            "25 Rue B, 5ème arrondissement, Paris"
        )
        assert travel_time == timedelta(minutes=15)
    
    def test_same_city_travel_time(self):
        """Test: même ville = 30 minutes"""
        travel_time = TravelService.calculate_travel_time(
            "10 Rue A, 1er arrondissement, Paris",
            "25 Rue B, 15ème arrondissement, Paris"
        )
        assert travel_time == timedelta(minutes=30)
    
    def test_different_city_travel_time(self):
        """Test: villes différentes = 60 minutes"""
        travel_time = TravelService.calculate_travel_time(
            "123 Main St, Paris",
            "456 Avenue, Lyon"
        )
        assert travel_time == timedelta(minutes=60)
    
    def test_normalize_location(self):
        """Test: normalisation des lieux"""
        loc1 = TravelService._normalize_location("  123   Main   St  ")
        loc2 = TravelService._normalize_location("123 main st")
        assert loc1 == loc2 == "123 main st"
    
    def test_needs_travel_buffer(self):
        """Test: détection du besoin de buffer"""
        # Trajet court (5 min) - pas de buffer nécessaire par défaut
        needs_buffer = TravelService.needs_travel_buffer(
            "123 Main St, Bureau 101, Paris",
            "123 Main St, Bureau 205, Paris"
        )
        assert not needs_buffer
        
        # Trajet long (30 min) - buffer nécessaire
        needs_buffer = TravelService.needs_travel_buffer(
            "10 Rue A, 1er arrondissement, Paris",
            "25 Rue B, 15ème arrondissement, Paris"
        )
        assert needs_buffer
    
    def test_get_travel_info(self):
        """Test: informations complètes du trajet"""
        info = TravelService.get_travel_info(
            "123 Main St, Paris",
            "456 Avenue, Lyon"
        )
        
        assert info["origin"] == "123 Main St, Paris"
        assert info["destination"] == "456 Avenue, Lyon"
        assert info["travel_time_minutes"] == 60
        assert info["needs_buffer"] is True
        assert "60 min" in info["warning_message"]
    
    def test_cache_mechanism(self):
        """Test: mécanisme de cache"""
        # Premier appel
        travel_time1 = TravelService.calculate_travel_time(
            "Location A",
            "Location B"
        )
        
        # Deuxième appel (devrait utiliser le cache)
        travel_time2 = TravelService.calculate_travel_time(
            "Location A",
            "Location B"
        )
        
        assert travel_time1 == travel_time2
        
        # Vérifier que le cache contient l'entrée
        cache_key = ("location a", "location b")
        assert cache_key in TravelService._travel_cache
        
        # Vider le cache
        TravelService.clear_cache()
        assert len(TravelService._travel_cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
