from flask import Flask, jsonify, request

app = Flask(__name__)

from orders import orders

# Testing Route
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'response': 'pong!'})

#INVOICES
# Get Data Routes
@app.route('/orders')
def getOrders():
    return jsonify({'orders': orders})

# Create Data Routes
@app.route('/orders', methods=['POST'])
def addOrders():
    new_order = {
		"id": request.json['id'],
		"name": request.json['name'],
		"last_name": request.json['last_name'],
		"consumer_address": request.json['consumer_address'],
		"dni_cuit": request.json['dni'],
		"minigo_address": request.json['minigo_address'],
		"date": request.json['date'],
		"time": request.json['time'],
		"items": request.json['items']
	}    
    orders.append(new_order)
    return jsonify({'orders': orders})    

if __name__ == '__main__':
    app.run(debug=True, port=4000)
