CREATE TABLE IF NOT EXISTS {table_name} (
	id SERIAL PRIMARY KEY, 			-- Primary ID key
        place VARCHAR(255) NOT NULL UNIQUE,	-- Name of place 
        geom GEOMETRY(Point, 4326),		-- Point geometry from longitude and latitude coordinates
        opening_hours TEXT,			-- Extracted opening hours from Google Geocoder JSON if available
        full_address TEXT,			-- Full address extracted from Google Geocoder JSON
        street_address VARCHAR(255),		-- Street address extracted from Google Geocoder JSON
        street_name VARCHAR(255),		-- Name of street extracted from Google Geocoder JSON
        street_number VARCHAR(50),		-- Street number extracted from Google Geocoder JSON
        postal_code INTEGER,			-- The postal (ZIP) code extracted from Google Geocoder JSON
        city_municipality VARCHAR(255),		-- City or municipality extracted from Google Geocoder JSON
        region VARCHAR(255),			-- Region of country extracted from Google Geocoder JSON
        country VARCHAR(255),			-- Country where the coordinates is located
        place_id VARCHAR(255),			-- Unique place ID extracted from Google Geocoder JSON
        location_type VARCHAR(255),		-- Additional information about location type (Bar, Museum, ect.)
        description VARCHAR(255),		-- Additional description from the commandline argument parsing
        url TEXT				-- Google maps link used to extract the data
)
