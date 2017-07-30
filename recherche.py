"""
Module dédié au calcul et au stockage des sommes MD5 de tous les fichiers dans la variable dossiers.
"""

import hashlib
import os
import sqlite3
import sys
import json
import exifread
import time

nomBDD = time.strftime("%Y-%m-%d %H-%M") + ".s3db"

def init():
    """
    Se connecte à la base de données et renvoie la connexion et le curseur.
    Créé la table 'Fichiers' si elle n'existe pas.
    """
    db = sqlite3.connect("Fichiers.s3db")
    cur = db.cursor()

    SQL = "CREATE TABLE Fichiers (Chemin TEXT, MD5 TEXT, Date TEXT, Size INTEGER)"
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

def date(fichier):
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

    # On récupère la liste des fichiers déjà traités
    SQL = "SELECT Chemin FROM Fichiers"
    dejaTrouve = [x[0] for x in cur.execute(SQL).fetchall()]

    # Instruction SQL pour l'insertion
    SQL = "INSERT INTO Fichiers VALUES (?, ?, ?, ?)"

    # On recherche dans chaque dossier racine de dossiers
    for dossier in dossiers:
        # c est utilisé pour compter les fichiers trouvés : on commit tous les 50
        c = len(dejaTrouve)

        print("Recherche dans '{}'".format(dossier))
        for root, dirs, files in os.walk(dossier, topdown = False):
            print("\tRecherche dans '{}'".format(root))
            for name in files:
                # On trouve le chemin complet du fichier
                path = os.path.join(root, name)

                # Pour permettre de réduire la complexité liée à la recherche dans dejaTrouve au cours du temps,
                # on supprime petit à petit les chemins qu'on a déjà vus
                try:
                    indice = dejaTrouve.index(path)
                    del dejaTrouve[indice]
                    continue
                except ValueError:
                    # On n'a pas déjà traité ce chemin
                    pass

                # Incrémentation du compteur de fichiers
                c += 1

                # Détermination du MD5
                MD5 = md5(path)

                # Détermination de la date de prise de vue
                datePriseDeVue = None
                if path.lower().endswith("jpeg") or path.lower().endswith("jpg"):
                    datePriseDeVue = date(path)

                # Détermination de la taille du fichier
                taille = os.stat(path).st_size

                # Insertion dans la base de données
                cur.execute(SQL, (path, MD5, datePriseDeVue, taille))

                # On sauvegarde si nécessaire
                if c % 50 == 0:
                    print("{} fichiers trouvés.".format(c))
                    db.commit()

    db.commit()
    print("Fini !")

if __name__ == "__main__":
    # Les arguments de ligne de commande
    args = sys.argv[1:]

    # Aucun argument donné
    if not args:
        print("Merci de bien vouloir appeler le script comme ceci :")
        print("python [config] [reset] recherche.py dossier1 dossier2 dossier3")
        sys.exit(0)
    # Argument 'config' : on charge depuis config.json
    else:
        # Suppression d'une base de données existante
        if "reset" in args:
            print("Suppression de la base de données.")
            if os.path.isfile("Fichiers.s3db"):
                os.unlink("Fichiers.s3db")
            if len(args) == 1:
                print("Merci de bien vouloir appeler le script comme ceci :")
                print("python [config] [reset] recherche.py dossier1 dossier2 dossier3")
                sys.exit(0)

            # On supprime l'argument reset qui serait mal interprété comme un dossier :
            del args[args.index("reset")]

    if args[0] == "config":
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
