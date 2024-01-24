# Import the dependencies.

import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with = engine)

# Save references to each table
measurements = base.classes.measurement
stations = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#Convert the precipitation data to a dictionary

@app.route('/')
def home():
    return "Welcome to the Climate API! Available routes: /api/v1.0/stations, /api/v1.0/temperature, /api/v1.0/precipitation, /api/v1.0/start, /api/v1.0/start/end, Use Year-month-day format for date"
    
    
@app.route('/api/v1.0/routes')
def list_routes():
    routes = [
        {'url': '/api/v1.0/stations', 'description': 'List all stations'},
        {'url': '/api/v1.0/temperature', 'description': 'Temperature data for the most active station'},
        {'url': '/api/v1.0/precipitation', 'description': 'Precipitation data for the last 12 months'},
        {'url': '/api/v1.0/<start>', 'description': 'Temperature data for dates >= start date'},
        {'url': '/api/v1.0/<start>/<end>', 'description': 'Temperature data from start to end date Min, Max and Average'},
    ]
    return jsonify({'routes': routes})

@app.route('/api/v1.0/stations')
def get_all_stations():
    # Query and return all stations
    all_stations = session.query(stations.station).all()
    return jsonify({'stations': [station[0] for station in all_stations]})

@app.route('/api/v1.0/temperature')
def get_temperature_data():
    # The most_active_station_id
    most_active_station_id = 'USC00519281'

  # Query temperature data for the most active station
    temperature_data = session.query(measurements.date, measurements.tobs).\
        filter(measurements.station == most_active_station_id).all()

    return jsonify({'temperature_data':[temperature[1] for temperature in temperature_data]})

@app.route('/api/v1.0/precipitation')
def get_precipitation_data():
    # Calculate the date one year from the last date in the dataset
    year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(measurements.date, measurements.prcp).\
        filter(measurements.date >= year_date).all()

    precip = {date: precipitation for date, precipitation in precipitation_data}
    return jsonify(precip)


#----------------------------------------------------------------------------------------

@app.route('/api/v1.0/<start>')
def get_temperature_stats_start(start):
    # Query temperature statistics for a specified start date
    temperature_stats = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
        filter(measurements.date >= start).all()

    return jsonify({
        'start_date': start,
        'temperature_stats': {
            'min_temperature': temperature_stats[0][0],
            'avg_temperature': temperature_stats[0][1],
            'max_temperature': temperature_stats[0][2]
        }
    })

@app.route('/api/v1.0/<start>/<end>')
def get_temperature_stats_range(start, end):
    # Query temperature statistics for a specified start-end range
    temperature_stats_range = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
        filter(measurements.date >= start, measurements.date <= end).all()

    return jsonify({
        'start_date': start,
        'end_date': end,
        'temperature_stats_range': {
            'min_temperature': temperature_stats_range[0][0],
            'avg_temperature': temperature_stats_range[0][1],
            'max_temperature': temperature_stats_range[0][2]
        }
    })

if __name__ == '__main__':
    app.run()
