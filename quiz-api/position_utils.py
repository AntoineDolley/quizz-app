def check_position(cursor, question):
    # On vérifie si une question existe déjà à la position spécifiée. Si c'est le cas, on donne la priorité à la dernière question
    # renseignée et on décale toutes les autres 
    free = cursor.execute("SELECT COUNT(*) FROM Question WHERE position = ?", (question.position,)).fetchone()[0]
    if free > 0:  # Si une question existe déjà à cette position
        cursor.execute("UPDATE Question SET position = position + 1 WHERE position >= ?", (question.position,))



def reorganize_positions(cursor, current_position, new_position):
    """
    Réorganise les positions dans la table Question en fonction de la nouvelle position.
    """
    if new_position > current_position:
        # Décaler les positions en diminuant
        cursor.execute(
            "UPDATE Question SET position = position - 1 WHERE position > ? AND position <= ?",
            (current_position, new_position)
        )
    elif new_position < current_position:
        # Décaler les positions en augmentant
        cursor.execute(
            "UPDATE Question SET position = position + 1 WHERE position >= ? AND position < ?",
            (new_position, current_position)
        )
