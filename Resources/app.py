import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        "-------------------------"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature Observation for the previous year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
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
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    result = session.query(*sel).all()
    session.close()

    stations = []
    for station, name, latitude, longitude, elevation in result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_dict["Elevation"] = elevation
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent = dt.datetime.strptime(last_date, '%Y-%m-%d')
    qdate = dt.date(recent.year -1, recent.month, recent.day)
    
    sel = [Measurement.date,Measurement.tobs]
    result = session.query(*sel).filter(Measurement.date >= qdate).all()
    session.close()

    tobs_list = []
    
    for date, tobs in result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobs_list = []
    for min,avg,max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>/<stop>')
def stop(start,stop):
    session = Session(engine)
    
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobs_list = []
    for min, avg, max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

if __name__ == "__main__":
    app.run(debug=True)