import sqlite3
import json
from position_utils import *
import os

# path = os.path.abspath("quizdb.db")
# path = 'quizdb.db'
path = "quizdb.db"


def get_db_connection():
    db_connection = sqlite3.connect(path) # create a connection
    db_connection.isolation_level = None    # set the sqlite connection in "manual transaction mode"
    return db_connection



def rebuild_database():  # Reconstruire/Écraser la table dans la base de donnée 
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("begin")
        cursor.execute("DROP TABLE IF EXISTS Question;")   # Supprimer la table si elle existe déjà
        cursor.execute("DROP TABLE IF EXISTS Participant;")
        
        cursor.execute("""
            CREATE TABLE Question (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                title TEXT NOT NULL,
                image TEXT,
                position INTEGER,
                possibleAnswers TEXT
            );
        """)
        
        cursor.execute("""
            CREATE TABLE Participant (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playerName TEXT NOT NULL,
                answers TEXT,
                score INTEGER
            );
        """)
        
        connection.commit()
    except Exception as e:
        print(f"Erreur lors de la recréation de la base de données : {e}")
        connection.rollback()
    finally:
        connection.close()


def get_quiz_info():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("begin")
    try:
        cursor.execute("SELECT COUNT(*) FROM Question")
        size = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT playerName, score
            FROM Participant
            ORDER BY score DESC
        """)
        scores = [{"playerName": row[0], "score": row[1]} for row in cursor.fetchall()]
        
        return {"size": size, "scores": scores}, 200
    
    except Exception as e:
        print(f"Erreur lors de la récupération du nombre de questions : {e}")
        return {"error": "Erreur du serveur"}, 500
    finally:
        connection.close()
        





def get_question_by_id(question_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM Question WHERE id = ?", (question_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        # Construire la question au format JSON
        return {
            "id": row[0],
            "text": row[1],
            "title": row[2],
            "image": row[3] if row[5] else None,
            "position": row[4],
            "possibleAnswers": json.loads(row[5]) if row[5] else None
        }
    except Exception as e:
        print(f"Erreur lors de la récupération de la question : {e}")
        return None
    finally:
        connection.close()
        
        
def get_question_by_position(question_position):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM Question WHERE position = ?", (question_position,))
        row = cursor.fetchone()
        if not row:
            return None
        
        # Construire la question au format JSON
        return {
            "id": row[0],
            "text": row[1],
            "title": row[2],
            "image": row[3] if row[5] else None,
            "position": row[4],
            "possibleAnswers": json.loads(row[5]) if row[5] else None
        }
    except Exception as e:
        print(f"Erreur lors de la récupération de la question : {e}")
        return None
    finally:
        connection.close()


def insert_question_to_db(question): 
       
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("begin")
        
        # On vérifie si une question existe déjà à la position spécifiée. Si c'est le cas, on donne la priorité à la dernière question
        # renseignée et on décale toutes les autres 
        check_position(cursor, question)
        
        possible_answers_json = json.dumps(question.possibleAnswers)
        
        cursor.execute("""
            INSERT INTO Question (text, title, image, position, possibleAnswers)
            VALUES (?, ?, ?, ?, ?)
        """, (question.text, question.title, question.image, question.position, possible_answers_json))
        
        question_id = cursor.lastrowid
        cursor.execute("commit")
        return question_id
        
    except Exception as e:
        cursor.execute("rollback")
        print(f"Erreur d'insertion : {e}")
    finally:
        connection.close()


def delete_question_by_id(question_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("begin")

        
        cursor.execute("SELECT position FROM Question WHERE id = ?", (question_id,))
        position = cursor.fetchone()
        if position:
            cursor.execute("UPDATE Question SET position = position - 1 WHERE position > ?", (position[0],))
        
        cursor.execute("DELETE FROM Question WHERE id = ?", (question_id,))
        
        cursor.execute("commit")
        return True
    except Exception as e:
        cursor.execute("rollback")
        print(f"Erreur lors de la suppression de la question : {e}")
        return False
    finally:
        connection.close()
        


def update_question_by_id(question_id, data):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("begin")
    
    new_pos = data.get("position")
    if new_pos:
        cursor.execute("SELECT position FROM Question WHERE id = ?", (question_id,))
        current_pos = cursor.fetchone()

        if not current_pos:
            print(f"Question avec id {question_id} introuvable.")
            cursor.execute("ROLLBACK")
            return False

        current_pos = current_pos[0]

        if new_pos != current_pos:
            reorganize_positions(cursor, current_pos, new_pos)
    
    try:
        # On génère les colonnes à modifier
        columns = []
        values = []

        if "text" in data:
            columns.append("text = ?")
            values.append(data["text"])
        if "title" in data:
            columns.append("title = ?")
            values.append(data["title"])
        if "image" in data:
            columns.append("image = ?")
            values.append(data["image"])
        if "position" in data:
            columns.append("position = ?")
            values.append(data["position"])
        if "possibleAnswers" in data:
            columns.append("possibleAnswers = ?")
            values.append(json.dumps(data["possibleAnswers"]))

        if not columns:
            return False  # Aucun champ à mettre à jour

        # On construit la requête SQL
        values.append(question_id)
        query = f"UPDATE Question SET {', '.join(columns)} WHERE id = ?"
        
        cursor.execute(query, values)
        connection.commit()

        return cursor.rowcount > 0  # Retourne True si une ligne a été affectée
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la question : {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def delete_all_questions():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("begin")
        cursor.execute("DELETE FROM Question;")
        cursor.execute("commit")
        return True
    except Exception as e:
        cursor.execute("rollback")
        print(f"Erreur lors de la suppression de toutes les questions (DB): {e}")
        return False
    finally:
        connection.close()
        


def get_correct_answers():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT possibleAnswers FROM Question")
        return [
            index + 1
            for row in cursor.fetchall()
            for index, answer in enumerate(json.loads(row[0]))
            if answer["isCorrect"]
        ]
    except Exception as e:
        print(f"Erreur lors de la récupération des réponses correctes : {e}")
        raise
    finally:
        connection.close()

        
def insert_participant_to_db(participant):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("BEGIN")

        # Sérialiser les réponses en JSON
        answers_json = json.dumps(participant.answers)
        
        # Insérer le participant dans la base
        cursor.execute("""
            INSERT INTO Participant (playerName, answers, score)
            VALUES (?, ?, ?)
        """, (participant.playerName, answers_json, participant.score))
        
        cursor.execute("COMMIT")
        return True
        
    except ValueError as ve:
        cursor.execute("ROLLBACK")
        print(f"Erreur : {ve}")
        return False
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"Erreur d'insertion : {e}")
        return False
    finally:
        connection.close()

        
        
        
        
        

def delete_all_participations():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("begin")
        cursor.execute("DELETE FROM Participant;")
        cursor.execute("commit")
        return True
    except Exception as e:
        cursor.execute("rollback")
        print(f"Erreur lors de la suppression de toutes les paticipations (DB): {e}")
        return False
    finally:
        connection.close()