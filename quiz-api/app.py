from flask import Flask
from flask_cors import CORS
from flask import Flask, request, jsonify
import hashlib
import jwt_utils
from questions import *


app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
	x = 'world'
	return f"Hello, {x}"

@app.route('/login', methods=['POST'])
def login():
    payload = request.get_json()
    tried_password = payload['password'].encode('UTF-8')
    hashed = hashlib.md5(tried_password).digest()
    if hashed == b'\xd8\x17\x06PG\x92\x93\xc1.\x02\x01\xe5\xfd\xf4_@' :

        return {'token': jwt_utils.build_token()}, 200
    return 'Unauthorized', 401
   

@app.route('/quiz-info', methods=['GET'])
def GetQuizInfo():
	return {"size": 0, "scores": []}, 200


@app.route('/questions', methods=['POST'])
def postQuestion():
    
    token = request.headers.get('Authorization').split(" ")[1]

    try:
        jwt_utils.decode_token(token)  # Décoder le token
    except jwt_utils.JwtError as e:
        return jsonify({"error": str(e)}), 401
    
    data = request.get_json()  # Récupération des données JSON
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    try:
        # Création de l'objet Question
        question = Question(
            text = data["text"],
            title = data["title"],
            image = data["image"],
            position = data["position"],
            possibleAnswers = data["possibleAnswers"]
        )
        
        # Retourner la question transformée en JSON
        return question.to_dict(), 200
        # return question, 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run()