"""
Module dédié au calcul et au stockage des sommes MD5 de tous les fichiers dans la variable dossiers.
"""

import hashlib
import os
import sqlite3
import sys
import json
import exifread

def init():
    """
    Se connecte à la base de données et renvoie la connexion et le curseur.
    Créé la table 'Fichiers' si elle n'existe pas.
    """
    db = sqlite3.connect("Fichiers.s3db")
    cur = db.cursor()

    SQL = "CREATE TABLE Fichiers (Chemin TEXT, MD5 TEXT, Date TEXT)"
    # On lance la requête, qui lève une exception si la table existe déjà
    try:
        cur.execute(SQL)
    except:
        pass

    return db, cur

def md5(fname):
    """
    Calcule la somme MD5 du fichier localisé en `path`.
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

SQL = "INSERT INTO Fichiers VALUES (?, ?, ?)"

def date(fichier):
    print("Recherche de la date pour '{}'".format(fichier))
    
    with open(fichier, 'rb') as f:
        tags = exifread.process_file(f, details = False)
        # return tags

    # On extrait l'information de l'EXIF
    string = tags.get("Image DateTime", None)
    
    # Pas de date de prise de vue
    if string is None: return None

    # On a une date de prise de vue dans le format YYYY:MM:DD HH:mm:SS
    string = str(tags["Image DateTime"])
    string = string.split()
    string = string[0].replace(":", "/") + " " + string[1]
    return string

def recherche(dossiers):
    """
    Recherche tous les fichiers dans `dossiers` et calcule leur somme MD5.
    En même temps, pour éviter de remplir la mémoire, on les stocke dans la base de données.
    """
    db, cur = init()

    # On recherche dans chaque dossier racine de dossiers
    for dossier in dossiers:
        # c est utilisé pour compter les fichiers trouvés : on commit tous les 50
        c = 0

        print("Recherche dans '{}'".format(dossier))
        for root, dirs, files in os.walk(dossier, topdown = False):
            print("\tRecherche dans '{}'".format(root))
            for name in files:
                path = os.path.join(root, name)
                c += 1

                # Détermination du MD5
                MD5 = md5(path)

                # Détermination de la date de prise de vue
                datePriseDeVue = None
                if path.lower().endswith("jpeg") or path.lower().endswith("jpg"):
                    datePriseDeVue = date(path)

                # Insertion dans la base de données
                cur.execute(SQL, (path, MD5, datePriseDeVue))

                # On sauvegarde si nécessaire
                if c % 50 == 0:
                    db.commit()

    db.commit()
    print("Fini !")

if __name__ == "__main__":
    # Les arguments de ligne de commande
    args = sys.argv[1:]

    # Aucun argument donné
    if not args:
        print("Merci de bien vouloir appeler le script comme ceci :")
        print("python recherche.py dossier1 dossier2 dossier3")
        sys.exit(0)
    # Argument 'config' : on charge depuis config.json
    elif args[0] == "config":
        # On essaie de charger la configuration
        # Si ça rate, on détaille pas le problème.
        # L'utilisateur a qu'à se débrouiller
        try:
            with open("config.json") as f:
                dossiers = json.load(f)["Dossiers"]
        except:
            print("Impossible d'ouvrir la configuration.")
            sys.exit(1)

    # Des dossiers donnés en arguments
    # On les ajoute un à un à la liste en vérifiant leur existence
    # Si l'un d'eux n'existe pas, on annule tout.
    else:
        dossiers = list()
        for d in args:
            if not os.path.isdir(d):
                print("Le dossier '{}' n'existe pas !".format(d))
                sys.exit(1)
            else:
                dossiers.append(d)

    recherche(dossiers)
