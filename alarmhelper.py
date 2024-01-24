import paho.mqtt.client as mqtt
import json
from datetime import datetime

from colorama import Fore, Style
from connectionhelper import ConnectionHelper


class AlarmHelper:
    @staticmethod
    def sendOveraboundanceAlarmFor(smartBinID):
        # Invio allarme sovrabbondanza

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.publish(topic, payload, qos=0, retain=False)
                client.disconnect()  # Scollega il client dopo l'invio del messaggio
            else:
                print(Fore.RED + Style.BRIGHT + f"Connessione al broker MQTT fallita con codice di ritorno {rc}" + Style.RESET_ALL)

        broker_url = ConnectionHelper.hostMQTT # "localhost"
        broker_port = ConnectionHelper.broker_port # 1883
        topic = "smartbin/alarms/capacity"
        client_id = "mqtt-publisher"

        client = mqtt.Client(client_id)
        client.on_connect = on_connect

        try:
            client.connect(broker_url, broker_port)

            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]  # Formatta la data come desiderato

            message_json = {
                "smartBinID": f"{smartBinID}",
                "description": "",
                "timestamp": formatted_time
            }
            payload = json.dumps(message_json, separators=(',', ':'))
            print(Fore.YELLOW + "* Invio allarme sovrabbondanza: " + payload  + Style.RESET_ALL)
        except Exception as e:
            print(f"Errore durante la preparazione del messaggio MQTT: {str(e)}")

        client.loop_forever()

    @staticmethod
    def dismissOveraboundanceAlarmFor(smartBinID):
        # Invio allarme svuotamento bin

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.publish(topic, payload, qos=0, retain=False)
                client.disconnect()  # Scollega il client dopo l'invio del messaggio
            else:
                print(Fore.RED + Style.BRIGHT + f"Connessione al broker MQTT fallita con codice di ritorno {rc}" + Style.RESET_ALL)

        broker_url = ConnectionHelper.hostMQTT  # "localhost"
        broker_port = ConnectionHelper.broker_port  # 1883
        topic = "smartbin/alarms/cleaning"
        client_id = "mqtt-publisher"

        client = mqtt.Client(client_id)
        client.on_connect = on_connect

        try:
            client.connect(broker_url, broker_port)

            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]  # Formatta la data come desiderato

            message_json = {
                "smartBinID": f"{smartBinID}",
                "description": "",
                "timestamp": formatted_time
            }
            payload = json.dumps(message_json, separators=(',', ':'))
            print(Fore.YELLOW + "* Invio allarme pulizia effettuata: " + payload  + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"Errore durante la preparazione del messaggio MQTT: {str(e)}" + Style.RESET_ALL)

        client.loop_forever()
