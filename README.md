# Doublons

Ce script permet de trouver les doublons dans un ensemble de dossiers (en se basant sur les sommes MD5 des fichiers). 

Les MD5 de tous les fichiers analysés sont stockés dans une base de données SQLite3. Il est ensuite possible d'appliquer un traitement automatique ou de définir son propre algorithme de tri, puisqu'il suffit de récupérer les informations de fichiers *a posteriori* dans la base de données.

# Fonctionnement

Pour lancer une première recherche, on peut soit donner une liste de dossiers au script, soit remplir un fichier JSON.

**Pour fournir les dossiers au script :**

    python recherche.py C:\ "D:\Photos"

**Pour utiliser `config.json` :**

```json
{
    "Dossiers" : 
    [
        "C:\\",
        "D:\\Photos"
    ]
}
```

Puis

    python recherche.py config

L'utilisation d'un fichier JSON permet de reprendre la recherche à tout moment en appellant tout simplement `python recherche.py`.

Le script prend deux arguments facultatifs : `config` pour utiliser le fichier JSON, `reset` pour supprimer la base de données existante (si elle existe) avant le démarrage de la recherche.

# Récupération des données 

Pour extraire tous les doublons / multiples copies d'un même fichier, on peut utiliser plusieurs instructions SQL différentes. 
Plusieurs sont proposées dans les exemples d'algorithmes de tri. 

**Renvoyer la liste des MD5 dont le fichier a au moins deux copies :**

```sql
SELECT MD5 
FROM Fichiers
GROUP BY MD5
HAVING COUNT(MD5) > 1
```

Puis, on peut récupérer les chemins pour chaque fichier avec 

```sql
SELECT Chemin FROM Fichiers WHERE MD5 = ?
```

En remplaçant `?` par le MD5 en question.