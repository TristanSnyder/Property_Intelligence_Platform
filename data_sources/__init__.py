"""
Real data sources integration module
"""
from .census_api import CensusAPI
from .openstreetmap_api import OpenStreetMapAPI
from .google_maps_api import GoogleMapsAPI
from .climate_api import ClimateAPI

__all__ = [
    "CensusAPI",
    "OpenStreetMapAPI", 
    "GoogleMapsAPI",
    "ClimateAPI"
]
