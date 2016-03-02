#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import scipy as sp
import networkx as nx
from difflib import get_close_matches
from collections import Counter
import itertools
import argparse
import pickle
import os

print

# create empty (undirected) graph
G=nx.Graph()

# import edges
edges_file="../mongoexport/edges.csv"
with open(edges_file, "r") as f :
    reader = csv.DictReader(f)
    for edge in reader :
        # print edge
        G.add_edge(edge["source"], edge["target"], {'type' : edge['type']})

print "#"*10
print "ORIGINAL NETWORK"
print "-"*10
print "%s nodes"%len(G.nodes())
print "%s edges"%len(G.edges())

# import nodes
nodes_file="../mongoexport/nodes.csv"
with open(nodes_file, "r") as f :
    reader = csv.DictReader(f)
    for node in reader :
        G.add_node(node["slug"], node)

print "%s nodes after data was added"%len(G.nodes())



### check for similar nodes

types = Counter([ g[1]["type"] for g in G.nodes(data=True) ]).keys()
print types
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
if len(similars) == 0:
    for node in G.nodes() :
        is_anon = False
        nodes = [ n for n in G.nodes() ]
        nodes.remove(node) # don't check for similarity with itself !
        for t in types :
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

# nodes_to_delete = []

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

deleted_nodes = []
clean_names = {}

# define clean names
for m in match_series:
    # arbitrary select first item as the good node
    clean_names[m] = m
    similar_nodes = list(set(match_series[m]))
    for node in similar_nodes:
        clean_names[node] = m

    # store nodes that have been deleted
    deleted_nodes += similar_nodes

print "%s deleted nodes"%len(deleted_nodes)

# get only clean nodes
for m in matched:
    real_name = clean_names[m]

    # get a complete list of nodes
    real_node = G.node[real_name]
    clean_G.add_node(real_name, real_node) # add clean nodes to the graph

    # get clean edges
    matched_edges = [e for e in G.edges(match_series[real_name], data=True)]
    for e in matched_edges:
        try:
            clean_G.add_edge(real_name, clean_names[e[1]], e[2] ) # rename edges properly and add to the graph
        except KeyError:
            clean_G.add_edge(real_name, e[1], e[2] ) # rename edges properly and add to the graph

# get all nodes except those already cleaned
clean_nodes = [n for n in G.nodes() if n not in matched and n != ""]

# make sure we have all nodes
assert len(clean_nodes) + len(matched) +1 == len(G.nodes())

# print len(clean_nodes)
for n in clean_nodes:
    clean_G.add_node(n, G.node[n])


# get all edges from clean nodes
clean_edges = [e for e in G.edges(clean_nodes) if e[0] not in deleted_nodes and e[1] not in deleted_nodes ]
for e in clean_edges:
    clean_G.add_edge( e[0], e[1], G.edge[e[0]][e[1]] )

# make sure that no deleted node is present in the final graph
assert len(set.intersection(set(clean_G.nodes()), set(deleted_nodes))) == 0

print "-"*10
print "%s nodes merged"%(len(G.nodes())-len(clean_G.nodes()))
print "%s edges merged"%(len(G.edges())-len(clean_G.edges()))
print "%s nodes after fix duplicate"%len(clean_G.nodes())
print "%s edges after fix duplicate"%len(clean_G.edges())


#### convert persons to edges
print
print "#"*20
print "CONVERT PERSONS TO EDGES"

persons = [node[0] for node in clean_G.nodes(data=True) if node[1]["type"] == "personne"]
persons_edges = clean_G.edges(persons)
print "%s persons linked to %s edges"%(len(persons), len(persons_edges))

for person in persons:

    # edges for a single person
    person_edges = clean_G.edges(person)
    # print "%s : %s edges "%(person, len(person_edges))

    # get all nodes linked by a single person
    list_of_person_nodes = []; map(list_of_person_nodes.extend, map(list,person_edges))
    assert len(list_of_person_nodes) == len(person_edges)*2 # make sure we have all nodes

    clean_nodes = [n for n in list_of_person_nodes if n != person]
    assert len(clean_nodes) == len(person_edges) # make sure we have all new nodes, except the person

    if len(person_edges) > 2 : # if have less than degree of 1 then remove node

        # get data to add to the edge
        data = clean_G.node[person]

        # delete person info
        data.pop("slug")
        data.pop("name")

        # create new edges between all those
        new_edges = list(itertools.combinations(clean_nodes, 2))
        for e in new_edges:
            clean_G.add_edge( e[0], e[1], data )

    # remove person from the graph
    clean_G.remove_node(person)

assert len(set.intersection(set(persons), set(clean_G.nodes() ))) == 0
assert "personne" not in [ n[1]["type"] for n in clean_G.nodes(data=True)]
print "-"*10
print "%s nodes after conversion of person from nodes to edges"%len(clean_G.nodes())
print "%s edges after conversion of person from nodes to edges"%len(clean_G.edges())



print
print "#"*10
print "SAVE CLEAN VERSIONS"
print

# change edges types
print Counter([n[2]["type"] for n in clean_G.edges(data=True)]).keys()

clean_edge_types = {
    'ville' : "travaille dans la ville de",
    'ecole-doctorale' : "héberge le doctorant",
    'etablissement' : "pilote le projet",
    'personne' : "ont des membres communs avec",
    'etablissements_gestionnaires' : "gère le projet",
    'projet' : "est partenaire de",
    'partenaire' : "est partenaire de",
    'laboratoire' : "héberge"
}

## save graph to a CSV file
with open('ARC5_final_edges.csv', 'wb') as metrics_file:
    wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
    wr.writerow(["source", "target", "type"])
    for n in clean_G.edges(data=True):
        data = n[2]
        row = [n[0], n[1], clean_edge_types[data["type"] ] ]
        wr.writerow(row)

print "edges saved as ARC5_final_edges.csv"

with open('ARC5_final_nodes.csv', 'wb') as metrics_file:
    wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
    wr.writerow(["id", "name", "type", "start", "end", "axe"])
    for n in clean_G.nodes(data=True):
        data = n[1]
        row = [n[0], data["name"], data["type"], data["start"], data["end"], data["axe.id"]]
        wr.writerow(row)
print "nodes saved as ARC5_final_nodes.csv"


print
print "#"*10
print "CENTRALITY METRICS"
## calculate centrality metrics:
degree = nx.degree_centrality(clean_G)
print "-- degree"
between = nx.betweenness_centrality(clean_G)
print "-- betweenness_centrality"
close = nx.closeness_centrality(clean_G)
print "-- closeness_centrality"

## save the multiple centrality metrics to a CSV file
with open('network_metrics.csv', 'wb') as metrics_file:
    wr = csv.writer(metrics_file, quoting=csv.QUOTE_ALL)
    wr.writerow(["name", "degree", "betweenness_centrality", "closeness_centrality"])
    for n in clean_G:
        wr.writerow([n, degree[n], between[n], close[n]])

print "Values saved to network_metrics.csv"

print
print "#"*10
print "HUMAN READABLE VERSION"

with open('ARC5_human_readable.txt', 'wb') as metrics_file:
    for n in clean_G.edges(data=True):
        line =  "%s %s %s \n\n"%(clean_G.node[n[1]]["name"], clean_edge_types[data["type"]], clean_G.node[n[0]]["name"])
        metrics_file.write(line)
