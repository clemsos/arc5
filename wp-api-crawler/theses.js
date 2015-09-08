var api = require("./api");
var file = require("./file");

var rawThesesFilename = './data/rawTheses.json';

// save to JSON
// api.getAllItems("bdd_these", function(theses){
//     // console.log(theses.length);
//     file.writeToJsonFile(theses,rawThesesFilename);
// })

file.readJsonFromFile(rawThesesFilename, function(theses) {
    // console.log(theses.length);
    var these_fields  = ["laboratoire" ,"etablissement" ,"ecole_doctorale" ,"partenaire" ,"directeur"  ,"coencadrant", "doctorant"];
    for (var i = 0; i < theses.length; i++) {
        var these = cleanItem(theses[i], "these", these_fields);
    }
});

api.getAllItems("bdd_projet", function(projects){
    var projects_fields  = ["nom_des_porteurs", "chercheur", "partenaires", "laboratoire" ,"etablissements_gestionnaires"];

    for (var i = 0; i < projects.length; i++) {
        var project = cleanItem(projects[i], "projet", projects_fields);
    }
});

function cleanItem(item, radical, fields) {

    var clean = replaceObjectsByID(item.meta, radical, fields);
    delete clean.public_fields; // some clean

    clean.ID = item.ID;
    clean.title = item.title;
    clean.slug = item.slug;
    clean.bdd_link = item.link;
    clean.axe = {}
    if(item.terms.bdd_thematique_arc5){
        clean.axe.ID = item.terms.bdd_thematique_arc5[0].ID;
        clean.axe.name = item.terms.bdd_thematique_arc5[0].name;
        clean.axe.slug = item.terms.bdd_thematique_arc5[0].slug;
    }

    console.log(clean);
    return clean
}

function replaceObjectsByID (item, radical, fields) {

    fields.forEach(function(field){
        var toParse = item[radical+"-"+field] || [];

        item[field] = toParse.map(function(d){ return d.ID })
        delete item[radical+"-"+field]
    })

    return item;
}
