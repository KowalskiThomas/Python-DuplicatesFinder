import shutil
import os

REPORT = 0
DELETE = 1

chemin = "D:/Users/Thomas/Pictures/VERSION PROPRE"

fichiers = [
    "thumbs.db",
    ".picasa.ini",
    "desktop.ini"
]

mode = REPORT

def act(path):
    if mode == REPORT:
        f.write((path + "\n").encode())
    else:
        if os.path.isfile(path):
            print("Suppression de {}".format(path))        
            os.unlink(path)
        else:
            print("{} est vide.".format(path))
            os.rmdir(path)

def supprimerFichiers(dossier):
    for element in os.listdir(dossier):
        _element = element
        element = dossier + "/" + element

        if os.path.isdir(element):
            supprimerFichiers(element)
        elif os.path.isfile(element):
            if _element.lower() in fichiers:
                act(element)
            elif _element.lower().endswith(".ini"):
                act(element)

    vide = True
    for _ in os.listdir(dossier):
        vide = False
        break

    if vide:
        act(dossier)

if __name__ == "__main__":
    if mode == REPORT:
        f = open("log.txt", 'wb')
    else:
        f = None

    supprimerFichiers(chemin)

    if f is not None:
        f.close()
