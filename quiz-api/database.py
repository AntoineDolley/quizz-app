import sqlite3
import json
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
        connection.commit()
        print("Base de données reconstruite avec succès.")
    except Exception as e:
        print(f"Erreur lors de la recréation de la base de données : {e}")
        connection.rollback()
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
    try:
        # Génère dynamiquement les colonnes à mettre à jour
        columns = []
        values = []

        # Ajoute uniquement les champs fournis dans `data`
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

        # Construire la requête SQL
        values.append(question_id)
        query = f"UPDATE Question SET {', '.join(columns)} WHERE id = ?"
        cursor.execute("BEGIN")
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
        
