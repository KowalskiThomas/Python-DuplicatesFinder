import sqlite3

SQL = "INSERT INTO Dossiers VALUES ('{}', {})"

db = sqlite3.connect("fichiers.s3db")
cur = db.cursor()

dossiers = dict()

SQL_Fichiers = "SELECT chemin FROM Fichiers WHERE NOT Chemin LIKE '%.ini'"

fichiers = cur.execute(SQL_Fichiers).fetchall()

for fichier in fichiers:
    d = "\\".join(fichier[0].split("\\")[:-1])
    dossiers[d] = dossiers.get(d, 0) + 1
	
for k, v in dossiers.items():
    _SQL = SQL.format(k.replace("'", "''"), v)
    print(_SQL)
    cur.execute(_SQL)
	
db.commit()
