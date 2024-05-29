import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Replace with your Google API Key
GOOGLE_API_KEY = 'TEST'

@app.route('/')
def index():
    return render_template('index.html', google_api_key=GOOGLE_API_KEY)

@app.route('/route', methods=['POST'])
def route():
    start = request.form['start']
    destination = request.form['destination']
    service = request.form['service']
    
    # Convert human-readable addresses to lat/lng coordinates
    start_coords = geocode_address(start)
    destination_coords = geocode_address(destination)
    
    if not start_coords or not destination_coords:
        return "Invalid start or destination location. Please try again."
    
    # Find nearby services
    nearby_services = find_nearby_services(start_coords, destination_coords, service)
    
    # Calculate deviation for each service
    deviations = calculate_deviations(start_coords, destination_coords, nearby_services)
    
    # Sort services by deviation
    sorted_services = sorted(deviations, key=lambda x: x['deviation_time'])
    
    return render_template('route.html', start=start, destination=destination, service=service, services=sorted_services, google_api_key=GOOGLE_API_KEY)

def geocode_address(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            location = results[0]['geometry']['location']
            return f"{location['lat']},{location['lng']}"
    return None

def find_nearby_services(origin, destination, service):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={origin}&radius=5000&type=restaurant&keyword={service}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    results = response.json().get('results', [])
    
    services = []
    for result in results:
        place_location = f"{result['geometry']['location']['lat']},{result['geometry']['location']['lng']}"
        place = {
            'name': result['name'],
            'address': result.get('vicinity', 'N/A'),
            'location': place_location,
            'google_map_link': f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={place_location}&travelmode=driving"
        }
        services.append(place)
    return services

def calculate_deviations(start, destination, services):
    deviations = []
    for service in services:
        origin_to_service = calculate_distance_time(start, service['location'])
        service_to_destination = calculate_distance_time(service['location'], destination)
        total_deviation_time = (origin_to_service['duration'] + service_to_destination['duration']) / 60  # convert to minutes
        deviations.append({
            'service': service,
            'deviation_time': total_deviation_time,
            'deviation_distance': (origin_to_service['distance'] + service_to_destination['distance']) / 1000  # convert to kilometers
        })
    return deviations

def calculate_distance_time(origin, destination):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    result = response.json().get('rows', [])[0].get('elements', [])[0]
    
    distance = result['distance']['value']  # in meters
    duration = result['duration']['value']  # in seconds
    
    return {'distance': distance, 'duration': duration}

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change 5001 to any available port number
