import os
import recherche

chemin = "D:/Users/Thomas/Pictures/VERSION PROPRE/AData/Sauvegarde Toshiba"

f = open("log.txt", 'w')
for dossier in os.listdir(chemin):
    _dossier = dossier
    dossier = chemin + "/" + dossier

    dates = set()

    for fichier in os.listdir(dossier):
        try:
            _fichier = fichier
            fichier = dossier + "/" + fichier
            t = recherche.date(fichier)
            if not t is None:
                dates.add(t.split(" ")[0])
        except:
            pass

    f.write(_dossier + "\n")
    for d in dates:
        f.write(d + "\n")

    f.write("\n")

f.close()
