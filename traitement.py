"""
Module dédié au traitement des doublons.
On récupère les données stockées dans la BDD et on fait des choses intéressantes avec.
"""

import sqlite3
import os
import json
import datetime
import shutil 

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

def grosDelta():
    """
    Affiche tous les fichiers dont la différence entre date de modification et de prise de vue > 1 jour.
    """
    db, cur = connect()
    SQL = "SELECT * FROM Fichiers"
    for chemin, md5, date, dateModification, taille in cur.execute(SQL).fetchall():
        if date is None or dateModification is None:
            continue
        date = datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
        dateModification = datetime.datetime.strptime(dateModification, "%Y/%m/%d %H:%M:%S")

        diff = date - dateModification
        
        if diff > datetime.timedelta(days = 1, seconds = 60):
            print(chemin)

def methodeDesDossiers():
    """
    Cette fonction permet de recopier les images en conservant toujours le fichier contenu dans le dossier le plus rempli.
    Par exemple:
    ```
    Dossier 1
    -- Fichier1
    -- Fichier2
    -- Fichier3
    Dossier 2
    -- Fichier2
    -- Fichier3
    ```
    Ne seront alors conservés que les fichiers dans le Dossier 1.
    """

    def calculerNombreDeFichiers(dossier):
        renvoye = 0

        for x in os.listdir(dossier):
            if os.path.isdir(x):
                renvoye += calculerNombreDeFichiers(dossier + "/" + x)
            else:
                renvoye += 1

        return renvoye        

    db, cur = connect()

    dossiers = set()
    nombreDeFichiers = {"" : 0}

    SQL = "SELECT * FROM Fichiers"
    resultats = cur.execute(SQL).fetchall()

    for chemin, _, _, _, _ in resultats:
        dossier = os.path.dirname(chemin)
        dossiers.add(dossier)

    for dossier in dossiers:
        nombreDeFichiers[dossier] = calculerNombreDeFichiers(dossier)

    SQL = """
    SELECT MD5 
    FROM Fichiers
    GROUP BY MD5
    HAVING COUNT(MD5) > 1
    """

    # SQLite3 renvoie les lignes sous forme de tuples ; dans notre cas ce sont des tuples de un élément... pas très intéressant
    # Donc on filtre.
    resultats = [x[0] for x in cur.execute(SQL).fetchall()]

    # Pour une MD5 donnée, on peut trouver tous les fichiers qui la partagent
    SQL = "SELECT Chemin FROM Fichiers WHERE MD5 = ?"
    print("Copie des doublons.")
    for i, md5 in enumerate(resultats):
        if i % 100 == 0:
            print("Progrès: {}/{}".format(i, len(resultats)))

        doublons = [x[0] for x in cur.execute(SQL, (md5, ))]
        
        meilleur = ""
        meilleurFichier = ""
        for fichier in doublons:
            if nombreDeFichiers[os.path.dirname(fichier)] > nombreDeFichiers[meilleur]:
                meilleur = os.path.dirname(fichier)
                meilleurFichier = fichier
        
        cheminRelatif = meilleurFichier.replace("D:\\Users\\Thomas\\Pictures", "")
        nouveauChemin = "D:\\Users\\Thomas\\Pictures\\VERSION PROPRE\\{}".format(cheminRelatif)
        if not os.path.isdir(os.path.dirname(nouveauChemin)):
            os.makedirs(os.path.dirname(nouveauChemin))
        shutil.copy(meilleurFichier, nouveauChemin)

    SQL = """
    SELECT MD5 
    FROM Fichiers
    GROUP BY MD5
    HAVING COUNT(MD5) = 1
    """
    resultats = [x[0] for x in cur.execute(SQL).fetchall()]

    SQL = "SELECT Chemin FROM Fichiers WHERE MD5 = ?"
    print("Copie des non doublons.")
    for i, md5 in enumerate(resultats):
        if i % 100 == 0:
            print("Progrès: {}/{}".format(i, len(resultats)))
        
        doublons = [x[0] for x in cur.execute(SQL, (md5, ))]
        
        cheminRelatif = fichier.replace("D:\\Users\\Thomas\\Pictures", "")
        nouveauChemin = "D:\\Users\\Thomas\\Pictures\\VERSION PROPRE\\{}".format(cheminRelatif)
        
        if not os.path.isdir(os.path.dirname(nouveauChemin)):
            os.makedirs(os.path.dirname(nouveauChemin))
        
        shutil.copy(fichier, nouveauChemin)

methodeDesDossiers()

def reorganisation():
    """
    Ca fait pas grand chose.
    """
    db, cur = connect()
    
    dossiers = set()
    dossiersAvecMD5 = dict()
    md5 = dict()

    SQL = "SELECT * FROM Fichiers"
    resultats = cur.execute(SQL).fetchall()

    for chemin, MD5, _, _, _ in resultats:
        dossier = os.path.dirname(chemin)
        dossiers.add(dossier)
        
        if not dossier in dossiersAvecMD5:
            dossiersAvecMD5[dossier] = list()
        
        if not MD5 in md5:
            md5[MD5] = list()

        md5[MD5].append(chemin)
        dossiersAvecMD5[dossier].append(MD5)

    ratios = dict()

    for dossier in dossiers:
        ratios[dossier] = 0
        for MD5, fichiersCeMD5 in md5.items():
            if len(MD5) > 1:
                for fichier in fichiersCeMD5:
                    if os.path.dirname(fichier) == dossier:
                        ratios[dossier] += 1
                        
        # On divise le nombre de doublons par le nombre de fichiers dans le dossier :
        ratios[dossier] /= len([name for name in os.listdir(dossier) if os.path.isfile(os.path.join(dossier, name))])

    with open("dossiers.json") as f:
        json.dump(ratios, f)

    # # Détermination du pourcentage de doublons dans chaque dossier
    # SQL = """SELECT * FROM Fichiers
    #          WHERE Chemin LIKE "{}%"
    #       """

    # # Maintenant qu'on a un ensemble de dossiers, on le transforme en dictionnaire pour pouvoir stocker les pourcentages de doublons
    # dossiers = {dossier : 0 for dossier in dossiers}
    # for dossier in dossiers:
    #     fichiers = cur.execute(SQL.format(dossier)).fetchall()

    #     totalFichiers = len(fichiers)
    #     totalDoublons = 0

    #     SQL2 = "SELECT * FROM Fichiers WHERE MD5 = ?"
    #     for chemin, md5, _, _, _ in fichiers:
    #         doublons = cur.execute(SQL2, (md5, )).fetchall()

    #         if len(doublons) > 1:
    #             totalDoublons += 1

    #     ratio = totalDoublons / totalFichiers
    #     dossiers[dossier] = ratio
