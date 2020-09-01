var Couchbase = require("couchbase");
var Express = require("express");
var BodyParser = require("body-parser");
var UUID = require("uuid");

var app = Express();
var N1qlQuery = Couchbase.N1qlQuery;

var myCluster = new Couchbase.Cluster('couchbase://' + process.env.COUCHBASE_HOST);
myCluster.authenticate(process.env.COUCHBASE_ADMIN_USER, process.env.COUCHBASE_ADMIN_PASSWORD);
var bucket = myCluster.openBucket(process.env.COUCHBASE_BUCKET);

app.use(BodyParser.json());

app.get("/", function(request, response) {
    response.send("The API provides a list of breweries for a given city, e.g. http://localhost:" + process.env.APPLICATION_PORT + "/example-1/breweries?city=Los%20Angeles");
});

app.get("/example-1/breweries", function(request, response) {
    var city = request.query.city;
    var query = N1qlQuery.fromString("SELECT * FROM `" + bucket._name + "` WHERE city = '" + city + "'");
    bucket.query(query, function(error, result) {
	    if(error) {
		return response.status(500).send(error);
	    }
	    response.send(result);
    });
});

app.get("/example-2/breweries", function(request, response) {
    var country = request.query.country;
    var query = N1qlQuery.fromString('SELECT * FROM `' + bucket._name + '` WHERE country = "' + country + '"');
    bucket.query(query, function(error, result) {
	    if(error) {
		return response.status(500).send(error);
	    }
	    response.send(result);
    });
});

var server = app.listen(process.env.APPLICATION_PORT || 3000, function() {
    console.log("Listening on port " + server.address().port + "...");
});
