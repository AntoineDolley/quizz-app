from typing import List, Dict, Any

class Question:
    
    _id_counter = 1
    
    def __init__(self, text: str, title: str, image: str = None, position: int = None, possibleAnswers: List[str] = None):
        self.id = Question._id_counter
        Question._id_counter += 1
        self.text = text
        self.title = title
        self.image = image
        self.position = position
        self.possibleAnswers = possibleAnswers

    def to_dict(self):
        return {
            "id" : self.id,
            "text": self.text,
            "title": self.title,
            "image": self.image,
            "position": self.position,
            "possibleAnswers": self.possibleAnswers
        }
        
    def from_dict(cls, data: Dict[str, Any]) -> "Question":
        return cls(
            text=data["text"],
            title=data["title"],
            image=data.get("image"),
            position=data.get("position"),
            possibleAnswers=data.get("possibleAnswers"),
            id=data.get("id")
        )