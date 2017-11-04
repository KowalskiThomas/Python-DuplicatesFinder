# 10 pour YYYY-MM-DD
if "-" in avantEspace and len(avantEspaceSansTiret) > 10:
    print("Format inconnu pour {}".format(_dossier))
    print("Gestion automatique")
    # Format YYYY-MM-DD-autreChose
    # Comme on n'a pas stocké la description encore, on va juste rappeler la fonction avec un nom de dossier différent
    if avantEspace.count("-") > 3:
        input()
        # On recompose la date
        temp = "-".join(avantEspace.split("-")[0:3])
        # On met un espace pour la suite
        temp2 = "-".join(avantEspace.split("-")[3:])

        _dossier = temp + " " + temp2
        parent = "/".join(dossier.split("/")[:-1])
        return formatterNomDossier(parent + "/" + _dossier)
    
    # Format XX[XX]-MM-autreChose
    elif avantEspace.count("-") == 3:
        split = avantEspace.split("-")
        # Format YYYY-MM-autreChose
        input()
        if len(split[0]) == 4:
            _dossier = split[0] + "-" + split[1] + "-xx " + split[2]
            parent = "/".join(dossier.split("/")[:-1])
            return formatterNomDossier(parent + "/" + _dossier)

        # Format MM-DD-autreChose
        elif len(split[1]) == 2:
            _dossier = split[0] + "-" + split[1] + " " + split[2]
            parent = "/".join(dossier.split("/")[:-1])
            return formatterNomDossier(parent + "/" + _dossier)