from flask import Flask, Response, render_template, redirect, request, jsonify
import datetime
import json
from math import floor
from model import Model
from slugify import slugify
import os

app = Flask(__name__, )

data_file = "/var/www/foodtime/data.json"

def loadData(f=data_file):
    with open(f, "r") as file:
        return json.load(file)

def saveData(obj, f=data_file):
    with open(f, "w") as file:
        json.dump(obj, file, sort_keys=False, indent=4)

def time_to_index(x):
    return x.hour * 4 + floor(x.minute / 15)

@app.route("/")
def root():
    data = loadData()
    return render_template("index.html", data=data)

@app.route("/dev")
def dev():
    data = loadData()
    return render_template("dev.html", data=data)

@app.route("/update", methods=["post"])
def update():
    location = request.json['location']
    macs = request.json['macs']
    time_offset = request.json['time_offset']
    post_number = request.json['post_number']
    number_of_posts = request.json['number_of_posts']
    post_type = request.json['post_type']

    data = loadData()
    update_time = (datetime.datetime.now()+datetime.timedelta(hours=int(data['locations'][location]['time_offset'])))
    if (post_type == "clear"):
        data['locations'][location]['macs'] = []
    data['locations'][location]['macs'] += macs
    data['locations'][location]['time_offset'] = int(time_offset)
    data['locations'][location]['last_updated'] = update_time.strftime("%A, %B %d, %Y at %I:%M %p")
    saveData(data)

    if (post_number == number_of_posts):
        m = Model(bins=96, parsing_function=time_to_index)
        model_file = f"models/{slugify(location, separator='_')}_model.json"
        if (not os.path.exists(model_file)):
            m.save(model_file)
        else:
            m.load(model_file)
        m.train(update_time, len(data['locations'][location]['macs']))
        m.save(model_file)
    
    return Response(response="POST Request Successful\n\nRequest data: {}".format(request.data), status=200)

@app.route("/predict")
def predict():
    model_file = f"models/{slugify(request.args.get('location'), separator='_')}_model.json"
    if (os.path.exists(model_file)):
        m = Model()
        m.load(model_file)
        res = jsonify(m.predict(int(request.args.get('index'))))
        return res
    else:
        return Response(response="Model does not exist", status=400)

@app.route("/predictall")
def predictall():
    model_file = f"models/{slugify(request.args.get('location'), separator='_')}_model.json"
    if (os.path.exists(model_file)):
        m = Model()
        m.load(model_file)
        res = jsonify(m.predictall())
        return res
    else:
        return Response(response="Model does not exist", status=400)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)