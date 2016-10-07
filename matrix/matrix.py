    #!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import json
import scipy as sp
import networkx as nx
from difflib import get_close_matches
from collections import Counter
import itertools
import argparse
import pickle
import os

# results folder
results_folder = os.path.join(os.getcwd(), "../results/network")

# create empty (undirected) graph
G=nx.Graph()

excluded_nodes = ["", "imaginove", "ardi"]
node_types = ["ville", "projet", "etablissement", "these", "ecole-doctorale", "partenaire"]

print "#"*10
print "ORIGINAL NETWORK"
print "-"*10

# import edges
edges_file="../mongoexport/edges.csv"
with open(edges_file, "r") as f :
    reader = csv.DictReader(f)
    for edge in reader :
        if edge["source"] not in excluded_nodes and edge["target"] not in excluded_nodes:
            G.add_edge(edge["source"], edge["target"], {'type' : edge['type']})

# import nodes
nodes_file="../mongoexport/nodes.csv"
with open(nodes_file, "r") as f :
    reader = csv.DictReader(f)
    for node in reader :
        if node["slug"] not in excluded_nodes:
            G.add_node(node["slug"], node)
        else :
            print "" #excluded_nodes

node_types = Counter([ g[1]["type"] for g in G.nodes(data=True) ])
edge_types = Counter([ g[2]["type"] for g in G.edges(data=True) ])
print "%s nodes : %s "%(len(G.nodes()),node_types)
print "%s edges: %s"%(len(G.edges()),edge_types)

# print Counter([ g[1]["start"] for g in G.nodes(data=True) ])
# print "project dates : %s"%Counter([ n[1]["start"] for n in G.nodes(data=True) if n[1]["type"] == "these" or n[1]["type"] == "projet"])


### check for similar nodes
print
print "#"*20
print "DELETE DUPLICATES"

matches = []
if os.path.isfile("matches.txt"):
    with open("matches.txt", "r") as infile:
        matches = pickle.load(infile)
    print "%s duplicate nodes loaded"%len(matches)

# get all similar nodes
similars = []
if os.path.isfile("raw_similar_words.txt"):
    with open("raw_similar_words.txt", "r") as infile:
        similars = pickle.load(infile)

# get a list of similar words
node_types
if len(similars) == 0:
    for node in G.nodes() :
        is_anon = False
        nodes = [ n for n in G.nodes() ]
        nodes.remove(node) # don't check for similarity with itself !
        for t in node_types :
            if node.startswith(t):
                is_anon = True
        if not is_anon:
            # check if name is similar
            similar = get_close_matches(node, nodes)
            # check if has the same type
            if len(similar) > 0 :
                for s in similar:
                    # check if similar type
                    if G.node[node]["type"] == G.node[s]["type"]:
                        # print set([node,s])
                        if set([node,s]) not in similars :
                            similars.append(set([node,s]))

if not os.path.isfile("raw_similar_words.txt"):
    with open("raw_similar_words.txt", "wb") as outfile:
        pickle.dump(similars, outfile)
    print "-"*10
    print "%s similar nodes"%len(similars)


if not len(matches):
    for i, sim in enumerate(similars):
        print "---------- %s/%s"%(i, len(similars))
        if sim not in matches:
            source = tuple(sim)[0]
            target = tuple(sim)[1]

            # manually check if similar

            manual_check = raw_input("Are those words similar (y/n)?  \n '%s' \n '%s' ?: "%(source, target))
            if manual_check == "y":
                print "they are similar"
                matches.append( (source , target) )
                with open("matches.txt", "wb") as outfile:
                    pickle.dump(matches, outfile)
            else :
                print "they are not similar"
        else :
            print "already processed"

    print "%s names that match "%len(matches)

print "-"*10

duplicates_nodes = []
match_index = { m[0]:m[1] for m in matches }
match_reverse_index = { m[1]:m[0] for m in matches }

# merge nodes and edges that match
match_series = {}
matched = []
for m in matches:

    # add corresponding
    if m[0] not in matched : # check if is already existing
        try :
            match_series[m[0]].append(m[1])
        except KeyError:
            match_series[m[0]] = []
            match_series[m[0]].append(m[1])

        # flag as already matched
        matched.append(m[0])
        matched.append(m[1])

        # get corresponding of corresponding
        try:
            w = match_index[m[1]]
            if w not in matched :
                match_series[m[0]].append(w)
                matched.append(w)
        except KeyError:
            pass

        try:
            w = match_reverse_index[m[0]]
            if w not in matched :
                match_series[m[0]].append(w)
                matched.append(w)
        except KeyError:
            pass

        # get reserve value
        try:
            w = match_reverse_index[m[1]]
            if w not in matched :
                match_series[m[0]].append(w)
                matched.append(w)
        except KeyError:
            pass

print "%s unique nodes in %s matching groups"%(len(matched), len(match_series))

# create clean graph
clean_G = nx.Graph()

duplicates_nodes = []
clean_names = {}

# remove useless names
villes = ["grenoble", "lyon", "valence", "brou", "etienne"]
ville_names = {
    "grenoble" : "Grenoble",
    "lyon" : "Lyon",
    "valence" : "Valence",
    "brou" : "Bourg-en-Bresse",
    "etienne" : "St-Etienne"
    }

for n in G.nodes(data=True):
    m = n[1]["slug"]

    # ignore node of degree zero
    if G.degree(m) == 0:
        excluded_nodes.append(m)

    #parse city name
    elif m.startswith("ville-"):
        for e in G.edges(m):
            hasVille = [v for v in villes if v in e[1].lower() ] # wild guess of city name from edges info
        if hasVille :
            clean_names[m] = hasVille[0] # first city in the list
            duplicates_nodes.append(m)
        else :
            excluded_nodes.append(m)

    # excludes unnamed projects and partenaires
    elif m.startswith("projet-") or m.startswith("partenaire-") or m.startswith("ecole-doctorale"):
        excluded_nodes.append(m)

    # get clean names
    elif m in match_series:
        # clean_names[m]
        # arbitrary select first item as the good node
        clean_names[m] = m
        similar_nodes = list(set(match_series[m]))

        for node in similar_nodes:
            clean_names[node] = m

        # store nodes that have been deleted
        duplicates_nodes += similar_nodes

print "%s duplicate nodes"%len(duplicates_nodes)
print "%s excluded nodes (unknown or singleton)"%len(excluded_nodes)

# print [ G.node[ x ] for x in duplicates_nodes ]

# parse nodes for the whole graph
for n in G.nodes():
    if n not in clean_names.keys() and n not in duplicates_nodes:
        clean_names[n] = n

# get only clean nodes and edges
for n in G.nodes(data=True):
    if n[0] not in excluded_nodes:
        real_name = clean_names[n[0]]

        data = n[1]
        if real_name in villes :
            data["name"]= ville_names[real_name]

        # store information from the previous node
        if real_name != n[0]: # if changes
            if G.node[n[0]]["start"] != "" :
                data["start"] = G.node[n[0]]["start"]
            if G.node[n[0]]["end"] != "" :
                data["end"] = G.node[n[0]]["end"]

            # if G.node[n[0]]["type"] == "projet" :
            #     print G.node[n[0]]["start"], data["start"]
            #     print G.node[real_name]["start"]

        clean_G.add_node(real_name, data) # add clean nodes to the graph

print "dates des projets avant :%s " % Counter([ n[1]["start"] for n in G.nodes(data=True) if n[1]["type"] == "projet"])
print "nombre de projets avec date avant :%s " % len([ n for n in G.nodes(data=True) if n[1]["type"] == "projet" and n[1]["start"] != ""])

print "dates des projets :%s " % Counter([ n[1]["start"] for n in clean_G.nodes(data=True) if n[1]["type"] == "projet"])
print "dates des theses :%s " % Counter([ n[1]["start"] for n in clean_G.nodes(data=True) if n[1]["type"] == "these"])


for e in G.edges(data=True):
    if e[0] not in excluded_nodes and e[1] not in excluded_nodes:
        source = clean_names[e[0]]
        target = clean_names[e[1]]
        clean_G.add_edge(source, target, e[2] ) # rename edges properly and add to the graph

print set.intersection(set(clean_G.nodes()), set(excluded_nodes))
# make sure that no deleted node is present in the final graph
assert len(set.intersection(set(clean_G.nodes()), set(duplicates_nodes))) == 0
assert len(set.intersection(set(clean_G.nodes()), set(excluded_nodes))) == 0

print "-"*10
print "%s nodes merged"%(len(G.nodes())-len(clean_G.nodes()))
print "%s edges merged"%(len(G.edges())-len(clean_G.edges()))
print "%s nodes after fix duplicate"%len(clean_G.nodes())
print "%s edges after fix duplicate"%len(clean_G.edges())

# print Counter([ g[1]["start"] for g in clean_G.nodes(data=True) ])
# print Counter([n[1]["type"] for n in clean_G.nodes(data=True)])

with open(os.path.join(results_folder,'ARC5_merged_nodes_with_names.csv'), 'wb') as metrics_file:
    wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
    wr.writerow(["id", "name", "type", "start", "end", "axe"])
    for n in clean_G.nodes(data=True):
        data = n[1]
        row = [n[0], data["name"], data["type"], data["start"], data["end"], data["axe.id"]]
        wr.writerow(row)
print "nodes saved as ARC5_merged_nodes_with_names.csv"

## save graph to a CSV file
with open(os.path.join(results_folder,'ARC5_merged_edges_with_names.csv'), 'wb') as metrics_file:
    wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
    wr.writerow(["source", "target", "type"])
    for n in clean_G.edges(data=True):
        data = n[2]
        row = [n[0], n[1], data["type"]]
        wr.writerow(row)
print "nodes saved as ARC5_merged_nodes_with_names.csv"


### some metrics

nodes_projects = [node[0] for node in clean_G.nodes(data=True) if node[1]["type"] == "projet"  or node[1]["type"] == "project"]

nodes_theses = [node[0] for node in clean_G.nodes(data=True) if node[1]["type"] == "these"]

count_partenaires_par_projet = []
for p in nodes_projects:
    # print p
    adjacent_nodes_types = [ clean_G.node[n[1]]["type"] for n in clean_G.edges(p)]
    # print Counter(adjacent_nodes_types)["partenaire "]
    count_partenaires_par_projet.append(Counter(adjacent_nodes_types)["partenaire"])

# print Counter(count_partenaires_par_projet)

# print nodes_theses
count_persons_par_these = []
for p in nodes_theses:
    # print p
    adjacent_nodes_types = [ clean_G.node[n[1]]["type"] for n in clean_G.edges(p)]
    # print Counter(adjacent_nodes_types)["personne"]
    count_persons_par_these.append(Counter(adjacent_nodes_types)["personne"])

# print Counter(count_persons_par_these)

#### convert persons to edges
print
print "#"*20
print "CONVERT PERSONS TO EDGES"

persons = [node[0] for node in clean_G.nodes(data=True) if node[1]["type"] == "personne"]
projects_theses_edges = clean_G.edges(persons, data=True)
# print "%s persons linked to %s edges"%(len(persons), len(projects_theses_edges))

for person in persons:

    # edges for a single person
    project_these_edges = clean_G.edges(person)
    # print "%s : %s edges "%(person, len(project_these_edges))

    # get all nodes linked by a single person
    list_of_person_nodes = []; map(list_of_person_nodes.extend, map(list,project_these_edges))
    assert len(list_of_person_nodes) == len(project_these_edges)*2 # make sure we have all nodes

    clean_nodes = [n for n in list_of_person_nodes if n != person]
    assert len(clean_nodes) == len(project_these_edges) # make sure we have all new nodes, except the person

    if len(project_these_edges) > 2 : # if have less than degree of 1 then remove node

        # get data to add to the edge
        data = clean_G.node[person]

        # delete person info
        data.pop("slug")
        data.pop("name")

        # create new edges between all those
        new_edges = list(itertools.combinations(clean_nodes, 2))

        # print [G[n]["start"] in clean_nodes]
        # if n[1]["end"] : print n[1]["end"]
        for e in new_edges:
            clean_G.add_edge( e[0], e[1], {"type" : "personne"} )

    # remove person from the graph
    clean_G.remove_node(person)

assert len(set.intersection(set(persons), set(clean_G.nodes() ))) == 0
assert "personne" not in [ n[1]["type"] for n in clean_G.nodes(data=True)]
print "-"*10
print "%s nodes after conversion of person from nodes to edges"%len(clean_G.nodes())
print "%s edges after conversion of person from nodes to edges"%len(clean_G.edges())

print Counter([ g[1]["type"] for g in clean_G.nodes(data=True) ])
print Counter([ g[1]["start"] for g in clean_G.nodes(data=True) if g[1]["type"] == "projet"])
#
# print
# print "#"*10
# print "SAVE CLEAN VERSIONS"
# print

# # change edges types
# final_edges_types = Counter([n[2]["type"] for n in clean_G.edges(data=True)])
# print "final edges types : %s"%final_edges_types
#
# ## save graph to a CSV file
# with open(os.path.join(results_folder,'ARC5_edges_wrapup.txt'), 'wb') as wrapup_file:
#     wrapup_file.write("Types of edges\n")
#     wrapup_file.write("---\n")
#     for e in final_edges_types:
#         line = "%s : %s edges \n"%(e, final_edges_types[e])
#         wrapup_file.write(line)
#
# clean_edge_types = {
#     'ville' : "dans la ville de " ,
#     'doctorant' : "en thèse",
#     'personne' : "est membre de",
#     'laboratoire' : "hebergé par le laboratoire",
#     'etablissement' : "gère",
#     'etablissements_gestionnaires' : "gère",
#     'projet' : "travaille avec",
#     'partenaire' : "est partenaire de",
#     'ecole-doctorale' : "fait sa thèse à",
#     "common_projects" : "ont des projets ou thèses communes"
# }
#
# ## save graph to a CSV file
# with open(os.path.join(results_folder,'ARC5_anonymous_edges.csv'), 'wb') as metrics_file:
#     wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
#     wr.writerow(["source", "target", "type", "name"])
#     for n in clean_G.edges(data=True):
#         data = n[2]
#         # print data
#         row = [n[0], n[1], data["type"], clean_edge_types[data["type"]] ]
#         wr.writerow(row)
#
# print "edges saved as ARC5_anonymous_edges.csv"

# with open(os.path.join(results_folder,'ARC5_anonymous_nodes.csv'), 'wb') as metrics_file:
#     wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
#     wr.writerow(["id", "name", "type", "start", "end", "axe"])
#     for n in clean_G.nodes(data=True):
#         data = n[1]
#         row = [n[0], data["name"], data["type"], data["start"], data["end"], data["axe.id"]]
#         wr.writerow(row)
# print "nodes saved as ARC5_anonymous_nodes.csv"
#
#
# print
# print "#"*10
# print "CENTRALITY METRICS"
# ## calculate centrality metrics:
# degree = nx.degree_centrality(clean_G)
# print "-- degree"
# between = nx.betweenness_centrality(clean_G)
# print "-- betweenness_centrality"
# close = nx.closeness_centrality(clean_G)
# print "-- closeness_centrality"
#
# ## save the multiple centrality metrics to a CSV file
# with open(os.path.join(results_folder,'ARC5_network_metrics.csv'), 'wb') as metrics_file:
#     wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
#     wr.writerow(["name", "degree", "betweenness_centrality", "closeness_centrality"])
#     for n in clean_G:
#         wr.writerow([clean_G.node[n]["name"], degree[n], between[n], close[n]])
#
# print "Values saved to network_metrics.csv"
#
# print
# print "#"*10
# print "HUMAN READABLE VERSION"
#
# with open(os.path.join(results_folder,'ARC5_human_readable.txt'), 'wb') as metrics_file:
#     for n in clean_G.edges(data=True):
#         line =  "'%s' %s '%s' \n\n"%(clean_G.node[n[1]]["name"], clean_edge_types[data["type"]], clean_G.node[n[0]]["name"])
#         metrics_file.write(line)


#### convert project to edges
print
print "#"*20
print "CONVERT PROJECT + THESES TO EDGES"

projects_theses = [ node for node in clean_G.nodes(data=True) if node[1]["type"] == "projet" or node[1]["type"] == "these" or node[1]["type"] == "project" ]
projects_theses_edges = clean_G.edges([n[0] for n in projects_theses], data=True)
# print "%s persons linked to %s edges"%(len(projects_theses), len(projects_theses_edges))

print "number of projects without a date %s"%len([ p for  p  in projects_theses if p[1]["start"] == ""])

for proj in projects_theses:
    p = proj[0]
    data = proj[1]
    start = proj[1]["start"]
    end = proj[1]["end"]

    # edges for a single project or these
    project_these_edges = clean_G.edges(p)
    # print "%s : %s edges "%(person, len(project_these_edges))

    # get all nodes linked by a single person
    list_of_person_nodes = []; map(list_of_person_nodes.extend, map(list,project_these_edges))
    assert len(list_of_person_nodes) == len(project_these_edges)*2 # make sure we have all nodes

    clean_nodes = [n for n in list_of_person_nodes if n != p]
    assert len(clean_nodes) == len(project_these_edges) # make sure we have all new nodes, except the person

    if len(project_these_edges) > 2 : # if have less than degree of 1 then remove node

        # get data to add to the edge
        # data = clean_G.node[p]

        # create new edges between all those
        new_edges = list(itertools.combinations(clean_nodes, 2))
        for e in new_edges:
            p_name = "'%s : %s'"%(data["type"],data["name"])
            try:
                clean_G[ e[0] ][ e[1] ]["additionalData"].append(p_name)
            except :
                clean_G.add_edge( e[0], e[1],
                {
                "type" : "projects",
                "additionalData": [p_name],
                "name" : "projets ou thèses en commun"
                })

            # print clean_G.node[e]
            # if clean_G.node[e[1]]["start"] == "" or start < clean_G.node[e[1]]["start"] :
            #     clean_G.node[e[1]]["start"] = start
            #
            # if clean_G.node[e[0]]["start"] == "" or start < clean_G.node[e[0]]["start"] :
            #                 clean_G.node[e[0]]["start"] = start

    # # update date info on other nodes
    # for e in clean_G[p]:
    #     print start
    #     # print clean_G.node[e]
        # if clean_G.node[e]["start"] == "" or start < clean_G.node[e]["start"] :
        #     clean_G.node[e]["start"] = start
        #     prin start
        #     print "add date : %s"%start
        # else : print "--- %s"%clean_G.node[e]["start"]

    # remove person from the graph
    clean_G.remove_node(p)

print "nodes time distribution : %s"%Counter([ n[1]["start"] for n in clean_G.nodes(data=True) ])
print "types of nodes without a date info : %s"%Counter([ n[1]["type"] for n in clean_G.nodes(data=True) if n[1]["start"] == "" ])
print "-"*10
print "%s nodes after conversion of person from nodes to edges"%len(clean_G.nodes())
print "%s edges after conversion of person from nodes to edges"%len(clean_G.edges())
print "-"*10


## save graph to a CSV file
with open(os.path.join(results_folder,'ARC5_no_project_edges.csv'), 'wb') as metrics_file:
    wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
    wr.writerow(["source", "target", "type", "name", "additionalData", "start", "end"])
    for n in clean_G.edges(data=True):
        data = n[2]

        try :
            name = data["name"]
        except KeyError:
            name = data["type"]
        try :
            data["additionalData"]
        except KeyError:
            data["additionalData"] = []

        try:
            start = data["start"]
        except KeyError:
            start = None

        try :
            end = data["end"]
        except KeyError:
            end = None

        row = [n[0], n[1], data["type"], name, json.dumps(data["additionalData"]), start, end ]
        wr.writerow(row)

print "edges saved as ARC5_no_project_edges.csv"

with open(os.path.join(results_folder,'ARC5_no_project_nodes.csv'), 'wb') as metrics_file:
    wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
    wr.writerow(["id", "name", "type", "start", "end", "axe"])
    for n in clean_G.nodes(data=True):
        data = n[1]
        row = [n[0], data["name"], data["type"], data["start"], data["end"], data["axe.id"]]
        wr.writerow(row)
print "nodes saved as ARC5_no_project_nodes.csv"
