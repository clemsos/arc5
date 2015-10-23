#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import json
from slugify import slugify

dossier = "data/csv"
dest_dir = "data/json"

# parse tableau global des items 
fichier_items = "tableauDeBord.csv"

items = []

data = {};
data["projets"]=[]
data["theses"] = []
data["postdocs"] = []
data["personnes"]=[]
data["ecole-doctorales"]=[]
data["etablissements"]=[]
data["laboratoires"]=[]

def add_to_data(name, type):
    if(name not in data[type]) : data[type].append(name)

def new_personne(nom , tel , mail , etablissement, labo , role):
        personne = {}
        personne["type"] = "personne"
        personne["title"] = nom
        personne["slug"] = slugify(nom)
        personne["tel"] = tel
        personne["mail"] = mail
        personne["etablissement"] = etablissement
        personne["labo"]  = labo
        personne["role"] = role
        return personne 

def new_etablissement(name, city ):
        etablissement = {}
        etablissement["type"] = "etablissement"
        etablissement["title"] = name
        etablissement["slug"] = slugify(name)
        etablissement["city"] = city
        etablissement["meta"] = {}
        return etablissement

#"nom_des_porteurs", "chercheur", "partenaires", "laboratoire" ,"etablissements_gestionnaires"

def new_projet(projet, nom_des_porteurs, chercheur, partenaires, laboratoire, etablissements_gestionnaires):
    projet["meta"]["projet-nom_des_porteurs"] = nom_des_porteurs
    projet["meta"]["projet-chercheur"] = [chercheur]
    projet["meta"]["projet-partenaires"] = [partenaires]
    projet["meta"]["projet-laboratoire"] = [laboratoire]
    projet["meta"]["projet-etablissements_gestionnaires"] = [etablissements_gestionnaires]
    return projet

def new_these(these, doctorant, laboratoire, etablissement, ecole_doctorale, partenaire, directeur, coencadrant ):
    these["meta"]["these-doctorant"]=[doctorant]
    these["meta"]["these-laboratoire"]=[laboratoire]
    these["meta"]["these-etablissement"]=[etablissement]
    these["meta"]["these-ecole-doctorale"]=[ecole_doctorale]
    these["meta"]["these-partenaire"]=[partenaire]
    these["meta"]["these-directeur"]=[directeur]
    these["meta"]["these-coencadrant"]=[coencadrant]
    return these

def new_labo(labo_name):
    labo = {}
    labo["title"] = labo_name
    labo["type"] = "laboratoire"
    return labo

with open( os.path.join(dossier, fichier_items), "r") as f :
    reader = csv.DictReader(f) 

    for line in reader : 

        #init
        item =  {}

        # parse basic
        item["id"] = line["Ref"]
        item["title"] = line["Titre"]
        item["slug"] = slugify(line["Titre"])
        item["year"] = line["Année"]
        item["axe"] = line["Axe"]

        item["meta"] = {}
        item["meta"]["acronyme"] = ""
        item["meta"]["site"] = ""

        if line["Type"] == "Thèses" : item["type"] = "these"
        elif line["Type"] == "pd": item["type"] = "postdoc"
        else : item["type"] = "projet"

        # parse etablissements
        etablissement = new_etablissement(line["Etablissements de tutelle – Nom"], line["Etablissements de tutelle – Ville"])
        item["etablissement"] = etablissement
        add_to_data(etablissement, "etablissements")

        # parse personnes
        equipe = []
        porteur = new_personne(line["PORTEUR(s) DE PROJET – Nom"] + " " + line["PORTEUR(s) DE PROJET – Prénom"], line["PORTEUR(s) DE PROJET – Tél"], line["PORTEUR(s) DE PROJET – Mail"], etablissement["title"], line["Laboratoires porteurs de projets"], "principal")
        equipe.append(porteur)
        add_to_data(porteur, "personnes")

        laboratoire = new_labo(line["Laboratoires porteurs de projets"])
        add_to_data(laboratoire, "laboratoires")


        if line["Co-encadrant / co-porteur – Nom"] != "":
            co_porteur = new_personne(line["Co-encadrant / co-porteur – Nom"], line["Co-encadrant / co-porteur – Tel"], line["Co-encadrant / co-porteur – Mail"], line["Co-encadrant / co-porteur – Etablissement"], line["Co-encadrant / co-porteur - Labo"], "co-encadrant" )
            equipe.append(co_porteur)
            add_to_data(co_porteur, "personnes")

        # these
        if item["type"] == "these": 

            # new_personne(nom , tel , mail , etablissement, labo , role)
            thesard = new_personne(line["Bénéficiaire ADR (ou post-doc) – Nom Prénom"], line["Bénéficiaire ADR (ou post-doc) – Tel"], line["Bénéficiaire ADR (ou post-doc) – Mail"], etablissement, line["Bénéficiaire ADR (ou post-doc) – Labo"], "doctorant")
            # item["thesard"] = thesard
            add_to_data(thesard, "personnes")

            # ecole doctorale
            ecole_doctorale = {}
            ecole_doctorale["title"] = line["Ecole doctorale  - Nom"]
            ecole_doctorale["id"] = line["Ecole doctorale  - ID"]
            ecole_doctorale["type"] = "ecole-doctorale"
            item["ecole_doctorale"] = ecole_doctorale
            add_to_data(ecole_doctorale, "ecole-doctorales")

            # date "YYYYMMDD"
            if(line["Année de thèse – 2012-2013"]):
                item["meta"]["date_debut"] = "20120101"
                item["meta"]["date_fin"] = "20150101"

            if co_porteur is not None : equipe.append(co_porteur)

            # def new_these(these, doctorant, laboratoire, etablissement, ecole_doctorale, partenaire, directeur, coencadrant ):
            these = new_these(item, thesard, None, etablissement, ecole_doctorale, None, porteur, co_porteur )
            data["theses"].append(these)

        elif item["type"] == "projet" : 
            # new_projet(projet, nom_des_porteurs, chercheur, partenaires, laboratoire, etablissements_gestionnaires):
            projet = new_projet(item, equipe, porteur, "", laboratoire, etablissement)
            data["projets"].append(item)

        elif item["type"] == "postdoc" : 
            data["postdocs"].append(item)

        items.append(item)

# log results
print "total : %s items"%len(items)
for key in data : 
    print "%s %s"%(len(data[key]), key)

def write_to_json(data, filename):
    with open(os.path.join(dest_dir, filename), 'w') as outfile:
        json.dump(data, outfile, sort_keys = True, indent = 4 )

# write_to_json(items, "projects.json")

for key in data:
    write_to_json(data[key], "%s.json"%key)
