var client = require('mongodb').MongoClient;

var dbName = "arc5";

// Connection URL
var url = 'mongodb://localhost:27017/' + dbName;


function createEdge(targetId, sourceId, type,  start, end) {

        // Use connect method to connect to the Server
        client.connect(url, function(err, db) {
        console.log("Connected correctly to server");

        var edges = db.collection('edges');

        edge.update(
                    edge,
                    { upsert: true } 
         );

    })



}


var nodes = db.collection('nodes');
