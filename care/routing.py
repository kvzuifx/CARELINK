import math, requests

def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371  # Radius of Earth in kilometers
    distance = R * c
    return distance


def geocode_location(location_name):
    """
    Convert a location name to latitude and longitude using OpenCage.
    """
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location_name}&key={settings.OPENCAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data['results']:
        coords = data['results'][0]['geometry']
        return coords['lat'], coords['lng']
    else:
        raise ValueError("Location not found")