from cleaningpath import CleaningPath
from disposal import *
from disposalhelper import *
from smartbin import *
from alarmhelper import *
from colorama import init, Fore, Back, Style

from terminalclearer import TerminalClearer

# MENU Functions
def showMainMenu():
    print("Seleziona azione")
    print("1. Accedi a Bin (tramite ID)")
    print("2. Visualizza percorsi di pulizia da effettuare")
    print("0. Aggiorna lista SmartBins") # (corrisponde a riavviare il tutto in modo che se uno smartbin viene aggiunto mentre il nodo è in esecuzione, questo viene caricato in memoria)
    print("X. Esci")
    return input("> ")
def showBinMenuFor(currentBin):
    currentBin.toString()
    print("Seleziona azione")
    print("1. Effettua conferimento")
    print("X. Torna indietro")
    return input("> ")
def showCleaningPathMenu():
    print("Seleziona azione")
    print("1. Avvia percorso di pulizia")
    print("0. Aggiorna lista percorsi")
    print("X. Torna indietro")
    return input("> ")

# MAIN
# Ogni SmartBin di tipo ALLOCATED viene caricato in memoria. Si suppone che, quando questo nodo è in esecuzione,
# nessuna altra entità possa effettuare conferimenti.
# L'intento di questo script è quello di simulare ciascun nodo fisico SmartBin.
# I passi principali del main sono questi:
# 1. Caricare tutti gli SmartBins ALLOCATED
# 2. Mostrare menu principale
def main():
    TerminalClearer.clear()

    while True:
        smartBinList = SmartBin.getBinList()

        while True:
            SmartBin.printBinList(smartBinList)
            choice = showMainMenu()

            if choice == "1":
                TerminalClearer.clear()
                SmartBin.printBinList(smartBinList)
                binId = input("Inserisci ID del Bin al quale accedere: ")
                currentBin = SmartBin.getBinBy(binId, smartBinList)

                TerminalClearer.clear()
                while currentBin != "not valid":    # se currentBin è "not valid" significa che ha inserito un id di bin non valido

                    choice = showBinMenuFor(currentBin)
                    if choice == "1":
                        (token, weight) = Disposal.askDisposalInfo()
                        TerminalClearer.clear()

                        # Check capienza
                        if currentBin.currentCapacity + int(weight) > currentBin.totalCapacity:
                            TerminalClearer.clear()
                            print(Fore.RED + Style.BRIGHT + "Impossibile effettuare il conferimento." + Style.RESET_ALL)
                        else:
                            # Invio tramite RabbitMQ le info del conferimento al microservizio Conferimenti
                            disposal = Disposal(currentBin.id, token, currentBin.type, weight, currentBin.position)
                            DisposalHelper.insertDisposal(disposal)
                            status = DisposalHelper.status

                            if status == "SUCCESS":
                                print(Fore.GREEN + "Conferimento effettuato con successo." + Style.RESET_ALL)
                                # Aggiorno peso SmartBin
                                oldCapacityPercentage = currentBin.currentCapacity / currentBin.totalCapacity
                                currentBin.currentCapacity += weight
                                newCapacityPercentage = currentBin.currentCapacity / currentBin.totalCapacity
                                # Verifico se inviare allarme sovrabbondanza
                                if oldCapacityPercentage < float(currentBin.capacityThreshold) and \
                                        newCapacityPercentage >= float(currentBin.capacityThreshold):
                                    AlarmHelper.sendOveraboundanceAlarmFor(currentBin.id)
                            elif status == "ERROR":
                                print(Fore.RED + Style.BRIGHT + "Errore richiesta. Controllare che il token fornito sia valido." + Style.RESET_ALL)
                            elif status == "TIMEOUT_ERROR":
                                print(Fore.RED + Style.BRIGHT + "Errore di Timeout. Impossibile esaudire la richiesta momentaneamente." + Style.RESET_ALL)
                            else:
                                print(Fore.RED + Style.BRIGHT + "Errore sconosciuto. Impossibile esaudire la richiesta momentaneamente." + Style.RESET_ALL)
                    elif choice == "x":
                        TerminalClearer.clear()
                        break
                    else:
                        TerminalClearer.clear()
                        print(Fore.RED + Style.BRIGHT + "Scelta non valida." + Style.RESET_ALL)
                if currentBin == "not valid":
                    TerminalClearer.clear()
                    print(Fore.RED + Style.BRIGHT + "ID SmartBin non esistente." + Style.RESET_ALL)
            elif choice == "2":
                TerminalClearer.clear()
                while True:
                    cleaningPathList = CleaningPath.getCleaningPathList()
                    CleaningPath.printCleaningPathList(cleaningPathList)
                    choice = showCleaningPathMenu()

                    if choice == "1":
                        # Seleziona percorso di pulizia
                        TerminalClearer.clear()
                        CleaningPath.printCleaningPathList(cleaningPathList)
                        cleaningPathId = input("Inserisci ID del Percorso da effettuare: ")
                        currentCleaningPath = CleaningPath.getCleaningPathBy(cleaningPathId, cleaningPathList)

                        TerminalClearer.clear()
                        if currentCleaningPath != "not valid":
                            status = CleaningPath.executeCleaningPath(currentCleaningPath, smartBinList)
                            if status == "SUCCESS":
                                print(Fore.GREEN + "Percorso completato con successo" + Style.RESET_ALL)
                            else:
                                print(Fore.RED + Style.BRIGHT + "Errore sconosciuto." + Style.RESET_ALL)
                            break
                        else:
                            TerminalClearer.clear()
                            print(Fore.RED + Style.BRIGHT + "ID percorso di pulizia non valido" + Style.RESET_ALL)


                    elif choice == "x":
                        TerminalClearer.clear()
                        break
                    elif choice == "0":
                        TerminalClearer.clear()
                    else:
                        TerminalClearer.clear()
                        print(Fore.RED + Style.BRIGHT + "Scelta non valida." + Style.RESET_ALL)

            elif choice == "0":
                TerminalClearer.clear()
                break
            elif choice == "x":
                return
            else:
                TerminalClearer.clear()
                print(Fore.RED + Style.BRIGHT + "Scelta non valida." + Style.RESET_ALL)


if __name__ == '__main__':
    main()

