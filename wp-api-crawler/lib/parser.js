var api = require("./api")
    , utils = require("./utils")
    , moment = require('moment')
    , logger = require('winston');

function parseRelationshipsFields (item, type, fields, callback) {

    var edges = [];
    // loop through all relationships fields
    fields.forEach(function(field){
        var toParse = item.meta[type+"-"+field] || [];

        // for each element
        toParse.forEach(function(target){
            if(target) {
                var edge = getEdge(item, target, field, item.start, item.end);
                edges.push(edge);
            }
        });
    })

    callback(edges);
}

function getEdge (source, target, type, start, end) {

    var edge = {
            'source' : parseNode(source),
            'target' : parseNode(target),
            'type' : type
        }

    if(start) edge.start = start //moment( start , "YYYYMMDD").toString();
    if(end)  edge.end = end //moment( end , "YYYYMMDD").toString();

    return edge
}

function getAxe(id) {

        var axe1 = {
                id : 1,
                name : 'Axe 1 - Cultures au pluriel',
                slug : 'axe-1-cultures-au-pluriel'
            };

        var axe2 = {
                id : 2,
                name: 'Axe 2 - Cultures numériques',
                slug: 'axe-2-cultures-numeriques'
            };

        var axe3 =  {
                id: 3,
                name: 'Axe 3 - Sciences et techniques',
                slug: 'axe-3-sciences-et-techniques'
            };

        switch (id) {
            case  9 :  return axe1;
            case 10 : return axe2;
            case  11: return axe3;
            case "1" : return axe1;
            case "2" : return axe2;
            case "3" : return axe3;
        }

        return {}
}

// get clean type
function getType(type) {
    if(type.slice(0, 3) == "bdd") return type.slice(4, type.length); // remove bdd_
    else return  type
}

function parseRelationships(item, callback) {

        var type = getType(item.type);

        var relationshipsFields =[];
        switch (type) {

            case "laboratoire":
                logger.log("debug", "-- labo");
                break;
            case "etablissement":
                logger.log("debug", "-- etablissement");
                relationshipsFields =  ["directeur", "laboratoire", "partenaire"];
                break;
            case "personne":
                logger.log("debug", "-- personne");
                break;
            case "ecole-doctorale" :
                logger.log("debug", '--ecole-doctorale');
                break;
            case "partenaire" :
                logger.log("debug", '--partenaire');
                relationshipsFields = ["projet", "porteur", "ville"]
                break;
            case "projet" :
                logger.log("debug", '--projet');
                relationshipsFields = ["nom_des_porteurs", "chercheur", "partenaires", "laboratoire" ,"etablissements_gestionnaires"];
                break;
            case "these" :
                logger.log("debug", '--these');
                relationshipsFields = ["doctorant", "laboratoire", "etablissement", "ecole-doctorale", "partenaire", "directeur", "coencadrant"]
                break;
        } // end switch

        parseRelationshipsFields(item, type, relationshipsFields, function(edges) {
            callback(edges);
        })
}

function parseNode(item) {

        var node = {};

        // get type
        var t = item.type || item.post_type;
        node.type = getType(t);

        node.bddLink = item.link || "";

        node.start =  item.start // moment(item.start, "YYYYMMDD").toJSON();
        node.end = item.end // moment(item.end, "YYYYMMDD").toJSON();

        // if(node.type == "partenaire") console.log(item);

        // parse date, axe
        if (node.type == "projet" || node.type == "these" || node.type == "postdoc") {

            // add meta
            node.name = item.title || node.type + "-" +Math.floor(Math.random()*100000);
            node.acronyme = item.meta.acronyme || node.name.match(/\b(\w)/g).join('').toUpperCase();
            node.site = item.meta.site;
            // axe
            if (item.terms && item.terms.bdd_thematique_arc5) node.axe =  getAxe(item.terms.bdd_thematique_arc5[0].ID);
            else node.axe =  getAxe(item.axe);

        } else if (node.type == "laboratoire") {

            // add meta
            node.name = item.post_title || item.title || "laboratoire"+Math.floor(Math.random()*100000);
            node.bddLink = item.guid || "";

        } else if (node.type == "personne"|| node.type == "partenaire" || node.type == "ecole-doctorale" || node.type == "etablissement") {

            // generate ID if no name is defined
            if (item.title) node.name = item.title;
            else if (item.name) node.name = item.name;
            else {
                node.name = (item.role != undefined || item.type != undefined) ?  node.type +"-"+Math.floor(Math.random()*100000) : item.post_title;
            }

        } else if (node.type == "ville" ){
            node.name = item.title || "ville"+"-"+Math.floor(Math.random()*100000);
        }

        node.slug = item.slug || utils.slugify(node.name);
        return node;
}

module.exports = {
    parseNode : parseNode,
    parseRelationships : parseRelationships
}
