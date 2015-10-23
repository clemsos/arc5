#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import json

dossier = "data/csv"
dest_dir = "data/json"


# parse partenaires
fichier_partenaires= "partenaires.csv"

partenaires = []

with open( os.path.join(dossier,  fichier_partenaires), "r") as f :
    reader = csv.DictReader(f) 
    for line in reader:
        partenaire={}
        partenaire["name"]=line["Structure"]
        partenaire["personne_referente"]=line["Personne référente"]
        partenaire["address"]=line["Adresse postale"]
        partenaire["mail"]=line["Mail"]
        partenaire["role"]=line["Qualité - compétences"]
        partenaire["missions"]=line["Missions de la structure"]

        # partenaire["ville"]=line["Ville"]
        # partenaire["projet"]=line["Projet"]
        # partenaire["porteurDuProjet"]=line["Porteur"]

        partenaire["year"]=line["Année"]
        partenaire["axe"]=line["Axe"]
        partenaire["type"]="partenaire"
        partenaire["meta"] = {}
        partenaire["meta"]["partenaire-projet"] = [{ "type" : "projet", "title" : line["Projet"], "meta" : {} }]
        partenaire["meta"]["partenaire-porteur"] = [{ "type" : "personne", "title" : line["Porteur"], "meta" : {}}]
        partenaire["meta"]["partenaire-referente"] = [{ "type" : "personne", "title" : line["Personne référente"], "meta" : {}}]
        partenaire["meta"]["partenaire-ville"]=[{"type" : "ville", "title" : line["Ville"] }]
        partenaires.append(partenaire)

print "total : %s partenaires"%len(partenaires)

with open(os.path.join(dest_dir, "partenaires.json"), 'w') as outfile:
    json.dump(partenaires, outfile, sort_keys = True, indent = 4 )

