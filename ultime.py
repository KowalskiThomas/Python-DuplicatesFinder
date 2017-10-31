import sqlite3
import os
import shutil

print("Copie de la base.")
shutil.copy("Fichiers.s3db", "Fichiers_Work.s3db")

db = sqlite3.connect("Fichiers_Work.s3db")
cur = db.cursor()

def etablirListeDossiers():
    dossiers = dict()

    # On vide la table
    # Malheureusement, TRUNCATE TABLE n'existe pas en SQLite
    SQL = "DELETE FROM 'Dossiers'"
    cur.execute(SQL)

    SQL_Fichiers = """SELECT Chemin 
                      FROM Fichiers 
                      WHERE NOT Chemin LIKE '%.ini' 
                      AND   NOT Chemin LIKE '%.tmp'"""

    fichiers = cur.execute(SQL_Fichiers).fetchall()

    for fichier in fichiers:
        d = "\\".join(fichier[0].split("\\")[:-1])
        dossiers[d] = dossiers.get(d, 0) + 1
        
    SQL = "INSERT INTO Dossiers VALUES ('{}', {})"
    for chemin, nbFichiers in dossiers.items():
        if nbFichiers == 0:
            print("{} est vide".format(chemin))
            continue

        _SQL = SQL.format(chemin.replace("'", "''"), nbFichiers)
        cur.execute(_SQL)
        
    db.commit()

while "Il reste des dossiers":
    # On récupère le dossier contenant le plus de fichiers
    SQL = "SELECT Chemin FROM Dossiers ORDER BY Fichiers DESC LIMIT 1"

    # On vérifie qu'on a bien un dossier
    resultats = cur.execute(SQL).fetchall()
    print(resultats)
    if not resultats:
        break
    
    dossier = resultats[0][0]
    print("Traitement de {}".format(dossier))

    # On récupère tous les fichiers de ce dossier
    SQL = """SELECT Chemin, MD5 
             FROM Fichiers 
             WHERE Chemin LIKE '{}%'
             AND   NOT Chemin LIKE '%.ini'
             AND   NOT Chemin LIKE '%.tmp'""".format(dossier)
    fichiers = cur.execute(SQL).fetchall()

    for chemin, md5 in fichiers:
        # On supprime les doublons de ce fichier
        print("Traitement de '{}'".format(chemin))
        SQL = """DELETE 
                 FROM Fichiers 
                 WHERE MD5 = '{}' 
                 AND   NOT Chemin = '{}'""".format(md5, chemin)
        cur.execute(SQL)

    SQL = "DELETE FROM Dossiers WHERE Chemin = '{}'".format(dossier.replace("'", "''"))
    cur.execute(SQL)

    db.commit()
    
    print("Etablissement de la liste des dossiers")
    etablirListeDossiers()

