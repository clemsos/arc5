var request = require('request');
var URI = require('URIjs');

/*
* ARCS API

http://arcs.test/wp-json/posts?type=bdd_these

bdd_projet
bdd_laboratoire
bdd_etablissement
bdd_ecole-doctorale
bdd_partenaire
bdd_these
bdd_personne

*/

var arcsURL = "http://arcs.test/wp-json"
var ARC_NUMBER = "arc5";


// get posts
var getItems = function (type, callback) {
    if (typeof  (type) != "string") throw new Error("Word should be a string");
    
    // URL query
    var params = {};
    params.type = type;
    params["filter[posts_per_page]"] = 1000;

    var urlParsing = URI(arcsURL+"/posts");
    url = urlParsing.query(params).toString();
    console.log(url);

    request(url, function(err, response, body) {
        callback(err,body);
    });
};

function getSingleItem(id, callback){
    // if (typeof  (type) != "string") throw new Error("Word should be a string");
    
    // URL query
    var params = {};

    var urlParsing = URI(arcsURL+"/posts/"+id);
    url = urlParsing.query(params).toString();
    console.log(url);

    request(url, function(err, response, body) {
        callback(err,body);
    });
}

function getAllItems(type, callback) {

    getItems(type,  function (err, data) {
        var items = [];

        var bdd = JSON.parse(data);

        console.log(bdd.length, "results in ", type );

        bdd.forEach(function  (d) {
            if( d.meta.bdd_arc.indexOf(ARC_NUMBER) > -1) items.push(d);
        })

        console.log( items.length, Math.round(items.length / bdd.length * 100) + "%" );
        callback(items);
    })
}


module.exports = {
    getAllItems : getAllItems,
    getSingleItem : getSingleItem
}
