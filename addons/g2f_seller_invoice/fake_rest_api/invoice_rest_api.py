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
                "name": request.json['name'],
                "last_name": request.json['last_name'],
                "consumer_address": request.json['consumer_address'],
                "doc_type": request.json['doc_type'],
                "doc_nbr": request.json['doc_nbr'],
                "minigo_code": request.json['minigo_code'],
                "minigo_address": request.json['minigo_address'],
                "origin": request.json['origin'],
                "date": request.json['date'],
                "time": request.json['time'],
                "seller": request.json['seller'],
                "amount_untaxed": request.json['amount_untaxed'],
                "amount_tax": request.json['amount_tax'],
                "amount_total": request.json['amount_total'],
                "items": request.json['items']
        }
    invoices.append(new_invoice)
    return jsonify({'invoices': invoices})


if __name__ == '__main__':
    app.run(debug=True, port=4000)
