from flask import Flask
from flask_cors import CORS
from flask import Flask, request, jsonify
import hashlib
import jwt_utils as jwt_utils
from questions import *
from participants import *
from database import *
from auth_utils import require_auth_admin


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


@app.route('/rebuild-db', methods = ['POST'])
@require_auth_admin
def rebuild_database_route():
    try:
        rebuild_database()  # Appelle la fonction de reconstruction
        return "Ok", 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la reconstruction de la base de données : {e}"}), 500
    


@app.route('/quiz-info', methods=['GET'])
def GetQuizInfo():
    size = get_quiz_info()[0]["size"]
    scores = get_quiz_info()[0]["scores"]
    return {"size": size, "scores": scores}, 200



@app.route('/questions', methods=['POST'])
@require_auth_admin
def postQuestion():
    
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
        question_id = insert_question_to_db(question)

        # Convertir en dictionnaire et ajouter l'ID
        question_dict = question.to_dict()
        question_dict["id"] = question_id

        # Retourner la question transformée en JSON
        return question_dict, 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET d'une question par l'id
@app.route('/questions/<int:question_id>', methods=['GET'])
def get_question_by_id_route(question_id):

    try:
        question = get_question_by_id(question_id)
        if not question:
            return jsonify({"error": "Question not found"}), 404
        return jsonify(question), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Modification d'une question par l'id
@app.route('/questions/<int:question_id>', methods=['PUT'])
@require_auth_admin
def update_question_by_id_route(question_id):
    try:
        question = get_question_by_id(question_id) # On vérifie si la question existe
        if not question:
            return jsonify({"error": "Question not found"}), 404

        data = request.get_json() # On récupère les nouvelles données envoyées
        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        
        updated = update_question_by_id(question_id, data) # On met à jour la question avec les nouvelles données
        if updated:
            return jsonify({"message": "Question updated successfully"}), 204
        return jsonify({"error": "Failed to update question"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

# Suppression d'une question par l'id
@app.route('/questions/<int:question_id>', methods=['DELETE'])
@require_auth_admin
def delete_question_by_id_route(question_id):
    try:
        
        question = get_question_by_id(question_id) # On vérifie si la question existe
        if not question:
            return jsonify({"error": "Question not found"}), 404
        
        success = delete_question_by_id(question_id)
        if success:
            return jsonify({"message": "La question a bien été supprimée"}), 204
        return jsonify({"error": "Erreur lors de la suppression de la question"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/questions', methods=['GET'])
def get_question_by_position_route():
    position = request.args.get('position', type=int)  # Récupère le paramètre `position` en tant qu'entier

    if position is None:
        return jsonify({"error": "Le paramètre 'position' est requis"}), 400

    try:
        question = get_question_by_position(position)
        if not question:
            return jsonify({"error": "Aucune question trouvée pour cette position"}), 404
        return jsonify(question), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération de la question : {str(e)}"}), 500



@app.route('/questions/all', methods=['DELETE'])
@require_auth_admin
def delete_all_questions_route():

    try:
        success = delete_all_questions()
        if success:
            return jsonify({"message": "Toutes les questions ont été supprimées avec succès"}), 204
        return jsonify({"error": "Erreur lors de la suppression des questions (route)"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    




@app.route('/participations', methods=['POST'])
def postParticipant():
    
    data = request.get_json()  # Récupération des données JSON
    
    if not data or "playerName" not in data:
        return {"error": "Nom Manquant"}, 400


    try:
        # Charger le participant
        participant = Participant.from_dict(data)

        # Récupérer les réponses correctes depuis la base de données
        correct_answers = get_correct_answers()  # On récupère le tableau correspondant aux réponses correctes
        # Pour chaque ajout de participant, on doit donc récupérer les réponses correctes, ce qui n'est pas forcemment opimal, mais dans
        # notre cas, étant donné que l'on ne dépassera pas les 10 participants, ce n'est pas très grave

        participant.save(correct_answers)
    
        return participant.to_dict(), 200
    
    except ValueError as ve:
        return {"error": str(ve)}, 400
    
    except Exception as e:
        print(f"Erreur dans add_participant : {e}")
        return {"error": "Erreur du serveur"}, 500




@app.route('/participations/all', methods=['DELETE'])
@require_auth_admin
def delete_all_participations_route():
    try:
        success = delete_all_participations()
        if success:
            return jsonify({"message": "Toutes les participations ont été supprimées avec succès"}), 204
        return jsonify({"error": "Erreur lors de la suppression des participations (route)"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500





if __name__ == "__main__":
    app.run()