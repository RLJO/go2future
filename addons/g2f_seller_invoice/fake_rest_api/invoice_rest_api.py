from flask import Flask, jsonify, request

app = Flask(__name__)

from invoices import invoices

# Testing Route
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'response': 'pong!'})

#INVOICES
# Get Data Routes
@app.route('/invoices')
def getInvoices():
    return jsonify({'invoices': invoices})

# Create Data Routes
@app.route('/invoices', methods=['POST'])
def addInvoices():
    new_invoice = {
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
    invoices.append(new_invoice)
    return jsonify({'invoices': invoices})

if __name__ == '__main__':
    app.run(debug=True, port=4000)
