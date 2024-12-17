# import sqlite3

# DATABASE_NAME = "quiz.db"

# def init_db():
#     """
#     Initialise la base de données SQLite3 et crée les tables nécessaires.
#     """
#     with sqlite3.connect(DATABASE_NAME) as conn:
#         cursor = conn.cursor()

#         # Création de la table des questions
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS quiz_question (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 position INTEGER NOT NULL,
#                 title TEXT NOT NULL,
#                 text TEXT NOT NULL,
#                 image TEXT
#             )
#         """)

#         # Création de la table des réponses possibles
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS quiz_answer (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 text TEXT NOT NULL,
#                 is_correct BOOLEAN NOT NULL,
#                 question_id INTEGER NOT NULL,
#                 FOREIGN KEY (question_id) REFERENCES quiz_question (id)
#             )
#         """)

#         conn.commit()

# def get_db_connection():
#     """
#     Retourne une connexion SQLite3.
#     """
#     return sqlite3.connect(DATABASE_NAME)
