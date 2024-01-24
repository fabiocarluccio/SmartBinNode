import json
from datetime import datetime

class Disposal:
    def __init__(self, binId, token, type, weight, position):
        self.binId = binId
        self.token = token
        self.type = type
        self.weight = weight
        self.timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.position = position

    def to_json(self):
        data = {
            "bin_id": self.binId,
            "token": self.token,
            "type": self.type,
            "weight": self.weight,
            "timestamp": self.timestamp,
        }

        json_data = json.dumps(data)

        return json_data

    @staticmethod
    def askDisposalInfo():
        token = input("Token Cittadino: ")
        while True:
            try:
                weight = float(input("Peso rifiuto (kg): "))
                break
            except ValueError:
                print("Formato non valido. Perfavore inserire un numero.")

        return (token, weight)