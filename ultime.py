import sqlite3
import os
import shutil

print("Copie de la base.")
shutil.copy("Fichiers.s3db", "Fichiers_Work.s3db")

db = sqlite3.connect("Fichiers_Work.s3db")
cur = db.cursor()

def etablirListeDossiers(dossiersTraites = list()):
    dossiers = dict()

    # On vide la table
    # Malheureusement, TRUNCATE TABLE n'existe pas en SQLite
    SQL = "DELETE FROM 'Dossiers'"
    cur.execute(SQL)

    SQL_Fichiers = """SELECT Chemin 
                      FROM Fichiers 
                      WHERE NOT Chemin LIKE '%.ini' 
                      AND   NOT Chemin LIKE '%.tmp'
                      AND   NOT Chemin LIKE '%lrdata%"""

    fichiers = cur.execute(SQL_Fichiers).fetchall()

    for fichier in fichiers:
        d = "\\".join(fichier[0].split("\\")[:-1])
        dossiers[d] = dossiers.get(d, 0) + 1
        
    SQL = "INSERT INTO Dossiers VALUES (?, ?)"
    for chemin, nbFichiers in dossiers.items():
        # On ignore les dossiers vides
        if nbFichiers == 0:
            print("{} est vide".format(chemin))
            continue

        # On ignore les dossiers déjà traités
        if chemin in dossiersTraites:
            continue

        cur.execute(SQL, (chemin, nbFichiers))
        
    db.commit()

dossiersTraites = list()
while "Il reste des dossiers":
    # On récupère le dossier contenant le plus de fichiers
    SQL = "SELECT Chemin FROM Dossiers ORDER BY Fichiers DESC LIMIT 1"

    # On vérifie qu'on a bien un dossier
    resultats = cur.execute(SQL).fetchall()
    if not resultats:
        break
    
    dossier = resultats[0][0]
    print("Traitement de {}".format(dossier))

    # On récupère tous les fichiers de ce dossier
    SQL = """SELECT Chemin, MD5 
             FROM Fichiers 
             WHERE Chemin LIKE ?
             AND   NOT Chemin LIKE '%.ini'
             AND   NOT Chemin LIKE '%.tmp'"""
    fichiers = cur.execute(SQL, (dossier + "%", )).fetchall()

    for chemin, md5 in fichiers:
        # On supprime les doublons de ce fichier
        # print("Traitement de '{}'".format(chemin))
        SQL = """DELETE 
                 FROM Fichiers 
                 WHERE MD5 = ? 
                 AND   NOT Chemin = ?"""
        cur.execute(SQL, (md5, chemin))

    dossiersTraites.append(dossier)
    
    print("Etablissement de la liste des dossiers")
    etablirListeDossiers(dossiersTraites)

    db.commit()

