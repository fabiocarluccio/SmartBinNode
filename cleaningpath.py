import time

import requests
import json
from tabulate import tabulate
from colorama import init, Fore, Back, Style
from datetime import datetime

from alarmhelper import AlarmHelper
from connectionhelper import ConnectionHelper


# CLASSES
class CleaningPath:
    def __init__(self, id, smartBinIDPath, scheduledDate, done):
        self.id = id
        self.smartBinIDPath = smartBinIDPath
        self.scheduledDate = scheduledDate
        self.done = done

    @staticmethod
    def getCleaningPathList():
        # get lista percorsi non ancora completati mediante SmartBinMS
        url = f'{ConnectionHelper.baseURL}/api/cleaningPath/status?done=false'
        token_jwt = ConnectionHelper.token_jwt()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token_jwt}'
        }

        # Effettua la richiesta GET
        response = requests.get(url, headers=headers)

        # Verifica lo stato della risposta
        if response.status_code == 204:
            return []
        if response.status_code != 200:
            print(Fore.RED + Style.BRIGHT + f"Richiesta lista percorsi di pulizia non riuscita. Codice di stato: {response.status_code}" + Style.RESET_ALL)
            return

        # Contenuto della risposta
        content = json.loads(response.text)

        cleaningPathList = []

        for cleaningPath_json in content:
            cleaningPath = CleaningPath(cleaningPath_json["id"],
                           cleaningPath_json["smartBinIDPath"],
                           cleaningPath_json["scheduledDate"],
                           cleaningPath_json["done"])
            cleaningPathList.append(cleaningPath)

        return cleaningPathList

    @staticmethod
    def printCleaningPathList(cleaningPathList):

        if not cleaningPathList:
            print("Nessun percorso da effettuare.\n")
            return

        headers = ["ID", "N. SmartBins", "Data"]
        tabulateData = []
        for cleaningPath in cleaningPathList:
            timestamp_milliseconds = cleaningPath.scheduledDate
            timestamp_seconds = timestamp_milliseconds / 1000.0  # Converti da millisecondi a secondi
            date_time = datetime.utcfromtimestamp(timestamp_seconds)
            date_time_formatted = date_time.strftime("%d/%m/%Y %H:%M")
            tabulateData.append((cleaningPath.id, len(cleaningPath.smartBinIDPath), date_time_formatted))

        # Utilizza tabulate per formattare e stampare la tabella
        table = tabulate(tabulateData, headers, tablefmt="plain")
        #print("-----------------------------------------------------------------------------------------")
        print("\n" + table + "\n")
        #print("-----------------------------------------------------------------------------------------")

    @staticmethod
    def getCleaningPathBy(cleaningPathId, cleaningPaths):
        for cleaningPath in cleaningPaths:
            if cleaningPath.id == cleaningPathId:
                return cleaningPath
        return "not valid"

    def toString(self):
        headers = ["ID", "N. SmartBins", "Data"]
        tabulateData = [((self.id, len(self.smartBinIDPath), self.scheduledDate))]

        # Utilizza tabulate per formattare e stampare la tabella
        table = tabulate(tabulateData, headers, tablefmt="plain")
        #print("-----------------------------------------------------------------------------------------")
        print("\n" + table + "\n")
        #print("-----------------------------------------------------------------------------------------")

    def executeCleaningPath(cleaningPath, smartBinList):

        print(Fore.YELLOW + "Avvio percorso di pulizia..." + Style.RESET_ALL)
        for smartBinId in cleaningPath.smartBinIDPath:
            time.sleep(2)

            # Svuoto (fisicamente) lo SmartBin (la bilancia segna 0 kg)
            status = "ERROR"
            isOnOveraboundanceAlarm = False
            for smartBin in smartBinList:
                if smartBin.id == smartBinId:
                    # Verifico se lo SmartBin era in allarme sovrabbondanza
                    capacityPercentage = smartBin.currentCapacity / smartBin.totalCapacity

                    if capacityPercentage >= float(smartBin.capacityThreshold):
                        isOnOveraboundanceAlarm = True


                    smartBin.currentCapacity = 0

                    if isOnOveraboundanceAlarm:
                        print(Fore.YELLOW + "Invio notifica avvenuto svuotamento a WMC." + Style.RESET_ALL)
                        AlarmHelper.dismissOveraboundanceAlarmFor(smartBin.id)

                    status = "SUCCESS"
                    break
            if status == "ERROR": return "ERROR"

            if isOnOveraboundanceAlarm: print("Eseguo svuotamento smartBin", Fore.RED + Style.BRIGHT + smartBinId + Style.RESET_ALL, "...")
            else: print("Eseguo svuotamento smartBin " + smartBinId + "...")
            status = CleaningPath.emptySmartBin(smartBinId)
            if status == "ERROR": return "ERROR"



        status = CleaningPath.finalizePath(cleaningPath.id)
        if status == "SUCCESS": return "SUCCESS"
        return "ERROR"

    def emptySmartBin(smartBinId):
        url = f'{ConnectionHelper.baseURL}/api/smartbin/' + smartBinId + '/reset'
        token_jwt = ConnectionHelper.token_jwt()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token_jwt}'
        }

        # Effettua la richiesta POST
        response = requests.post(url, headers=headers)

        # Verifica lo stato della risposta
        if response.status_code != 200 and response.status_code != 204:
            print(url)
            return "ERROR"

        AlarmHelper.dismissOveraboundanceAlarmFor(smartBinId)
        return "SUCCESS"

    def finalizePath(cleaningPathId):
        url = f'{ConnectionHelper.baseURL}/api/cleaningPath/' + cleaningPathId
        token_jwt = ConnectionHelper.token_jwt()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token_jwt}'
        }

        # Effettua la richiesta POST
        response = requests.patch(url, headers=headers)

        # Verifica lo stato della risposta
        if response.status_code != 200 and response.status_code != 204:
            return "ERROR"

        return "SUCCESS"