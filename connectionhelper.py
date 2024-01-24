import jwt
import datetime
import base64

class ConnectionHelper:
    hostMQTT = '3.208.106.127'# 'localhost'
    baseURL = 'https://nn9im8cie6.execute-api.us-east-1.amazonaws.com/prod' # 'http://localhost'
    broker_port = 1883
    #token_jwt = ''

    @staticmethod
    def token_jwt():
       
        # Chiave segreta per firmare il token
        secret_key = 'seedseedseedseedseedseedseedseedseedseedseed'

        # Converti la chiave segreta in un oggetto bytes
        secret_key_bytes = secret_key.encode()

        # Codifica la chiave segreta in Base64
        secret_key_base64 = secret_key#base64.b64encode(secret_key_bytes).decode()
        print(f"Secretkey_b64={secret_key_base64}")

        # Creazione di un payload con alcune informazioni utente
        payload = {
            'role': 'SmartBinNode',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Scadenza del token

            "aud": [
                "http://smartBinsManagementService:8081",
                "http://citizenManagementService:8082",
                "http://disposalManagementService:8083",
                "http://taxService:8085",
                "http://loginService:8080"
            ],
            "sub": "nodo",
            "iat": datetime.datetime.utcnow(),
            "iss": "nodo_smartbin",
        }

        # Creazione del token
        token = jwt.encode(payload=payload, key=secret_key_base64, algorithm='HS256')

        print("Token JWT generato: " + token)
        return token
