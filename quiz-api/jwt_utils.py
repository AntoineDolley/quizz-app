class JwtError(Exception):
    def __init__(self, message = "Jwt error"):
        self.message = message
        super().__init__(self.message)