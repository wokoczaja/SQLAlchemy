import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/Resources_hawaii.sqlite",connect_args={'check_same_thread':False})

Base=automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement=Base.classes.measurement
Station=Base.classes.station

session=Session(engine)

##weather app
app = Flask(__name__)

import datetime as dt
query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)



@app.route("/")
def home():
    return (f"Welcome to Surf's Up!: Hawaii Climate API<br/>"
        f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date/end date<br/>"
        f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
        )


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station, Station.name).all()
    all_stations=list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitation")
def precipitation():
    results=(session.query(Measurement.date,Measurement.prcp,Measurement.station)
                .filter(Measurement.date>query_date)
                .order_by(Measurement.date).all())
    precipdata = []
    for result in results:
        precipdict={result.date:result.prcp, "Station": result.station}
        precipdata.append(precipdict)
    return jsonify(precipdata)


@app.route("/api/v1.0/tobs")
def tobs():
    last12_tobs=session.query(Measurement.date,Measurement.station,Measurement.tobs).\
                filter(Measurement.date.between('2016-08-24','2017-08-23')).\
                group_by(Measurement.date).order_by(Measurement.date).all()
    tobs_data = []
    for rec in range(len(last12_tobs)):
        tobs_dict = {}
        tobs_dict['date']= last12_tobs[rec][0]
        tobs_dict['temp']= last12_tobs[rec][2]
        tobs_data.append(tobs_dict)
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
  
    min_temp=session.query(func.min(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d",Measurement.date)==start).first()
    avg_temp=session.query(func.avg(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d",Measurement.date)==start).first()
    max_temp=session.query(func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d",Measurement.date)==start).first()
    tobs_data=[min_temp,avg_temp,max_temp]

    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>/<end_date>")
def temp_date_range(start,end_date):
    min_temp=session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date.between(start,end_date)).first()
    avg_temp=session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date.between(start,end_date)).first()
    max_temp=session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date.between(start,end_date)).first()
    tobs_data=[min_temp,avg_temp,max_temp]
    return jsonify(tobs_data)


if __name__== "__main__":
    app.run(debug=True)



