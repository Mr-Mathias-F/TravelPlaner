#!/bin/python3

###########################
# Required Python Modules #
###########################

import re			        # For working with regular expressions
import requests			    # Enables HTTP requests
import argparse			    # Parses arguments from the commandline
import urllib.parse		    # For URL parsing and quoting
import configparser		    # For loading and saving config file from previously parsed arguments
import os			        # For interacting with the operating system
import psycopg2			    # PostgreSQL database adapter for Python
from psycopg2 import sql	# For formatting SQL queries

# Configuration file path
config_file = '/etc/TravelPlaner/settings.ini'

# Function to load previously stored settings
def load_settings():
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
        return config['SETTINGS']
    return {}

# Function to save settings
def save_settings(settings):
    config = configparser.ConfigParser()
    config['SETTINGS'] = settings
    with open(config_file, 'w') as configfile:
        config.write(configfile)

# Load previously stored settings
saved_settings = load_settings()

#################################
# Arguments Parsed from the CLI #
#################################

parser = argparse.ArgumentParser(description="Extract Information from Google Maps Link.")
parser.add_argument('link', help='Google Maps link.')												                                        # Positional Argument
parser.add_argument('-a', '--api_key', default=saved_settings.get('api_key'), help='API Key for Google Maps Geocoding API.')			    # Keyword Argument
parser.add_argument('-d', '--dbname', default=saved_settings.get('dbname'), help='Name of PostgreSQL Database to Store Information.')		# Keyword Argument
parser.add_argument('-H', '--host', default=saved_settings.get('host'), help='Name of Host / Address.')						                # Keyword Argument
parser.add_argument('-p', '--port', default=saved_settings.get('port'), help='Port to Host / Address.')						                # Keyword Argument
parser.add_argument('-u', '--user', default=saved_settings.get('user'), help='Name of User Accessing the Database.')				        # Keyword Argument
parser.add_argument('-w', '--password', default=saved_settings.get('password'), help='User password to the Database.')				        # Keyword Argument
parser.add_argument('-T', '--tablename', default=saved_settings.get('tablename'), help='Name of Table to Insert Values into.')			    # Keyword Argument
parser.add_argument('-c', '--comment', help='Add Additional Comment about Location.')								                        # Optional Keyword Argument
parser.add_argument('-t', '--type', help='What Type of Location (Bar, Museum, Restaurant, etc.)')						                    # Optional Keyword Argument

#############################################
# Parse Arguments to the Python Environment #
#############################################

args = parser.parse_args()

# Update settings if new values are introduced
new_settings = {
    'api_key': args.api_key,
    'dbname': args.dbname,
    'host': args.host,
    'port': args.port,
    'user': args.user,
    'password': args.password,
    'tablename': args.tablename
}

# Save the new settings
save_settings(new_settings)

###########################################
# Name of Variables from Parsed Arguments #
###########################################

link = args.link
api = args.api_key
dbname = args.dbname
host = args.host
port = args.port
user = args.user
password = args.password
location_type = args.type
comment = args.comment
table_name = args.tablename

###################################################################
# Extract Coordinates (Latitude, Longitude) from Google Maps Link #
###################################################################

def extract_coordinates(google_maps_url):
    # Use regular expression to find latitude and longitude from Google maps URL
    coordinates_pattern = r'@([-\d\.]+),([-\d\.]+)'
    match = re.search(coordinates_pattern, google_maps_url)
    if match:
        latitude = match.group(1)
        longitude = match.group(2)
        return (latitude, longitude)
    else:
        return None

##############################################
# Extract Address Information from JSON File #
##############################################

def extract_address_component(components, desired_types):
    # Extract address information from Google Geocoding JSON
    for component_type in desired_types:
        for component in components:
            if component_type in component['types']:
                return component['long_name']
    return None

############################################
# Extract Place Name from Google Maps Link #
############################################

def extract_place_name(link):
    # Regular expression pattern to match the place name
    pattern = r'/maps/place/([^/@]+)'
    match = re.search(pattern, link)

    # If a match is found, extract the place name
    if match:
        place_name = match.group(1).replace('+', ' ')
        return place_name
    return None

####################################################
# Extract Geolocation Data from Google Geocode API #
####################################################

def get_geolocation_data(coordinates, api_key):
    api = api_key  
    try:
        # Create Geocoding API URL using parameters
        params = {
            'latlng': f"{coordinates[0]},{coordinates[1]}",
            'key': api
        }
        geocoding_url = 'https://maps.googleapis.com/maps/api/geocode/json'

        response = requests.get(geocoding_url, params=params)
        response.raise_for_status()

        data = response.json()
        if data['status'] == 'OK' and data['results']:
            result = data['results'][0]
            extracted_details = {
                'place_id': result.get('place_id'),
                'formatted_address': result.get('formatted_address'),
                'street_name': extract_address_component(result['address_components'], ['route']),
                'street_number': extract_address_component(result['address_components'], ['street_number']),
                'postal_code': extract_address_component(result['address_components'], ['postal_code']),
                'city_municipality': extract_address_component(result['address_components'], ['administrative_area_level_2', 'administrative_area_level_1']),
                'region': extract_address_component(result['address_components'], ['administrative_area_level_1']),
                'country': extract_address_component(result['address_components'], ['country'])
            }
            extracted_details['street_address'] = f"{extracted_details['street_name']} {extracted_details['street_number']}".strip()
            return extracted_details
        else:
            print('No address information found for the given coordinates.')
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Request error occurred: {err}')
    except Exception as e:
        print(f'An error occurred: {e}')

#################################################################################
# Extract Place Details based on Place ID extracted from 'get_geolocation_data' #
#################################################################################

def get_place_details(geo_information, api_key):
    base_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': geo_information.get('place_id'),
        'fields': 'opening_hours,name',
        'key': api_key
    }
    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print('Error fetching the place details:', response.status_code)
        return None

    data = response.json()

    if data.get('status') != 'OK':
        print('The API did not return a successful status:', data.get('status'))
        return None

# Extract place name
name = extract_place_name(link)
# Extract coordinates
coordinates = extract_coordinates(link)
# Extract geographic information
geo_information = get_geolocation_data(coordinates, api)
# Extract opening hours
opening_hours = get_place_details(geo_information, api)

# Format opening hours if applicable
if opening_hours != None:
    opening_hours = '\n'.join(opening_hours)
else:
    opening_hours

print(f"Place: {urllib.parse.unquote(name)}")
print(f"Latitude: {coordinates[0]}")
print(f"Longitude: {coordinates[1]}")
print(f"Opening hours: \n{opening_hours}")
print(f"Full address: {geo_information['formatted_address']}")
print(f"Street address: {geo_information['street_address']}")
print(f"Street name: {geo_information['street_name']}")
print(f"Street number: {geo_information['street_number']}")
print(f"Postal code: {geo_information['postal_code']}")
print(f"City / Municipality: {geo_information['city_municipality']}")
print(f"Region: {geo_information['region']}")
print(f"Country: {geo_information['country']}")
print(f"Place_id: {geo_information['place_id']}")
print(f"Type: {location_type}")
print(f"Comment: {comment}")
print(f"Link: {link}")


# Connect to PostgreSQL database
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cursor = conn.cursor()

table = sql.SQL("""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        place VARCHAR(255) NOT NULL UNIQUE,
        geom GEOMETRY(Point, 4326),
        opening_hours TEXT,
        full_address TEXT,
        street_address VARCHAR(255),
        street_name VARCHAR(255),
        street_number VARCHAR(50),
        postal_code INTEGER,
        city_municipality VARCHAR(255),
        region VARCHAR(255),
        country VARCHAR(255),
        place_id VARCHAR(255),
        location_type VARCHAR(255),
        description VARCHAR(255),
        url TEXT
    )
    """).format(table_name=sql.Identifier(table_name))

# Execute the create table statement if not already exists
cursor.execute(table)

# Insert statement
insert = sql.SQL("""
    INSERT INTO {table_name} (
        place, geom, opening_hours, full_address,
        street_address, street_name, street_number, postal_code,
        city_municipality, region, country, place_id, location_type,
        description, url
    ) VALUES (
        %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """).format(table_name=sql.Identifier(table_name))

# Data statement
data = (
    urllib.parse.unquote(name),
    coordinates[1],
    coordinates[0],
    opening_hours,
    geo_information['formatted_address'],
    geo_information['street_address'],
    geo_information['street_name'],
    geo_information['street_number'],
    geo_information['postal_code'],
    geo_information['city_municipality'],
    geo_information['region'],
    geo_information['country'],
    geo_information['place_id'],
    location_type,
    comment,
    link
)

# Execute insert statement with data statement
cursor.execute(insert, data)

# Commit to database
conn.commit()

# Close the connection
cursor.close()
conn.close()

print("Data inserted into database successfully.")
