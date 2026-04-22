import math
from typing import Optional, Tuple

import requests
from flask import current_app

from ..utils import as_float, normalizar_texto


def resolve_coordinates(payload: dict) -> Tuple[Optional[float], Optional[float]]:
    latitude = as_float(payload.get("latitude"))
    longitude = as_float(payload.get("longitude"))
    if latitude is not None and longitude is not None:
        return latitude, longitude

    if current_app.config.get("LOCATION_PROVIDER") != "regional":
        return None, None

    api_url = current_app.config.get("REGIONAL_GEO_API_URL")
    if not api_url:
        return None, None

    params = {
        "address": normalizar_texto(payload.get("endereco")),
        "city": normalizar_texto(payload.get("cidade")),
        "state": normalizar_texto(payload.get("estado")),
        "zip_code": normalizar_texto(payload.get("cep")),
    }
    headers = {}
    if current_app.config.get("REGIONAL_API_KEY"):
        headers["Authorization"] = f"Bearer {current_app.config['REGIONAL_API_KEY']}"

    try:
        response = requests.get(
            api_url,
            params=params,
            headers=headers,
            timeout=current_app.config.get("REQUEST_TIMEOUT", 10),
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None, None

    latitude = as_float(data.get("latitude"))
    longitude = as_float(data.get("longitude"))

    nested_data = data.get("data")
    if (latitude is None or longitude is None) and isinstance(nested_data, dict):
        latitude = as_float(nested_data.get("latitude"))
        longitude = as_float(nested_data.get("longitude"))

    return latitude, longitude


def calculate_distance_km(
    origem_latitude: Optional[float],
    origem_longitude: Optional[float],
    destino_latitude: Optional[float],
    destino_longitude: Optional[float],
) -> Optional[float]:
    if None in {origem_latitude, origem_longitude, destino_latitude, destino_longitude}:
        return None

    distancia_api = _calculate_distance_via_regional_api(
        origem_latitude,
        origem_longitude,
        destino_latitude,
        destino_longitude,
    )
    if distancia_api is not None:
        return distancia_api

    return _haversine_km(origem_latitude, origem_longitude, destino_latitude, destino_longitude)


def _calculate_distance_via_regional_api(
    origem_latitude: float,
    origem_longitude: float,
    destino_latitude: float,
    destino_longitude: float,
) -> Optional[float]:
    if current_app.config.get("LOCATION_PROVIDER") != "regional":
        return None

    api_url = current_app.config.get("REGIONAL_DISTANCE_API_URL")
    if not api_url:
        return None

    params = {
        "origin_lat": origem_latitude,
        "origin_lng": origem_longitude,
        "destination_lat": destino_latitude,
        "destination_lng": destino_longitude,
    }
    headers = {}
    if current_app.config.get("REGIONAL_API_KEY"):
        headers["Authorization"] = f"Bearer {current_app.config['REGIONAL_API_KEY']}"

    try:
        response = requests.get(
            api_url,
            params=params,
            headers=headers,
            timeout=current_app.config.get("REQUEST_TIMEOUT", 10),
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    distancia = as_float(data.get("distance_km"))
    nested_data = data.get("data")
    if distancia is None and isinstance(nested_data, dict):
        distancia = as_float(nested_data.get("distance_km"))

    return distancia


def _haversine_km(
    origem_latitude: float,
    origem_longitude: float,
    destino_latitude: float,
    destino_longitude: float,
) -> float:
    raio_terra_km = 6371.0

    lat1 = math.radians(origem_latitude)
    lon1 = math.radians(origem_longitude)
    lat2 = math.radians(destino_latitude)
    lon2 = math.radians(destino_longitude)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return raio_terra_km * c
