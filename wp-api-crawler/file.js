var fs = require('fs');

// save to JSON file
function writeToJsonFile (data, filename) {
    fs.writeFile(filename, JSON.stringify(data, null, 4), function(err) {
        if(err) {
          console.log(err);
        } else {
          console.log("JSON saved to " + filename);
        }
    });
} 


// read 
function readJsonFromFile (filename, callback) {
    fs.readFile(filename, 'utf8', function (err, data) {
        if(err) throw err;
        else callback( JSON.parse(data) );
    });
}

module.exports = {
    writeToJsonFile : writeToJsonFile,
    readJsonFromFile : readJsonFromFile
}
