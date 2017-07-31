"""
Module dédié au traitement des doublons.
On récupère les données stockées dans la BDD et on fait des choses intéressantes avec.
"""

import sqlite3
import os
import json

def connect():
    # On se connecte à la base de données et on récupère le curseur
    db = sqlite3.connect("Fichiers.s3db")
    cur = db.cursor()

    return db, cur

def rapport():
    """
    Ouvre la base de données et cherche les doublons à partir de celle-ci.
    Ecrit dans un fichier log.txt au fur et à mesure que la fonction trouve les doublons.
    """

    db, cur = connect()

    # On récupère les lignes en les groupant par MD5
    # On ne récupère que les groupes qui ont au moins deux éléments
    # Sinon il n'y a pas de doublon !
    SQL = """
        SELECT MD5 
        FROM Fichiers
        GROUP BY MD5
        HAVING COUNT(MD5) > 1
        """

    # SQLite3 renvoie les lignes sous forme de tuples ; dans notre cas ce sont des tuples de un élément... pas très intéressant
    # Donc on filtre.
    resultats = [x[0] for x in cur.execute(SQL).fetchall()]

    # On ouvre le fichier de résultats
    f = open("log.txt", 'w')

    # Pour une MD5 donnée, on peut trouver tous les fichiers qui la partagent
    SQL = "SELECT Chemin FROM Fichiers WHERE MD5 = ?"
    for md5 in resultats:
        doublons = [x[0] for x in cur.execute(SQL, (md5, ))]

        # On a maintenant tous les fichiers qui ont ce MD5
        for fichier in doublons:
            f.write(fichier)
            f.write("\n")

        f.write("\n")

    f.close()

def nomsDesDossiers():
    db, cur = connect()

    SQL = "SELECT Chemin FROM Fichiers GROUP BY MD5"
    donnees = cur.execute(SQL).fetchall()

    exclusion = [
        "lrdata"
    ]

    dossiers = set()
    for ligne in donnees:
        chemin = ligne[0]
        
        for ex in exclusion:
            if ex in chemin:
                break
        else:
            dossiers.add(os.path.dirname(chemin))

    with open("dossiers.txt", "wb") as f:
        for dossier in dossiers:
            f.write(dossier.encode())
            f.write("\n".encode())

def reorganisation():
    db, cur = connect()

    dossiers = set()

    SQL = "SELECT * FROM Fichiers"
    resultats = cur.execute(SQL).fetchall()

    for chemin, _, _, _, _ in resultats:
        dossiers.add(os.path.dirname(chemin))

    # Détermination du pourcentage de doublons dans chaque dossier
    SQL = """SELECT * FROM Fichiers
             WHERE Chemin LIKE "{}%"
          """

    # Maintenant qu'on a un ensemble de dossiers, on le transforme en dictionnaire pour pouvoir stocker les pourcentages de doublons
    dossiers = {dossier : 0 for dossier in dossiers}
    for dossier in dossiers:
        fichiers = cur.execute(SQL.format(dossier)).fetchall()

        totalFichiers = len(fichiers)
        totalDoublons = 0

        SQL2 = "SELECT * FROM Fichiers WHERE MD5 = ?"
        for chemin, md5, _, _, _ in fichiers:
            doublons = cur.execute(SQL2, (md5, )).fetchall()

            if len(doublons) > 1:
                totalDoublons += 1

        ratio = totalDoublons / totalFichiers
        dossiers[dossier] = ratio

    with open("dossiers.json") as f:
        json.dump(dossiers, f)

reorganisation()
