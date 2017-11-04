"""
Module de tri pour les photos de mon Lumia 1320 par mois.
C'est avant tout fait pour marcher, même si c'est pas très beau.
"""

import os
import shutil

def formatterDate(Y, M, D, h, m, s):
    return "{}/{}/{} {}:{}:{}".format(Y, M, D, h, m ,s)

racine = "D:/Users/Thomas/Pictures/VERSION PROPRE/Photos Thomas/2014/Photos Lumia"
fichiers = [f for f in os.listdir(racine) if os.path.isfile(racine + "/" + f)]

for f in fichiers:
    _f = f
    f = racine + "/" + f
    # Format
    # WP_20150114_10_55_29_Pro
    # WP_YYYYMMDD_hh_mm_ss_Pro

    try:
        # Format WP_YYYYMMDD_hh_mm_ss[_Pro]
        if "WP_" in f and len(f.split("_")) > 3:
            split = _f.split("_")
            date = split[1]
            heure = split[2]
            minute = split[3]
            seconde = split[4]

            annee = date[0:4]
            mois = date[4:6]
            jour = date[6:8]
           
        # Format WP_YYYYMMDD_XXX 
        elif len(f.split("_")) == 3:
            annee = date[0:4]
            mois = date[4:6]
            jour = date[6:8]      

            heure, minute, seconde = 0, 0, 0

        # Format YYYY_MM_DD_hh_mm_ss
        else:
            split = _f.split("_")
            annee = split[0]
            mois = split[1]
            jour = split[2]
            
            heure = split[3]
            minute = split[4]
            seconde = split[5]

        print(_f, formatterDate(annee, mois, jour, heure, minute, seconde))

        destination = racine + "/" + annee + "-" + mois
        if not os.path.isdir(destination):
            os.mkdir(destination)

        shutil.move(f, destination)
        
    except Exception as e:
        print(_f + " : " + str(e))
        