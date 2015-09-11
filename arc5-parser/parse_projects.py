#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import json

dossier = "data/csv"
dest_dir = "data/json"

def new_porteur(nom , tel , mail , etablissement, labo , role):
        porteur = {}
        porteur["name"] = nom
        porteur["tel"] = tel
        porteur["mail"] = mail
        porteur["labo"] = labo
        porteur["role"] = role
        return porteur 


# parse tableau global des projets 
fichier_projets = "tableauDeBord.csv"

projets = []

data = {};
data["projets"]=[]
data["theses"] = []
data["postdocs"] = []
data["personnes"]=[]
data["ecole-doctorales"]=[]
data["etablissements"]=[]

def add_to_data(name, type):
    if(name not in data[type]) : data[type].append(name)

# def add_edge(source, target, type, start, end):
    

with open( os.path.join(dossier, fichier_projets), "r") as f :
    reader = csv.DictReader(f) 

    for line in reader : 

        #init
        projet =  {}

        # parse basic
        projet["id"] = line["Ref"]
        projet["name"] = line["Titre"]
        projet["year"] = line["Année"]
        projet["axe"] = line["Axe"]


        etablissement = {}
        etablissement["name"] = line["Etablissements de tutelle – Nom"]
        etablissement["ville"] = line["Etablissements de tutelle – Ville"]
        projet["etablissement"] = etablissement

        add_to_data(etablissement, "etablissements")

        projet["equipe"] = []
        porteur = new_porteur(line["PORTEUR(s) DE PROJET – Nom"] + " " + line["PORTEUR(s) DE PROJET – Prénom"], line["PORTEUR(s) DE PROJET – Tél"], line["PORTEUR(s) DE PROJET – Mail"], etablissement["name"], line["Laboratoires porteurs de projets"], "principal")
        projet["equipe"].append(porteur)

        add_to_data(porteur, "personnes")

        if line["Type"] == "Thèses" : projet["type"] = "these"
        elif line["Type"] == "pd": projet["type"] = "postdoc"
        else : projet["type"] = "projet"

        if line["Type"] == "Thèses" or line["Type"] == "pd": 

            if line["Co-encadrant / co-porteur – Nom"] != "":
                co_tuteur = new_porteur(line["Co-encadrant / co-porteur – Nom"], line["Co-encadrant / co-porteur – Tel"], line["Co-encadrant / co-porteur – Mail"], line["Co-encadrant / co-porteur – Etablissement"], line["Co-encadrant / co-porteur - Labo"], "co-encadrant" )
                
                add_to_data(co_tuteur, "personnes")


            thesard = {}
            thesard["name"] = line["Bénéficiaire ADR (ou post-doc) – Nom Prénom"]
            thesard["labo"] = line["Bénéficiaire ADR (ou post-doc) – Labo"]
            thesard["tel"] = line["Bénéficiaire ADR (ou post-doc) – Tel"]
            thesard["mail"] = line["Bénéficiaire ADR (ou post-doc) – Mail"]
            projet["thesard"] = thesard

            add_to_data(thesard, "personnes")


            ecole_doctorale = {}
            ecole_doctorale["name"] = line["Ecole doctorale  - Nom"]
            ecole_doctorale["id"] = line["Ecole doctorale  - ID"]
            projet["ecole_doctorale"] = ecole_doctorale

            add_to_data(ecole_doctorale, "ecole-doctorales")

            if co_tuteur is not None : projet["equipe"].append(co_tuteur)

        if projet["type"] == "these" : data["theses"].append(projet)
        elif projet["type"] == "postdoc" : data["postdocs"].append(projet)
        elif projet["type"] == "projet" : data["projets"].append(projet)

        projets.append(projet)

print "total : %s projets"%len(projets)
# print "%s projets, %s postdocs et %s thèses"%(len(data["projets"]), len(data["postdocs"]), len(data["theses"]))

for key in data : 
    print "%s %s"%(len(data[key]), key)

def write_to_json(data, filename):
    with open(os.path.join(dest_dir, filename), 'w') as outfile:
        json.dump(data, outfile, sort_keys = True, indent = 4 )

# write_to_json(projets, "projects.json")

for key in data:
    write_to_json(data[key], "%s.json"%key)
