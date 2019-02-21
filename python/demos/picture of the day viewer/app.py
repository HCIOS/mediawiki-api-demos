from flask import Flask, render_template, request, jsonify, redirect
from datetime import date, timedelta
import requests

APP = Flask(__name__)
SESSION = requests.Session()
ENDPOINT = "https://en.wikipedia.org/w/api.php"

current_date = date.today()

@APP.route("/change_date", methods = ["POST"])

def change_date():
    global current_date

    try:
        change_date = request.form["change_date"]

        if (change_date == "← Back"):
            new_date = decrement_date()
        elif (change_date == "Next →"):
            new_date = increment_date()
    except:
        new_date = date.today()

    current_date = new_date

    return redirect("/")

def increment_date():
    return current_date + timedelta(days = 1)

def decrement_date():
    return current_date - timedelta(days = 1)

@APP.route("/", methods = ["GET", "POST"])

def index():
    if (request.method == "POST"):
        date_to_fetch = str(current_date)
        results = fetch_potd(date_to_fetch)

        return jsonify(results = results)

    return render_template("index.html")

def fetch_potd(date):
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "images",
        "titles": "Template:POTD protected/" + date
    }

    response = SESSION.get(url = ENDPOINT, params = params)
    data = response.json()

    try:
        file_name = data["query"]["pages"][0]["images"][0]["title"]
        image_info = fetch_image_info(file_name)
    
        results = [{
            "title": file_name,
            "image": image_info["image_url"],
            "description": image_info["description_url"],
            "date": date
        }]
    except:
        return

    return results

def fetch_image_info(file_name):
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "iiprop": "url",
        "titles": file_name
    }

    response = SESSION.get(url = ENDPOINT, params = params)
    data = response.json()
    page = next(iter(data["query"]["pages"].values()))
    image_info = page["imageinfo"][0]
    image_url = image_info["url"]
    description_url = image_info["descriptionurl"]

    return {"image_url": image_url, "description_url": description_url}

if __name__ == "__main__":
    APP.run()
