# Required imports
import os
import time

from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, request

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
drug_ref = db.collection('drugs')


# @app.route('/time')
# def get_current_time():
#     return {'time': time.time()}

all_drugs = {}

@app.route('/test', methods=['GET'])
def test():
    print(next(drug_ref.list_documents()).id)

    return jsonify({"success": True}), 200

@app.route('/compare', methods=['GET'])
def compare():
    """
        compare() : Given a list of drug_ids, check all interactions with other drugs within the list.
        Output ->
    """
    drug_ls = ['Hq6TB7KrkqF2ezXXRlrw', 'IdgTjrNPKVftpEnN1fSO',
               's9D1I7JvKXVA8n8P1BUC', 'fy8pUCzK9uybjP5xJokm',
               'jL1hQWqqAzzss6jV6dPl', 'lCNKpmGQCWNzB9XI533b',
               'lYMiJ1e7qN19km0KXvIX', 'tgO3zwJq7AcMaAn1JPay']
    
    interactions = []

    try:
        all_drugs = {doc.id: doc.to_dict() for doc in drug_ref.stream()}
    except Exception as e:
        return f"An Error Occurred: {e}"
    
    print(all_drugs)

    # go through all chosen drugs
    for i in range(len(drug_ls)-1):
        # go through all interactions for that drug
        for interaction in all_drugs[drug_ls[i]]['interactions']:
            # go through all remaining drugs to check for interactions
            for j in range(i+1, len(drug_ls)-1):
                if all_drugs[drug_ls[j]]['name'].lower() in interaction['name'].lower():
                    interactions.append(f'{all_drugs[drug_ls[i]]["name"]} and {all_drugs[drug_ls[j]]["name"]} ({interaction["severity"].upper()}) : {interaction["effect"]}')
    return interactions
    # return jsonify({"success": True}), 200




@app.route('/add', methods=['GET'])
def create():
    """
        create() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'drug_name': '1', 'title': 'Write a blog post'}
    """
    my_json = {'names': ['Dorprin', 'Durlaza'],
            'description': 'a nonsteroidal anti-inflammatory drug used to reduce pain, fever, and/or inflammation, and as an antithrombotic.'}
    try:
        # drug_name = request.json['drug_name']
        drug_name = 'aspirin'
        drug_ref.document(drug_name).set(my_json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"


@app.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON.
        drug : Return document that matches query ID.
        all_todos : Return all documents.
    """
    try:
        # Check if ID was passed to URL query
        drug_name = request.args.get('name')
        if drug_name:
            drug = drug_ref.document(drug_name).get()
            return jsonify(drug.to_dict()), 200
        else:
            all_drugs = [doc.to_dict() for doc in drug_ref.stream()]
            return jsonify(all_drugs), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/update', methods=['POST', 'PUT'])
def update():
    """
        update() : Update document in Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'drug_name': '1', 'title': 'Write a blog post today'}
    """
    try:
        drug_name = request.json['drug_name']
        drug_ref.document(drug_name).update(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    """
        delete() : Delete a document from Firestore collection.
    """
    try:
        # Check for ID in URL query
        drug_name = request.args.get('drug_name')
        drug_ref.document(drug_name).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"


port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
