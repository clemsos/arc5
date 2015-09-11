var api = require("./lib/api")
    , parser = require("./lib/parser")
    , file = require("./lib/file");


// parse the project list
file.readJsonFromFile("data/json/ecoles_doctorales.json", function(items) {
    var nodes = [];
    for (var i = 0; i < items.length; i++) {
        searchAndParseNode(items[i].Nom, "ecole-doctorale" , function(node){
            nodes.push(node);
            console.log(nodes.length);
        })
    }
});


function searchAndParseNode (q, type, callback) {
    api.searchItem(q, type, function (data) {
        
        if (data) {
           parser.getNode(data.ID, function  (node) {
               callback(node);
           })
        }
    })
}

// api.getAllItems("bdd_projet", function(projects){
//     for (var i = 0; i < projects.length; i++) {
//         parser.getNode(projects[i].ID, function  (node) {
//             console.log(node);
//         })
//     };
// });

// api.getAllItems("bdd_these", function(projects){

//     var projects_fields  = ["bdd_projet", "bdd_laboratoire", "bdd_etablissement", "bdd_ecole-doctorale", "bdd_partenaire", "bdd_these", "bdd_personne"]

//     for (var i = 0; i < projects.length; i++) {
//         var project = parser.getCleanItems(projects[i], "projet", projects_fields);
//     }
// });



// var rawThesesFilename = './data/rawTheses.json';

// save to JSON
// api.getAllItems("bdd_these", function(theses){
//     // console.log(theses.length);
//     file.writeToJsonFile(theses,rawThesesFilename);
// })

// read from JSON
// file.readJsonFromFile(rawThesesFilename, function(theses) {
//     // console.log(theses.length);
//     var these_fields  = ["laboratoire" ,"etablissement" ,"ecole_doctorale" ,"partenaire" ,"directeur"  ,"coencadrant", "doctorant"];
//     for (var i = 0; i < theses.length; i++) {
//         var these = cleanItem(theses[i], "these", these_fields);
//     }
// });
