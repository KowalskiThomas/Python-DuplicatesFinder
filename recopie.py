import sqlite3
import shutil
import os

shutil.copy("Fichiers_Work.s3db", "Fichiers_Copie.s3db")

db = sqlite3.connect("Fichiers_Copie.s3db")
cur = db.cursor()

SQL = "SELECT Chemin FROM Fichiers LIMIT 250"
SQL_DELETE = "DELETE FROM Fichiers WHERE Chemin = ?"
while "Il reste des fichiers à copier":
    resultats = cur.execute(SQL).fetchall()

    if not resultats:
        break

    for fichier in cur.execute(SQL).fetchall():
        fichier = fichier[0]

        cheminRelatif = fichier.replace("D:\\Users\\Thomas\\Pictures", "")
        nouveauChemin = "D:\\Users\\Thomas\\Pictures\\Version propre" + cheminRelatif

        if not os.path.isdir(os.path.dirname(nouveauChemin)):
            os.makedirs(os.path.dirname(nouveauChemin))

        print("Copie de {}".format(fichier))
        shutil.copy(fichier, nouveauChemin)

        cur.execute(SQL_DELETE, (fichier, ))

    db.commit()
