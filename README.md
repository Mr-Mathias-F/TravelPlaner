# Setup

```
git clone https://github.com/Mr-Mathias-F/TravelPlaner.git
sudo bash setup.sh
```

# Required Python modules

The modules below is required to run the command-line tool or `.py` script:

```
pip install requests
pip install psycopg2-binary
```

# Required PostgreSQL extension

A PostgreSQL database with the PostGIS extension installed and enabled is required to store the geospatial data extracted from the Google Maps link.

```
CREATE EXTENSION postgis;
```

The SQL schema used to store the extracted data is found in the `SQL_Schema` folder (also included in `TravelPlaner`)

# How to use

From `TravelPlaner --help`:

```
Extract Information from Google Maps Link.

positional arguments:
  link                  Google Maps link.

options:
  -h, --help            show this help message and exit
  -a API_KEY, --api_key API_KEY
                        API Key for Google Maps Geocoding API.
  -d DBNAME, --dbname DBNAME
                        Name of PostgreSQL Database to Store Information.
  -H HOST, --host HOST  Name of Host / Address.
  -p PORT, --port PORT  Port to Host / Address.
  -u USER, --user USER  Name of User Accessing the Database.
  -w PASSWORD, --password PASSWORD
                        User password to the Database.
  -T TABLENAME, --tablename TABLENAME
                        Name of Table to Insert Values into.
  -c COMMENT, --comment COMMENT
                        Add Additional Comment about Location.
  -t TYPE, --type TYPE  What Type of Location (Bar, Museum, Restaurant, etc.)
```
Information about `-a, --api_key`, `-d, --dbname`, `-H, --host`, `-p, --port`, `-u, --user`, `-w, --password`, `-T, --tablename` will be stored in the `settings.ini` file located in the `/etc/TravelPlaner/` directory.
