var request = require('request');
var URI = require('URIjs');

/*
* ARCS API

http://arcs.test/wp-json/posts?type=bdd_these

bdd_projet
bdd_these

bdd_laboratoire
bdd_personne
bdd_partenaire

bdd_etablissement
bdd_ecole-doctorale

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
        if(err) throw err
        callback(JSON.parse(body));
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

function searchItem (q, type, callback) {
    if (typeof  (type) != "string") throw new Error("Word should be a string");
    if (typeof  (q) != "string") throw new Error("Word should be a string");
    
    // URL query
    var params = {};
    params.type = "bdd_"+type;
    params["filter[s]"] = q;

    var urlParsing = URI(arcsURL+"/posts");
    url = urlParsing.query(params).toString();
    // console.log(url);

    request(url, function(err, response, body) {
        if(err) throw err
        var bdd = JSON.parse(body);
        // console.log(bdd.length, "results for", q, " in ", type );

        var items = [];
        if(type == "projet" || type=="these") {
            bdd.forEach(function  (d) {
                if( d.meta.bdd_arc.indexOf(ARC_NUMBER) > -1) items.push(d);
            })
        } else {
            items = bdd;
        }

        callback(items[0]); // return only the 1st result

    });

}

module.exports = {
    getAllItems : getAllItems,
    getSingleItem : getSingleItem,
    searchItem : searchItem
}
