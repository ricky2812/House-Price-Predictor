from flask import Flask, request, jsonify
import util


app = Flask(__name__)

@app.route('/get_location_names', methods=['GET', 'POST'])
def get_location_names():
    city = request.form['city']

    response = jsonify({
        'locations': util.get_location_names(city)
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/predict_home_price', methods=['POST', 'GET'])
def predict_home_price():
    city = request.form['city']
    total_sqft = float(request.form['total_sqft'])
    location = request.form['location']
    bhk = int(request.form['bhk'])

    response = jsonify({
        'estimated_price': util.get_estimated_price(city,location, total_sqft, bhk)
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route('/get_city_names', methods=['GET'])
def get_City_names():
    response = jsonify({
        'city': util.get_city_names()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == '__main__':
    #starting server in debug mode
    print('Starting server...')
    app.run()
    # app.run()