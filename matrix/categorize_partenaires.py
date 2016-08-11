    #!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import pickle
from collections import Counter

# import edges
partenaires_file="../results/network/ARC5_no_project_nodes.csv"
with open(partenaires_file, "r") as f :
    reader = csv.DictReader(f)
    partners = [node for node in reader if node["type"] == "partenaire"]

print "%s partenaires"%len(partners)

categories=[
{
    "id" : "patrimoine",
    "name" : "Institutions Patrimoniales"
},
{
    "id" : "creation",
    "name" : "Création"
    },
{
    "id" : "médiation",
    "name" :  "Structures Médiatrices"
},
{
    "id" : "cst",
    "name" :  "Culture Scientifique et Technique (CST)"
},
{
    "id" : "enseignement",
    "name" :  "Enseignement & Recherche"
}
]

# import existing results
partner_categories = []
partner_categories_file="partner_categories.txt"
if os.path.isfile(partner_categories_file):
    with open(partner_categories_file, "r") as infile:
        partner_categories = pickle.load(infile)
    print "%s partner categories loaded"%len(partner_categories)

for partner in partners:
    if partner["id"] not in [ p[0] for p in partner_categories]:
        print "-"*10

        manual_check = raw_input("""A quelle catégorie appartient? \n
        [0] : Institutions Patrimoniales (musées, bibliothèques, archives...)
        [1] : Création (théatre, art...)
        [2] : Structures Médiatrices (CCSTI, Arald, OPC, Nacre...)
        [3] : Culture Scientifique et Technique (CST)
        [4] : Enseignement (Ecoles, conservatoire...)\n
        '%s'
        """%partner["name"])

        # assert int(manual_check)
        assert int(manual_check)  < 5

        category  = categories[int(manual_check)]
        print "%s"%(category["name"])

        partner_categories.append( (partner["id"],category["id"]) )

        with open(partner_categories_file, "wb") as outfile:
            pickle.dump(partner_categories, outfile)


def get_partenaire_name(id):
    for part in partners:
        if part["id"] == id : return part["name"]


def get_category_name(id):
    for cat in categories:
        if cat["id"] == id : return cat["name"]


# write to CSV if new records
if len(partner_categories) != len(partners):
    with open('categories_de_partenaires.csv', 'wb') as partners_file:
        wr = csv.writer(partners_file, quoting=csv.QUOTE_ALL)
        wr.writerow(["nom", "catégorie", ])
        for partner in partner_categories:
            name = get_partenaire_name(partner[0])
            cat = get_category_name(partner[1])
            row = [name, cat]
            wr.writerow(row)
    print "saved as categories_de_partenaires.csv"


# parse partenaire
with open(partenaires_file, "r") as f :
    reader = csv.DictReader(f)
    original_nodes = [node for node in reader]


right_cat = { cat[0]  : cat[1] for cat in partner_categories}

print Counter([ c[1] for c in partner_categories])
new_nodes = []
for n in original_nodes:
    if n["id"] in right_cat.keys() :
        n["type"] = right_cat[n["id"]]
        new_nodes.append(n)
    else :
        new_nodes.append(n)

assert len(new_nodes) == len(original_nodes)

# results folder
results_folder = os.path.join(os.getcwd(), "../results/network")
nodes_file_ok="ARC5_no_project_nodes_ok.csv"
with open(os.path.join(results_folder, nodes_file_ok), 'wb') as nodes_file:
    wr = csv.writer(nodes_file, quoting=csv.QUOTE_ALL)
    wr.writerow(["id", "name", "type", "start", "end", "axe"])
    for n in new_nodes:
        row = [n["id"], n["name"], n["type"], n["start"], n["end"], n["axe"]]
        wr.writerow(row)
print "nodes saved as %s"%nodes_file_ok
