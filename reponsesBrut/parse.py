#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter
import uuid
import csv
import os
import codecs
from jinja2 import Environment, FileSystemLoader
import json

PATH = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)

def clamp(val, minimum=0, maximum=255):
    if val < minimum:
        return minimum
    if val > maximum:
        return maximum
    return val

def colorscale(hexstr, scalefactor):
    """
    Scales a hex string by ``scalefactor``. Returns scaled hex string.

    To darken the color, use a float value between 0 and 1.
    To brighten the color, use a float value greater than 1.

    >>> colorscale("#DF3C3C", .5)
    #6F1E1E
    >>> colorscale("#52D24F", 1.6)
    #83FF7E
    >>> colorscale("#4F75D2", 1)
    #4F75D2
    """

    hexstr = hexstr.strip('#')

    if scalefactor < 0 or len(hexstr) != 6:
        return hexstr

    r, g, b = int(hexstr[:2], 16), int(hexstr[2:4], 16), int(hexstr[4:], 16)

    r = clamp(r * scalefactor)
    g = clamp(g * scalefactor)
    b = clamp(b * scalefactor)

    return "#%02x%02x%02x" % (r, g, b)

def do_json(value):
    """A filter that outputs Python objects as JSON"""
    return json.dumps(value)

TEMPLATE_ENVIRONMENT.filters['tojson'] = do_json

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def create_html_file(context, fname):
    #
    with codecs.open(fname, 'w', "utf-8") as f:
        html = render_template("ARC5-report-layout.html", context)
        f.write(html)
    print "file save as %s"%fname

def get_dataset_from_CSV(survey_type):
    data = []
    csv_name = "results-%s.csv"%survey_type
    csv_path = os.path.join(PATH, csv_name)
    if not os.path.isfile : raise ValueError("wrong path")
    with open(csv_path,"r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            data.append(dict(row))
    print "%s results exported from %s"%(len(data), csv_name)
    return data

def save_to_CSV(data, keys, final_path):
    with open(final_path, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def build_clean_dataset(data, common_keys, survey_type):
    clean_dataset = []
    for row in data :
        newRow = {}
        newRow["type"] = survey_type
        for key in common_keys:
            newRow[key] = row[key]
        clean_dataset.append(newRow)
    print "%s clean results"%len(clean_dataset)
    return clean_dataset

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))

def create_index_html(clean_dataset, title, questions, fname):

    print "%s : len of clean dataset "%len(clean_dataset)

    get_headers = questions

    # remove empty records
    final_dataset = []

    for entry in clean_dataset:
        try :
            if entry["Date[SQ001]"] != "":
                entry["Date[SQ001]"] = int(float(entry["Date[SQ001]"]))
            if entry["Date[SQ002]"] != "":
                entry["Date[SQ002]"] = int(float(entry["Date[SQ002]"]))
        except KeyError:
            # print "no time info"
            pass

        # check number of empty answers
        empty_answers = 0
        for key in entry:
            if entry[key] == "N/A" or entry[key] == "":
                empty_answers = empty_answers +1
        # avoid ttly empty answers
        if not empty_answers >= len(entry.keys())-5:
            final_dataset.append(entry)

    print "%s : len of final dataset "%len(final_dataset)


    # write final results to file
    keys = final_dataset[0].keys()
    final_path = os.path.join(PATH,'ARC5-survey-final-results.csv')
    save_to_CSV(final_dataset, keys, final_path)

    # save header doc
    final_path = os.path.join(PATH,'ARC5-survey-description.csv')
    save_to_CSV(headers_common, ["name", "description"], final_path)

    # Decode the UTF-8 string to get unicode
    ha =  [ { "name" : row["name"].decode('utf-8') , "description" : row["description"].decode('utf-8') } for row in headers_common]


    # organize by answer
    answers = []
    subquestions = []

    #load mapping
    with open(os.path.join(PATH,"chartMapping.json")) as data_file:
        chart_mapping = json.load(data_file)

    def get_results(key):
        _results = []
        for row in final_dataset:
            res = row[key]
            if not res == "N/A":
                _results.append(str(res).decode("utf-8"))
        return _results

    # map els
    for el in chart_mapping["questions"]:
        key = el["name"]
        chartType = el["chartType"]

        # print chartType
        if len(chartType.split("title")) > 1 :
            isTitle = True
        else :
            isTitle = False
        # print isTitle

        # check if subquestions
        hasSubQuestion = False
        try :
            el["subquestions"]
            hasSubQuestion = True
        except KeyError:
            hasSubQuestion = False

        # check if has ordering
        try :
            order = el["order"]
        except KeyError:
            order = []

        def sort_by_order(d):
            try:
                return order.index(d)
            except ValueError:
                return

        # parse the question
        question = {}
        question["name"] = key
        if hasSubQuestion or isTitle:
            question["description"] = key
        else :
            question["description"] = get_headers[key]

        # get chart type
        question["chartType"] = chartType
        # print question

        # get the results
        results = []
        chartData = []

        if not hasSubQuestion and not isTitle:
            results = get_results(key)
            if question["chartType"] != "list":
                count = dict(Counter(results))
                chartData = [{
                    "name" : k,
                    "label" : k,
                    "value" : count[k],
                    "color" : colorscale("#DF3C3C", .5*i+1)
                    }
                    for i, k in enumerate(count) if count[k] != "" and k != "" and k != " "]
        elif not isTitle:
            # add a case for Partenaires (merge all into a single list)
            if key == "Partenaires":
                for subkey in el["subquestions"]:
                    res = get_results(subkey)
                    results+=res
                # print results
            else :
                for i, subkey in enumerate(el["subquestions"]):
                    results = get_results(subkey)
                    count = dict(Counter(results))
                    label = get_headers[subkey]
                    if label.startswith("Comment avez".decode("utf-8")):
                        label = get_headers[subkey].split( "Comment avez-vous été amené(e) à travailler avec ces partenaires ? ".decode("utf-8") )[1]
                    elif label.startswith("Comment a ".decode("utf-8")):
                        label = get_headers[subkey].split("Comment a été financé ce projet ? ".decode("utf-8"))[1]
                    if subkey != "":
                        try:
                            c = count["Oui"]
                        except KeyError:
                            c = 0
                        point = {
                            "name" : subkey,
                            "label" : label,
                            "value" : c,
                            "color" : colorscale("#DF3C3C", .2*i)
                        }
                        chartData.append(point)

        # sort

        if len(order):
            chartData = sorted(chartData, key=lambda k: sort_by_order(k["name"]))
        print "---%s"%key
        for d in chartData : print d["name"]

        question["chartData"] = chartData
        question["results"] = results
        answers.append(question)

    # parse HTML reponsesBrut
    context = {
        "answers" : answers,
        "title" : title,
        "total_rep" : unicode(len(final_dataset))
    }

    create_html_file(context, fname)

def parse_headers(raw_headers):
    headers = {}
    for key in raw_headers.keys():
        row_id = key.split(".")[0]
        row_description = key.split(row_id)[1][2:]
        headers[row_id] = row_description
    return headers

if __name__ == "__main__":

    print "#"*10
    print "Parse Clean Datasets"
    # get raw data as list of dict
    culture_answers = get_dataset_from_CSV("Culture")
    recherche_answers = get_dataset_from_CSV("Recherche")

    # CSV keys
    culture_keys = culture_answers[0].keys()
    recherche_keys =recherche_answers[0].keys()
    print "%s culture_keys"%len(culture_keys)
    print "%s recherche_keys"%len(recherche_keys)

    # u = union(culture_keys, recherche_keys)
    # print len(u)
    common_keys = intersect(culture_keys, recherche_keys)
    print "%s common_keys"%len(common_keys)

    # headers
    raw_headers = get_dataset_from_CSV("headers")
    headers = parse_headers(raw_headers[0])

    headers_common = [{"name" :key, "description" : headers[key] } for key in headers if key in common_keys]
    assert len(headers_common) == len(common_keys)

    # clean
    clean_culture = build_clean_dataset(culture_answers, common_keys, "culture")
    clean_recherche = build_clean_dataset(recherche_answers, common_keys,"recherche")

    # build a master set
    clean_merged_dataset = clean_recherche + clean_culture

    questions = { row.decode('utf-8') : headers[row].decode('utf-8')  for row in headers  }

    print PATH
    RESULTS_PATH = os.path.join(PATH, "../results/questionnaires")
    if not os.path.isdir(RESULTS_PATH) : os.mkdir(RESULTS_PATH)

    print "#"*10
    print "Recherche"
    questions_culture_headers = get_dataset_from_CSV("culture-headers")
    # print questions_culture_headers[0]
    questions_culture = parse_headers(questions_culture_headers[0])

    # print questions_culture
    create_index_html(clean_culture, "Questionnaire Culture", { row.decode('utf-8') : questions_culture[row].decode('utf-8')  for row in questions_culture  },
    os.path.join(RESULTS_PATH, "ARC5_resultats_culture.html"))

    print "#"*10
    print "Culture"
    create_index_html(clean_recherche, "Questionnaire Recherche", questions, os.path.join(RESULTS_PATH, "ARC5_resultats_recherche.html"))

    # print "#"*10
    # print "Recherche + Culture"
    # questions_merged = { row["name"] : row["description"].decode('utf-8')  for row in headers_common  }
    # questions_merged["type"] = "Type de questionnaire (Recherche ou Culture)"
    # create_index_html(clean_merged_dataset, "Résulats Recherche+Culture", questions_merged, "ARC5_resultats_total.html")
