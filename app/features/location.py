from typing import Dict
from ..schemas import LocationResult


FAKE_GEO_DB = {
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "vadodara": {"lat": 22.3072, "lon": 73.1812},
    "surat": {"lat": 21.1702, "lon": 72.8311},
    "rajkot": {"lat": 22.3039, "lon": 70.8022},
    "gandhinagar": {"lat": 23.2156, "lon": 72.6369},
    "mumbai": {"lat": 19.0760, "lon": 72.8777},
    "delhi": {"lat": 28.7041, "lon": 77.1025},
}


class LocationResolver:
    def resolve(self, entities: Dict[str, str]) -> LocationResult:
        locations: Dict[str, Dict[str, float]] = {}
        for text, label in entities.items():
            if label == "LOCATION":
                key = text.lower()
                locations[text] = FAKE_GEO_DB.get(key, {"lat": 0.0, "lon": 0.0})
        return LocationResult(locations=locations)
