#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import json
import csv
import unicodecsv
from rhizi_client import RhiziAPIClient, set_debugging

node_file = "../mongoexport/nodes.csv"
edge_file = "../mongoexport/edges.csv"

def load_csv_data(filename):
    """Load CSV data from filename"""

    print("loading {}".format(filename))
    with open(filename, "r") as f:
        data = [x for x in unicodecsv.DictReader(f)]
    return data

def init_rhizi_instance(config):
    # parse intance URL
    assert not config['host'].startswith('http://')
    port = ':{}'.format(config["port"]) if config['port'] is not None else ''
    rhizi_instance_url = "http://{}{}".format(config["host"], port)

    print("Connecting to : {}".format(rhizi_instance_url))

    # init client
    rhizi_instance = RhiziAPIClient(rhizi_instance_url,
                                    config["rz_user_email"],
                                    config["rz_user_password"],
                                    debug=False) # set debug
    return rhizi_instance


if __name__ == '__main__':

    print "Import ARC5 data into Rhizi"

    # parse config
    with open("config.json", "r") as f:
        config = json.load(f)
    print("Config options : {}".format(config))

    # init API
    rhizi_instance = init_rhizi_instance(config)
    rz_doc_name = config["rz_doc_name"]

    # load data
    node_data = load_csv_data(node_file)
    edge_data = load_csv_data(edge_file)

    nodes = []
    node_types = {
        "personne": "Person",
    	"projet" :  "Project",
    	"ville" :  "City",
        "ecole-doctorale" : "Ecole Doctorale",
    	"etablissement" :  "Etablissement",
    	"laboratoire" :  "Laboratoire",
    	"these" :  "Thèse",
    	"postdoc" :  "Postdoc",
    	"partenaire" :  "Partenaire"
        }

    for n in node_data :
        node_type = node_types[str(n["type"])]
        print node_type
        # print n["id"], n["label"], node_type
        nodes.append({ "name" : n["label"], "id" : str(n["id"]) , "label":[ node_type ] })

    edges = []
    for n in edge_data :
        # print type(n["source"]), type(n["target"]), type(n["type"])
        # print n["source"], n["target"], n["type"]
        edge_type = str(n["type"])
        edges.append({ "__src_id": str(n["source"]), "id" : str(n["_id"]), "__dst_id" : str(n["target"]), "__type" : [edge_type] })


    # print nodes
    # parse data

    # init doc (reset scratch)
    # print("init doc")
    rhizi_instance.rz_doc_delete(rz_doc_name)
    rhizi_instance.rz_doc_create(rz_doc_name)

    # send data
    rhizi_instance.node_create(rz_doc_name, nodes)
    rhizi_instance.edge_create(rz_doc_name, edges)
