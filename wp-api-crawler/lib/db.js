

var insertOrUpdateEdge = function(edge, db, callback) {
    var source = edge.source;
    var target = edge.target;

    insertOrUpdateNode(source, db,function (nodeA) {
        insertOrUpdateNode(target, db,function (nodeB) {
            // console.log(nodeA.name, nodeB.name);
            db.collection('edges').findAndModify( 
                { "type" : edge.type, "source" : nodeA._id, "target" : nodeB._id},
                { "type" : 1}, // sort order
                { $set :
                     {  
                        "type" : edge.type, 
                        "source" : nodeA._id, 
                        "target" : nodeB._id,
                        start: edge.start,
                        end : edge.end
                    }
                },
                { upsert: true },
                 function(err, result) {
                    if(err) throw err;
                    // console.log(result);
                    callback(result);
                 })
            })
    })
}

var insertOrUpdateNode = function(node,db,callback) {
    db.collection('nodes').findAndModify(
        { "name" : node.name, "type" : node.type}, // query 
        { "name" : 1}, // sort order
        { $set : {
                name: node.name, 
                type: node.type, 
                slug: node.slug,
                bddLink: node.bddLink,
                acronyme: node.acronyme,
                start: node.start,
                end : node.end,
                axe : node.axe
            }
        },
        { upsert: true },
        function(err, result) {
            if(err)  throw err;
            // console.log(result.value);
            callback(result.value);
         }
    );
}

var getNode = function(node, db, callback) {
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
}

module.exports = {
    insertOrUpdateNode : insertOrUpdateNode,
    insertOrUpdateEdge : insertOrUpdateEdge

}
