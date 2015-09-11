#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import json

dossier = "data/csv"
dest_dir = "data/json"

fichiers = ["2012_projets.csv", "2013_projets.csv"]

total = 0
subventions = []

def parse_subventions(fichier) : 
    year = fichier[:4]
    with open( os.path.join(dossier, fichier), "r") as f :
        reader = csv.DictReader(f) 

        for line in reader :
            if "ARC N° 05" in line["Objet de l'opération"] : 

                # print line["Montant en euros sur dépenses éligibles HT"]
                try :
                    montant = int( line["Montant en euros sur dépenses éligibles HT"][:-3])
                except ValueError:
                    print "ERROR ", line["Montant en euros sur dépenses éligibles HT"]

                subvention = {}
                subvention["year"] = year
                subvention['montant'] = montant
                subvention["labo"] = line["Nom du laboratoire"]
                subvention["univ"] = line["Nom bénéficiaire"]
                subvention["chercheur"] = line["Nom du chercheur"]
                subvention["projet"] = line["Titre du projet"]
                subvention["subventionId"] = line["N° subvention"]

                subventions.append(subvention)

for fichier in fichiers  : 
    parse_subventions(fichier) 
    print "%s subventions in %s"%(len(subventions), fichier)

print "Total : %s subventions."%(len(subventions))

with open(os.path.join(dest_dir, "subventions.json"), 'w') as outfile:
    json.dump(subventions, outfile, sort_keys = True, indent = 4 )
