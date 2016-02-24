import csv
import scipy as sp
import networkx as nx

# create empty graph
G=nx.Graph()

# import edges
edges_file="../mongoexport/edges.csv"
with open(edges_file, "r") as f :
    reader = csv.DictReader(f)
    for edge in reader :
        G.add_edge(edge["source"], edge["target"])

print "%s nodes"%len(G.nodes())
print "%s edges"%len(G.edges())

#export to scipy sparse matrix
A = nx.adjacency_matrix(G)
print(A.todense())
