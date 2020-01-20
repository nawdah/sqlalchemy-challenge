import datetime as dt 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station 

app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"Welcome to my API! Here are the routes available:<br/k>"
        f"Precipitation: /api/v1.0/precipitation<br/k>"
        f"List of Stations: /api/v1.0/stations<br/k>"
        f"Temperature Observation for one year: /api/v1.0/tobs<br/>"
        f"Temperature statistics from start date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/k>"
        f"Temperature statistics from start to end dates (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    sel = [Measurement.date, Measurement.prcp]

    result = session.query(*sel).all()

    session.close()

    precipitation = []

    for date, prcp in result:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]

    result = session.query(*sel).all()

    session.close()

    stations = []
    for station, name, latitude, longitude, elevation in result:
        stations_dict = {}
        stations_dict["Station"] = station
        stations_dict["Name"] = name
        stations_dict["Latitude"] = latitude
        stations_dict["Longitude"] = longitude
        stations_dict["Elevation"] = elevation
        stations.append(stations_dict)
    
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).filter()[0]
    date_converted = dt.datetime(date_str, '%Y-%m-%d')
    date_query = dt.date(date_converted.year -1 , date_converted.month, date_converted.day)

    sel = [Measurement.date, Measurement.tobs]

    result = session.query(*sel).filter(Measurement.date >= date_query).all()

    session.close()

    tobs = []
    for date, tobs in result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["TOBs"] = tobs
        tobs.append(tobs_dict)
    
    return jsonify(tobs)

@app.route('/api/v1.0/<start>')
def begin(start):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    tobs = []
    for min, avg, max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs.append(tobs_dict)
    
    return jsonify(tobs)

@app.route('/api/v1.0/<start>/<stop>')
def end(start, stop):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()

    session.close()

    tobs = []
    for min, avg, max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs.append(tobs_dict)
    
    return jsonify(tobs)


if __name__ == '__main__':
    app.run(debug=True)
