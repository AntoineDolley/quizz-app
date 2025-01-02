from typing import List, Dict, Any
from database import insert_participant_to_db

class Participant: 
    def __init__(self, playerName: str, answers: List[str] = None, score: int = 0):
        self.playerName = playerName
        self.answers = answers
        self.score = score

    def to_dict(self):
        return {
            "playerName": self.playerName,
            "answers": self.answers,
            "score": self.score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Participant":
        return cls(
            playerName = data["playerName"],
            answers = data.get("answers"),
            score = data.get("score", 0)
        )
        
    
    def calculate_score(self, correct_answers):
        self.score = sum(1 for user_answer, correct_answer in zip(self.answers, correct_answers) if user_answer == correct_answer)
        return self.score    
    
    
    def validate_answers(self, correct_answers_count: int):
        if len(self.answers) != correct_answers_count:
            raise ValueError("Le nombre de réponsses n'est pas correct")
    
        
    def save(self, correct_answers):
        self.validate_answers(len(correct_answers))
        self.calculate_score(correct_answers)
        return insert_participant_to_db(self)