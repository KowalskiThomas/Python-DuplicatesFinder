"""
Module dédié au calcul et au stockage des sommes MD5 de tous les fichiers dans la variable dossiers.
"""

import hashlib
import os
import sqlite3
import sys
import json

def init():
    """
    Se connecte à la base de données et renvoie la connexion et le curseur.
    Créé la table 'Fichiers' si elle n'existe pas.
    """
    db = sqlite3.connect("Fichiers.s3db")
    cur = db.cursor()

    SQL = "CREATE TABLE Fichiers (Chemin TEXT, MD5 TEXT)"
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

SQL = "INSERT INTO Fichiers VALUES (?, ?)"

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

                # On calcule le MD5 et on insère dans la BDD
                MD5 = md5(path)
                cur.execute(SQL, (path, MD5))

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
