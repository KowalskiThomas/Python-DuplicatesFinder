"""
Ce module permert ede renommer automatiquement les dossiers après un tri des doublons avec les autres modules.
Pour cela, il va travailler de la sorte suivante :
    Si le dossier a déjà un nom du type <Date> <Description> Alors
        Si <Date> est déjà au format choisi
            On ne fait rien
        Sinon
            On modifie le format de la date
        Fin Si
    Sinon
        On regarde les fichiers dans le dossier et on essaie de trouver une date de prise de vue
        Si tous les fichiers on la même date
            On renomme le dossier en fonction de celle-ci
        Sinon
            On écrit dans un rapport les différentes dates
        Fin Si
    Fin Si
"""

import shutil
import os
import sqlite3
import pyperclip
# Pour DatePrisedeVue
from recherche import date

RAPPORT = 0
RENOMMAGE = 1

def supprimerChiffres(s, accepte = ["123456789"]):
    """
    Cette fonction est moche.
    """
    sortie = ""
    for c in s:
        if c in accepte:
            sortie += c

    return sortie

def formatterNomDossier(dossier):     
   
    _dossier = dossier.split("/")[-1]
    # print(_dossier)
    
    # On sépare par l'espace et on regarde si la première partie est une date
    avantEspace = _dossier.split(" ")[0]
    avantEspaceSansTiret = avantEspace.replace("-", "")

    try:
        if "xx" in avantEspaceSansTiret.lower():
            avantEspace = avantEspace.lower().replace("xx", "")
        else:
            int(avantEspaceSansTiret)
    
        # print("Date déjà là pour {}".format(_dossier))

        # Récupération des paramètres communs
        annee = dossier.split("/")[-2]
        if " " in _dossier:
            description = " ".join(_dossier.split(" ")[1:])
        else:
            description = ""

        # Format MMDD
        if len(avantEspace) == 4:
            mois = avantEspace[0:2]
            jour = avantEspace[2:4]
        # Format MM-DD
        elif len(avantEspaceSansTiret) == 4:
            mois = avantEspace[0:2]
            jour = avantEspace[3:5]
        # Format YYYY-MM
        elif len(avantEspaceSansTiret) == 6:
            mois = avantEspace[5:7]
            jour = "xx"
        # Format YYYY-MM-DD
        elif len(avantEspaceSansTiret) == 8:
            annee = avantEspace[0:4]
            mois = avantEspace[5:7]
            jour = avantEspace[8:10]

        if annee != dossier.split("/")[-2]:
            print("Année bizarre pour {}".format(dossier))
            input()

        if "xx" in avantEspaceSansTiret.lower():
            jour = "xx"

        return "{}-{}-{} {}".format(annee, mois, jour, description)

    except ValueError as e:
        # On a voulu faire un int avec un morceau du nom mais ça a pas marché
        # On va regarder à quoi c'est dû

        sansChiffres = supprimerChiffres(avantEspaceSansTiret)
        if not sansChiffres == "":
            print("Merci de renommer manuellement {}".format(dossier))
            pyperclip.copy(dossier)
            input()
        else:        
            for element in os.listdir(dossier):
                if os.path.isdir(dossier + "/" + element):
                    # print("{} contient un dossier : on passe".format(dossier))
                    return None

            # print("Pas de date pour {}".format(_dossier))
            dates = set()
            for element in os.listdir(dossier):
                _element = element
                element = dossier + "/" + element

                if not os.path.isfile(element):
                    print("{} n'est pas un fichier !".format(_element))
                    input()
    
                d = date(element)
                if d is not None:
                    dates.add(d[0:10])

            if f is not None:
                f.write(_dossier + "\n")
                for d in dates:
                    f.write("\t{}\n".format(d))
            else:
                print("f est fermé !")
            return ""
    

    except Exception as e:
        raise e

def renommerDossiers(racine):
    _racine = racine.split("/")[-1]
    print("Traitement de {}".format(_racine))
    contenus = os.listdir(racine)
    dossiers = list()

    for element in contenus:
        _element = element
        element = racine + "/" + element
        if os.path.isdir(element):
            dossiers.append(element)

    for dossier in dossiers:
        nouveauNom = formatterNomDossier(dossier)
        # if not nouveauNom is None:
        #     print(nouveauNom)
        # else:
        #     print("On ne renomme pas {}".format(dossier))
        agir(dossier, nouveauNom)

def agir(dossier, nouveauNom):
    if mode == RAPPORT:
        SQL = "INSERT INTO Dossiers VALUES (?, ?)"
        cur.execute(SQL, (dossier.split("/")[-1], nouveauNom))
    else:
        raise Exception("pas implémenté")
        

mode = RAPPORT
db, cur = None, None
f = None

if __name__ == "__main__":
    racines = ["D:/Users/Thomas/Pictures/VERSION PROPRE/Photos Communes", "D:/Users/Thomas/Pictures/VERSION PROPRE/Photos Thomas"]


    f = open("rapport.txt", 'w')

    if mode == RAPPORT:
        print("Mode rapport")
        db = sqlite3.connect("Renommage_Dossiers.s3db")
        cur = db.cursor()
        try:
            cur.execute("DROP TABLE Dossiers")
        except:
            pass
        cur.execute("CREATE TABLE Dossiers (Avant TEXT, Apres TEXT)")

    else:
        print("Mode exécution")

    for racine in racines:
        annees = [racine + "/" + d for d in os.listdir(racine) if os.path.isdir(racine + "/" + d)]
        for annee in annees:
            _annee = annee.split("/")[-1]

            # On vérifie que le dossier en cours de traitement désigne une année (pas un dossier genre "Images")
            # Pour ça, et pour éviter de catcher les exceptions entraînées par renommerDossiers, on passe à l'élément suivant de l'itérable en cas d'exception
            # Sinon on continue l'exécution
            # Comme ça, renommerDossiers est en dehors du try
            try:
                int(_annee)
            except:
                print("{} n'est pas une année.".format(_annee))
                continue

            renommerDossiers(annee)

    db.commit()
    f.close()