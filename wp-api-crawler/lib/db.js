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
    // TODO : reset data
    // nodes.drop();
    // edges.drop();
    // console.log("Existing data dropped");
});

db.on('connect',function() {
    console.log('database connected');
});

db.on('error', function (err) {
    console.log('database error', err)
})

// Initialize the Ordered Batch to store all stuff properly
var nodesBatch = [];
var edgesBatch = [];

// errors
var errorsCount = 0;
var operationsCount = 0;


// write node
var nodesInBatch = []
var insertOrUpdateNode = function(node) {
  if( nodesInBatch.indexOf(node.slug) == -1  ) {
    addToNodesBatch(node);
    nodesInBatch.push(node.slug)
  }
}

// parse and write edge
var insertOrUpdateEdge = function(edge, isProjet) {
    var source = edge.source;
    var target = edge.target;

    // if (target.type == "projet" && target.start == "") console.log(source);

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

// init
if(!edgesBatch.length) edgesBatch.push(edges.initializeOrderedBulkOp());
addToEdgesBatch = function(edge) {

  // get last one
  var bulk = edgesBatch[edgesBatch.length -1];

  if(bulk._currCmd) // has at least 1 command
      if(bulk._currCmd.updates.length > 999) {// but more  than 999
          edgesBatch.push(edges.initializeOrderedBulkOp()); // add new batch
          bulk = edgesBatch[edgesBatch.length -1]; // switch to new batch
      }

    bulk
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

    if (node.start == "") node.start = null
    if (node.end == "") node.end = null

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
  console.log("executing DB ");
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

var edgesExecCount = 0;
var edgesBatchExec = function(cb){
  edgesBatchExecRecursive(cb);
}

var edgesBatchExecRecursive = function(cb){
  console.log("Edges : executing DB ");
    if(edgesExecCount == edgesBatch.length) {
        cb() // stop when reach total
        return
    }

    // log
    console.log(edgesBatch[edgesExecCount]._currCmd.updates.length, " edges "+(edgesExecCount+1)+"/"+edgesBatch.length+" operations");

    // exec
    edgesBatch[edgesExecCount].execute(function(err, results) {
        if(err) {
            console.log(err);
            throw err;
        }
        console.log(" nodes "+(edgesExecCount+1)+"/"+edgesBatch.length+" ok");
        edgesExecCount++;
        edgesBatchExecRecursive(cb);
    })
}

executeBatches = function () {

    // get started with DB
    console.log("Executing bulk write queries in Mongo");

    console.log(nodesBatch.length, "batch of nodes");
    console.log(edgesBatch.length, "batch of edges");

     edgesBatchExec(function(err, results) {
            if(err) {
                console.log(err);
                throw err;
            }
            console.log("Edges written ok");
            // recursive exec
            nodesBatchExec(function () {
                console.log("Nodes written ok");
                console.log("everything done !");

                // setTimeout(function(){
                    //do what you need here
                db.close();
                // }, 2000);
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
