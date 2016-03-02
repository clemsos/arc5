var uuid = require('node-uuid');
// var client = require('mongodb').MongoClient;
var mongojs = require('mongojs')

// DB connection
var dbName = "arc5";
var url = 'mongodb://localhost:27017/' + dbName;

// connect to Mongo
var db = mongojs(url)

// collections
var nodes = db.collection('nodes')
var edges = db.collection('edges')

db.runCommand('serverStatus', function (err, resp) {
    if(err) throw err;
    console.log("DB correctly running");
    if (parseFloat(resp.version) < 2.6) throw "Require Mongo <2.6"
})

db.on('ready',function() {
    console.log('database ready');
    // reset data
    nodes.drop();
    edges.drop();
});

db.on('connect',function() {
    console.log('database connected');
    console.log("Existing data dropped");
});

db.on('error', function (err) {
    console.log('database error', err)
})

// Initialize the Ordered Batch to store all stuff properly
var nodesBatch = [];
var edgesBatch = edges.initializeOrderedBulkOp();

// errors
var errorsCount = 0;
var operationsCount = 0;

// write node
var insertOrUpdateNode = function(node) {
    addToNodesBatch(node);
}

// parse and write edge
var insertOrUpdateEdge = function(edge) {
    var source = edge.source;
    var target = edge.target;

    // if(!source.slug) console.log(source);
    // if(!target.slug) console.log(target);

    // write to db
    insertOrUpdateNode(source);
    insertOrUpdateNode(target);

    var edge = {
        "type" : edge.type,
        "source" : source.slug,
        "target" : target.slug,
        "start" : edge.start,
        "end" : edge.end
    };

    addToEdgesBatch(edge);

}

// DB : queue to Mongo bulk
addToEdgesBatch = function(edge) {

    edgesBatch
        .find({ "type" : edge.type, "source" : edge.source, "target" : edge.target}) // query
        .upsert()
        .updateOne({ '$set' :  {
                "type" : edge.type,
                "source" : edge.source,
                "target" : edge.target,
                "start": edge.start,
                "end" : edge.end
            }
        })
}

// DB : queue to Mongo bulk

// init
if(!nodesBatch.length) nodesBatch.push(nodes.initializeOrderedBulkOp());

addToNodesBatch = function(node, callback) {

    // get last one
    var bulk = nodesBatch[nodesBatch.length -1];

    if(bulk._currCmd) // has at least 1 command
        if(bulk._currCmd.updates.length > 999) {// but more  than 999
            nodesBatch.push(nodes.initializeOrderedBulkOp()); // add new batch
            bulk = nodesBatch[nodesBatch.length -1]; // switch to new batch
        }

    // catch last bulk
    bulk
        .find({ "slug" : node.slug, "type" : node.type}) // query
        .upsert()
        .updateOne({
            name: node.name ,
            type: node.type  ,
            slug: node.slug ,
            bddLink: node.bddLink || "",
            acronyme: node.acronyme  || "",
            start: node.start  || "",
            end : node.end   || "",
            axe : node.axe || ""
        })
}

// DB : execute the operations
var execCount = 0;
var nodesBatchExec = function(cb){

    if(execCount == nodesBatch.length) {
        cb() // stop when reach total
        return
    }

    // log
    console.log(nodesBatch[execCount]._currCmd.updates.length, " nodes "+(execCount+1)+"/"+nodesBatch.length+" operations");

    // exec
    nodesBatch[execCount].execute(function(err, results) {
        if(err) {
            console.log(err);
            throw err;
        }
        console.log(" nodes "+(execCount+1)+"/"+nodesBatch.length+" ok");
        execCount++;
        nodesBatchExec(cb);
    })
}

executeBatches = function () {

    // get started with DB
    console.log("Executing bulk write queries in Mongo");


    console.log(nodesBatch.length, "batch of nodes");
    console.log(edgesBatch._currCmd.updates.length, " edges operations");

     edgesBatch.execute(function(err, results) {
            if(err) {
                console.log(err);
                throw err;
            }
            console.log("Edges written ok");
            // recursive exec
            nodesBatchExec(function () {
                console.log("everything done !");
                db.close();
            })
        })

}




module.exports = {
    insertOrUpdateEdge : insertOrUpdateEdge,
    insertOrUpdateNode : insertOrUpdateNode,
    execute : executeBatches
}


    /*var getNode = function(node, db, callback) {
        findNode(node, db, function  (result) {
            if(result) callback(result)
            else insertOrUpdateNode(node, db, function (node) {
                console.log(node);
            })
        })
    }

    var findNode = function(node, db, callback) {
      // Get the documents collection
      db.collection('nodes').findOne({ "name" : node.name, "type" : node.type}, function(err, result) {
            if(err) throw err;
            callback(result);
        });
    }

    var createNode = function (node, db, callback) {
        db.collection('nodes').insert(node, function (err, doc) {
            if(err) throw err;
            callback(doc);
        })
    }*/
