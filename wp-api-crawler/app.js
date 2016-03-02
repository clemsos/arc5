var api = require("./lib/api")
    , parser = require("./lib/parser")
    , file = require("./lib/file")
    , utils = require("./lib/utils")
    , methods = require("./lib/db");

// LOG file
var logger = require('winston');
logger.add(logger.transports.File, { filename: 'arc5.log', prettyPrint : true });
// logger.level = 'debug';

// indexes to crawl
var nodesFiles = ["ecole-doctorales" , "etablissements" , "laboratoires" , "personnes" , "postdocs" , "projets" , "theses", "partenaires"];
var wpIndex = ["bdd_these", "bdd_projet"];

// keep track of progresses
var totalIndexes = nodesFiles.length + wpIndex.length;

// loop through all JSON files
for (var i = 0; i < nodesFiles.length; i++) {
    file.readJsonFromFile("data/json/"+nodesFiles[i]+".json", function(items) {
        console.log(items.length, " items in ",  items[0].type+"s");
        saveEdgesAndNodes(items)
    })
}

// loop through all JSON WP indexes
for (var i = 0; i < wpIndex.length; i++) {
    api.getAllItems(wpIndex[i], function(items){
        saveEdgesAndNodes(items);
    });
}



var loops = 0;
function saveEdgesAndNodes (items, edgesBatch, nodesBatch) {

    // count function calls to keep track of progresses
    loops++;

    for (var z = 0; z < items.length; z++) {
        var item = items[z];

        if(item) {

            // save node
            var node = parser.parseNode(item);
            methods.insertOrUpdateNode(node);

            // create edges and target nodes
            parser.parseRelationships(item, function (edges) {
                for (var j = 0; j < edges.length; j++) {
                    methods.insertOrUpdateEdge(edges[j]);
                }

                if(totalIndexes == loops &&  z+1 == items.length) {
                    console.log("indexing done");
                    methods.execute()
                }
            })
        }
    }
}

// getAllThesesFromCSV();

    // nodes.forEach(function  (item) {
    //     saveNode (item.node);
    //     for (var i = 0; i < item.edges.length; i++) {
    //         saveEdge (item.edges[i]);
    //         saveNode (item.edges[i].target);
    //     };
    // })
// });



function saveEdge (edge) {
    // console.log(edge);
}

function getAndParseNode(_id, callback){
    api.getSingleItem(_id, function (item) {
        if (! item.type) return;
        else parser.getNode(item, function (node) {
            callback(node);
        });
    });
}

function searchAndParseNode (q, type, callback) {

    api.searchItem(q, type, function (data) {
        if (data) {
           parser.getAndParseNode(data.ID, function  (node) {
               callback(node);
           })
        } else {
            callback(null)
        }
    })
}

function getAllThesesFromWP (callback) {
    api.getAllItems("bdd_these", function(items){
        var nodes = [];
        for (var i = 0; i < items.length; i++) {

            parser.getNode(items[i], function (node) {

                // if (nodes.length == projects.length) callback(nodes);
            });
            // console.log(i);

            // parser.getRelationships(items[i], function (edges) {
            // //     // for (var j = 0; j < edges.length; i++) {
            // //     //     var source = getNode(edges[i].source)
            // //     //     var target = getNode(edges[i].source)
            // //         // saveEdge(source._id, target._id, edge[i]type);
            // }

            // })
        }
    });
}

function getAllThesesFromCSV(callback) {
    file.readJsonFromFile("data/json/theses.json", function(items) {
        var nodes = [];
        for (var i = 0; i < items.length; i++) {
            // parser.getNode(items[i], function (node) {
            // if (nodes.length == projects.length) callback(nodes);
            // });

            // console.log(i);
            parser.getRelationships(items[i], function (edges) {
                // console.log(edges);
            })

        //     parser.getNode(items[i], function (node) {
        //         nodes.push(node)
        //         if (nodes.length == items.length) callback(nodes);
        //     });
        }
    });
}

// if it exists fetch the available info and parse it into the node

// write the node to DB
// check if it has relationships with other nodes
// save relationship as edge

// fetch partners
// add partner as a node
// add partner relationship as an edge

// fetch sub
// add sub provider as a node
// add sub relationships as an edge with amount



// getAllThesesFromWP(function(wpResults){

//     getAllThesesFromCSV(function  (csvResults){
//         console.log(wpResults.length, csvResults.length);

//         // fetch similar posts
//         var wpNames = wpResults.map(function(d){return d.node.name});
//         var csvNames = csvResults.map(function(d){return d.node.name});
//         var similars = utils.matchSimilarItemsInArray(wpNames, csvNames);

//         similars.forEach(function (similar) {
//             var nodeA = wpResults[similar[0]];
//             var nodeB = csvResults[similar[1]];
//             var node = mergeNodesAndEdges(nodeA, nodeB);
//             console.log(node);
//         })

//     });
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
