import requests
import json
from tabulate import tabulate
from colorama import init, Fore, Back, Style

from connectionhelper import ConnectionHelper


# CLASSES
class SmartBin:
    def __init__(self, id, name, type, currentCapacity, totalCapacity, state, position, capacityThreshold):
        self.id = id
        self.name = name
        self.type = type
        self.totalCapacity = totalCapacity
        self.currentCapacity = currentCapacity
        self.state = state
        self.position = position
        self.capacityThreshold = capacityThreshold


    @staticmethod
    def getBinList():

        # get lista Bins ALLOCATI mediante SmartBinMS
        url = f'{ConnectionHelper.baseURL}/api/smartbin/state?state=ALLOCATED'
        token_jwt = ConnectionHelper.token_jwt()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token_jwt}'
        }

        # Effettua la richiesta GET
        response = requests.get(url, headers=headers)

        # Verifica lo stato della risposta
        if response.status_code != 200:
            print(Fore.RED + Style.BRIGHT + f"Richiesta lista SmartBins non riuscita. Codice di stato: {response.status_code}" + Style.RESET_ALL)
            return

        # Contenuto della risposta
        content = json.loads(response.text)

        smartBins = []

        for bin_json in content:
            bin = SmartBin(bin_json["id"],
                           bin_json["name"],
                           bin_json["type"],
                           bin_json["currentCapacity"],
                           bin_json["totalCapacity"],
                           bin_json["state"],
                           bin_json["position"],
                           bin_json["capacityThreshold"])
            smartBins.append(bin)

        return smartBins

    @staticmethod
    def printBinList(smartbins):

        if not smartbins: return

        headers = ["ID", "Nome", "Tipologia", "Capienza (kg)", "Soglia"]
        tabulateData = []
        for bin in smartbins:

            # Verifico se lo SmartBin è in allarme sovrabbondanza
            capacityPercentage = bin.currentCapacity / bin.totalCapacity

            if capacityPercentage >= float(bin.capacityThreshold):
                tabulateData.append((bin.id, bin.name, bin.type, Fore.RED + Style.BRIGHT + f"{bin.currentCapacity}/{bin.totalCapacity}" + Style.RESET_ALL, bin.capacityThreshold))
            else:
                tabulateData.append((bin.id, bin.name, bin.type, f"{bin.currentCapacity}/{bin.totalCapacity}", bin.capacityThreshold))

        # Utilizza tabulate per formattare e stampare la tabella
        table = tabulate(tabulateData, headers, tablefmt="plain")
        print("\n" + table + "\n")

    @staticmethod
    def getBinBy(binId, smartbins):
        for smartbin in smartbins:
            if smartbin.id == binId:
                return smartbin
        return "not valid"

    def toString(self):
        headers = ["ID", "Nome", "Tipologia", "Capienza (kg)", "Soglia"]

        # Verifico se lo SmartBin è in allarme sovrabbondanza
        capacityPercentage = self.currentCapacity / self.totalCapacity

        if capacityPercentage >= float(self.capacityThreshold):
            tabulateData = [((self.id, self.name, self.type, Fore.RED + Style.BRIGHT + f"{self.currentCapacity}/{self.totalCapacity}" + Style.RESET_ALL, self.capacityThreshold))]
        else:
            tabulateData = [((self.id, self.name, self.type, f"{self.currentCapacity}/{self.totalCapacity}", self.capacityThreshold))]


        # Utilizza tabulate per formattare e stampare la tabella
        table = tabulate(tabulateData, headers, tablefmt="plain")
        print("\n" + table + "\n")