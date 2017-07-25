"""
Module dédié au traitement des doublons.
On récupère les données stockées dans la BDD et on fait des choses intéressantes avec.
"""

import sqlite3

def traitement():
    """
    Ouvre la base de données et cherche les doublons à partir de celle-ci.
    Ecrit dans un fichier log.txt au fur et à mesure que la fonction trouve les doublons.
    """

    # On se connecte à la base de données et on récupère le curseur
    db = sqlite3.connect("Fichiers.s3db")
    cur = db.cursor()

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

# Si on appelle le fichier directement (pas appelé si on importe le module)
if __name__ == "__main__":
    traitement()
