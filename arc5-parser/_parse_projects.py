#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import json
from fuzzywuzzy import fuzz

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

                # print line["Titre du projet"], montant

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


def new_porteur(nom , tel , mail , etablissement, labo , role):
        porteur = {}
        porteur["nom"] = nom
        porteur["tel"] = tel
        porteur["mail"] = mail
        porteur["labo"] = labo
        porteur["role"] = role
        return porteur 

def find_projet(name):
    for p in projets:
        print name + "|||" +  p["titre"]
    #     if p["titre"] == name : 
    #         return p
    #     else : 
    #         r = fuzz.ratio( p["titre"], name)
    #         if r < 90 : return p


# parse tableau global des projets 
fichier_projets = "tableauDeBord.csv"

projets=[]
theses = []
postdocs = []

with open( os.path.join(dossier, fichier_projets), "r") as f :
    reader = csv.DictReader(f) 

    for line in reader : 

        #init
        projet =  {}

        # parse basic
        projet["id"] = line["Ref"]
        projet["titre"] = line["Titre"]
        projet["year"] = line["Année"]
        projet["axe"] = line["Axe"]

        etablissement = {}
        etablissement["nom"] = line["Etablissements de tutelle – Nom"]
        etablissement["ville"] = line["Etablissements de tutelle – Ville"]
        projet["etablissement"] = etablissement

        projet["equipe"] = []
        porteur = new_porteur(line["PORTEUR(s) DE PROJET – Nom"] + " " + line["PORTEUR(s) DE PROJET – Prénom"], line["PORTEUR(s) DE PROJET – Tél"], line["PORTEUR(s) DE PROJET – Mail"], etablissement["nom"], line["Laboratoires porteurs de projets"], "principal")
        projet["equipe"].append(porteur)

        if line["Type"] == "Thèses" : projet["type"] = "these"
        elif line["Type"] == "pd": projet["type"] = "postdoc"
        else : projet["type"] = "projet"

        if line["Type"] == "Thèses" or line["Type"] == "pd": 

            if line["Co-encadrant / co-porteur – Nom"] != "":
                co_tuteur = new_porteur(line["Co-encadrant / co-porteur – Nom"], line["Co-encadrant / co-porteur – Tel"], line["Co-encadrant / co-porteur – Mail"], line["Co-encadrant / co-porteur – Etablissement"], line["Co-encadrant / co-porteur - Labo"], "co-encadrant" )

            thesard = {}
            thesard["nom"] = line["Bénéficiaire ADR (ou post-doc) – Nom Prénom"]
            thesard["labo"] = line["Bénéficiaire ADR (ou post-doc) – Labo"]
            thesard["tel"] = line["Bénéficiaire ADR (ou post-doc) – Tel"]
            thesard["mail"] = line["Bénéficiaire ADR (ou post-doc) – Mail"]
            projet["thesard"] = thesard

            ecole_doctorale = {}
            ecole_doctorale["Nom"] = line["Ecole doctorale  - Nom"]
            ecole_doctorale["id"] = line["Ecole doctorale  - ID"]
            projet["ecole_doctorale"] = ecole_doctorale

            if co_tuteur is not None : projet["equipe"].append(co_tuteur)

        projets.append(projet)

print "total : %s projets"%len(projets)
# print "%s projets, %s postdocs et %s thèses"%(len(projets), len(postdocs), len(theses))


# parse partenaires
fichier_partenaires= "partenaires.csv"
with open( os.path.join(dossier, fichier_partenaires), "r") as f :
    reader = csv.DictReader(f) 
    # for line in reader:
        # print line["Projet"]
        # print find_projet(line["Projet"])


