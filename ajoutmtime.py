import sqlite3
import os
import datetime

def connect():
    # On se connecte à la base de données et on récupère le curseur
    db = sqlite3.connect("Fichiers.s3db")
    cur = db.cursor()

    return db, cur

db, cur = connect()

SQL = "SELECT * FROM Fichiers"
resultats = cur.execute(SQL).fetchall()

SQL = "UPDATE Fichiers SET DateModification = ? WHERE Chemin = ?"
for i, chemin, _, _, _, _ in enumerate(resultats):
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(chemin)).strftime("%Y/%m/%d %H:%M:%S")
    cur.execute(SQL, (mtime, chemin))

    if i % 500 == 0:
        db.commit()
        
db.commit()