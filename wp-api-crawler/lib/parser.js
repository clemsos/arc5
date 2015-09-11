var api = require("./api");
var moment = require('moment')


function parseRelationships (item, type, fields) {

    // loop through all relationships fields 
    fields.forEach(function(field){
        var toParse = item.meta[type+"-"+field] || [];

        // for each element
        toParse.forEach(function(target){ 

            getEdge(item.ID, target.ID, field, item.start, item.end);

            // nodesId.push(target.ID);
            getNode(target.ID);

        });
    })

}

function getEdge (sourceId, targetId, type, start, end) {

    return {
            'source' : sourceId, 
            'target' : targetId, 
            'type' : type,
            'start' : moment( start , "YYYYMMDD").toString() ,
            'end' : moment( end , "YYYYMMDD").toString()
        };
}

function getNode(_id, callback) {

    api.getSingleItem(_id, function (item) {

        if (! item.type) return;

        var node = {};
        node.id = _id;
        node.type = item.type.slice(4, item.type.length); // remove bdd_
        node.title = item.title;
        node.slug = item.slug;
        node.bddLink = item.link;
        node.start = null, 
        node.end = null;
        node.acronyme = item.meta.acronyme;
        node.site = item.meta.site;

        var relationshipsFields =[];

        switch (node.type) {

            case "laboratoire":
                console.log("-- labo");
                break;
            case "etablissement":
                console.log("-- etablissement");
                relationshipsFields =  ["directeur", "laboratoire", "partenaire"];
                break;
            case "personne":
                console.log("-- personne");
                break;
            case "ecole-doctorale" : 
                console.log('--ecole-doctorale');
                break;
            case "partenaire" : 
                console.log('--partenaire');
                break;
            case "projet" :
                console.log('--projet');

                relationshipsFields = ["nom_des_porteurs", "chercheur", "partenaires", "laboratoire" ,"etablissements_gestionnaires"];
                node.start =  item.meta["date_debut"];
                node.end = item.meta["date_fin"];

                // topics
                node.axe = {};
                if(item.terms.bdd_thematique_arc5){
                    node.axe.ID = item.terms.bdd_thematique_arc5[0].ID;
                    node.axe.name = item.terms.bdd_thematique_arc5[0].name;
                    node.axe.slug = item.terms.bdd_thematique_arc5[0].slug;
                }

                break;
            case "these" : 
                console.log('--these');
                
                relationshipsFields = ["bdd_projet", "bdd_laboratoire", "bdd_etablissement", "bdd_ecole-doctorale", "bdd_partenaire", "bdd_these", "bdd_personne"]
                // date
                node.start =  item.meta["date_debut"];
                node.end = item.meta["date_soutenance"];
                
                // topics
                node.axe = {};
                if(item.terms.bdd_thematique_arc5){
                    node.axe.ID = item.terms.bdd_thematique_arc5[0].ID;
                    node.axe.name = item.terms.bdd_thematique_arc5[0].name;
                    node.axe.slug = item.terms.bdd_thematique_arc5[0].slug;
                }
                break;
        } // end switch

        // store the node
        console.log(node);

        // get all relationship
        parseRelationships(item, node.type, relationshipsFields);

    })
}

module.exports = {
    getNode : getNode
}


// function getCleanItem(item, radical, fields) {

//     var clean = {};

//     clean.ID = item.ID;
//     clean.title = item.title;
//     clean.slug = item.slug;
//     clean.bddLink = item.link;
//     clean.type = radical;
//     clean.subType = item.meta.type

//     // parse date
//     var start =  item.meta["date_debut"];
//     var end = "";

//     if(radical == "these") {
//         end = item.meta["date_soutenance"];
//     } else if (radical == "projet") {
//         end = item.meta["date_fin"];
//     } 

//     clean.start = start;
//     clean.end = end;

//     // parse relationships
//     clean.relationships = parseRelationships(item, radical, fields, start, end);

//     // thematics



//     return clean
// }
