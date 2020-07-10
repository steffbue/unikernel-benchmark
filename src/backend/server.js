const fs = require('fs');
const axios = require('axios');
const https = require('https');
const express = require('express');
const bodyParser = require('body-parser');
const url = require('url');
const app = express();

const SEC_TO_MS = 1e3;
const NS_TO_MS = 1e-6;

const NUMBER_ITERATIONS = 1e4;

ipAddr = fs.readFileSync('/ip-info.txt')

axios({
	method: 'put',
	url: `http://${ipAddr}:8080/metric/boot`
})
.catch(error => {
	console.log(error)
});

app.use(bodyParser.json());

function generate_random_numbers() {
	var randomNumbers = [];

	for(let i = 0; i < NUMBER_ITERATIONS; i++) {
		const randomNumber = Math.floor(Math.random() * 80000) + 10000;
		randomNumbers.push(randomNumber.toString());
	}

	return randomNumbers;
}

function upload_data(putHost, putPath, data) {
	const options = {
		hostname: putHost,
		port: 443,
		path: putPath,
		method: 'PUT',
		headers: {
			'Content-Type': 'text/plain',
			'Content-Length': Buffer.byteLength(data)
		}
	};

	const req = https.request(options, (res) => {
		res.on('data', (data) => {
			console.log(data.toString('utf-8'));
		});
		
		res.on('error', (error) => {
			console.log(error);
		});
	});

	req.write(data);
	req.end();
}

function download_data(getHost, getPath) {
	const options = {
		hostname: getHost,
		port: 443,
		path: getPath,
		method: 'GET',
		headers: {
			'Accept': 'text/plain'
		}
	};

	const req = https.request(options, (res) => {
		res.on('data', (data) => {
			console.log(data.toString('utf-8'));
		});
		
		res.on('error', (error) => {
			console.log(error);
		});
	});

	req.end();
}

function benchmark_network_task(putHost, putPath, getHost, getPath) {
	var randomNumbers = generate_random_numbers();
	upload_data(putHost, putPath, randomNumbers.join());
	download_data(getHost, getPath);
	
}

function benchmark_disk_task() {
	var randomNumbers = generate_random_numbers();
	fs.writeFileSync('randomNumbers.txt', randomNumbers.join());
	const str = fs.readFileSync('randomNumbers.txt');
	console.log(str.toString('utf-8'));
}

app.put('/metric/network/execution', (req, res) => {
	const getURL = req.body.getURL;
	const putURL = req.body.putURL;

	startTime = process.hrtime();
	benchmark_network_task(url.parse(putURL).hostname, url.parse(putURL).pathname + url.parse(putURL).search, url.parse(getURL).hostname, url.parse(getURL).pathname + url.parse(getURL).search);
	diffTime = process.hrtime(startTime)

	resJson = {
		ExecutionTime: (diffTime[0] * SEC_TO_MS) + (diffTime[1] * NS_TO_MS) 
	}

	res.json(resJson)
	res.end()
});

app.get('/metric/disk/execution', (req, res) => {
	startTime = process.hrtime();
	benchmark_disk_task();
	diffTime = process.hrtime(startTime)

	resJson = {
		ExecutionTime: (diffTime[0] * SEC_TO_MS) + (diffTime[1] * NS_TO_MS) 
	}

	res.json(resJson)
	res.end()
});

app.listen(8080);
