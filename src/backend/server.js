var express = require('express');

console.log('Hello World');

var app = express();

app.get('/', (req, res) => {
	console.log('Hello World');
	res.end('Hello World');
});

app.listen(8080);
