import json
import datetime

with open("config.json") as f:
    j = json.load(f)
    mediaExtensions = j.get("MediaExtensions", list())

def getRequest(keepPairs = False, filterMedia = False, keepMD5 = False):
    sql = "SELECT Chemin"
    if keepMD5:
        sql += ", MD5"
    
    sql += "\nFROM Fichiers"

    if filterMedia:
        if mediaExtensions:
            sql += "\nWHERE"

        for i, ext in enumerate(mediaExtensions):
            sql += '\n\t{}Chemin LIKE "%.{}"'.format("OR " if i else "", ext)
        
    if not keepPairs:
        sql += "\nGROUP BY MD5"
    
    return sql

def nombreDeDoublons():
    # Récupération du nombre total de fichiers
    SQL = "SELECT COUNT(Chemin) FROM Fichiers"

    # Récupération du nombre de doublons
    SQL = "SELECT COUNT(MD5) FROM (SELECT DISTINCT MD5 FROM Fichiers)"

def joliPoids(x):
    return "{} octets.".format(x)

def tailleTotaleDesDoublons():
    # Récupération de la somme des tailles (en octets)
    SQL = """SELECT SUM(Size) 
             FROM (
                SELECT MD5, Chemin, Size 
                FROM Fichiers 
                GROUP BY MD5
             )"""

    somme = cur.execute(SQL).fetchall()[0]

    # Renvoi de la taille joliment :
    return joliPoids(somme)
