import pika
import json
from datetime import datetime
from colorama import init, Fore, Back, Style

from connectionhelper import ConnectionHelper


class DisposalHelper:
    status = ""

    @staticmethod
    def insertDisposal(disposal):
        DisposalHelper.sendDisposal(disposal)
        print(Fore.YELLOW + "- Attendere..." + Style.RESET_ALL)
        return DisposalHelper.listen_confirm_disposal_queue()




    @staticmethod
    def sendDisposal(disposal):
        connection = pika.BlockingConnection(pika.ConnectionParameters(ConnectionHelper.hostMQTT))
        channel = connection.channel()

        exchange_name = 'direct_exchange'
        channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)

        queue_name = 'coda.aggiunta_conferimento'
        channel.queue_declare(queue=queue_name, durable=True)
        routing_key = 'aggiunta_conferimento'
        channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        """
        position = {
            "type": "Point",
            "coordinates": [18.4254541, 40.005262]
        }
        """

        message_dict = {
            "smartBinID": disposal.binId,
            "type": disposal.type,
            "token": disposal.token,
            "amount": disposal.weight,
            "timestamp": datetime.now().isoformat(),
            "position": disposal.position
        }

        # Funzione per inviare un messaggio al broker RabbitMQ
        def send_message(message):
            channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
            print(Fore.YELLOW + f"> Invio messaggio: {message}" + Style.RESET_ALL)

        message = json.dumps(message_dict)

        send_message(message)

        channel.close()
        connection.close()

    @staticmethod
    def listen_confirm_disposal_queue():
        DisposalHelper.status = "TIMEOUT_ERROR"

        # Connessione al broker RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(ConnectionHelper.hostMQTT))
        channel = connection.channel()

        # Dichiarazione dell'exchange di tipo 'direct'
        exchange_name = "direct_exchange"
        channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)

        # Creazione della coda
        queue_name = "coda.conferma_conferimento"
        channel.queue_declare(queue=queue_name, durable=True)

        # Bind tra la coda e l'exchange con una routing key specifica
        routing_key = "conferma_conferimento"
        channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

        # Funzione callback per consumare il messaggio
        def callback(ch, method, properties, body):
            message = body.decode('utf-8')
            print(Fore.YELLOW + f"< Ricevo messaggio: {message}" + Style.RESET_ALL)
            data = json.loads(message)
            DisposalHelper.status = data["status"]
            channel.close()
            connection.close()


        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

        return DisposalHelper.status

