const fs = require('fs');
const axios = require('axios');
const https = require('https');
const express = require('express');
const app = express();

const SEC_TO_MS = 1e3;
const NS_TO_MS = 1e-6;

const NUMBER_ITERATIONS = 1e3;

ipAddr = fs.readFileSync('/ip-info.txt')

axios({
	method: 'put',
	url: `http://${ipAddr}:8080/metric/boot`
})
.catch(error => {
	console.log(error)
})

function generate_random_numbers() {
	var randomNumbers = [];

	for(let i = 0; i < NUMBER_ITERATIONS; i++) {
		const randomNumber = Math.floor(Math.random() * 1500);
		randomNumbers.push(randomNumber.toString());
	}

	return randomNumbers;
}

function upload_data(put_host, put_path, data) {
	const options = {
		hostname: put_host,
		port: 443,
		oath: put_path,
		method: 'PUT'
	};

	const req = https.request(options, (res) => {
		res.on('error', (error) => {
			console.log(error);
		});
	});

	req.write(data);
	req.end();
}

function download_data(get_host, get_path, data) {
	const options = {
		hostname: get_host,
		port: 443,
		oath: get_path,
		method: 'GET'
	};

	const req = https.request(options, (res) => {
		res.on('data', (data) => {
			console.log(data);
		});
		
		res.on('error', (error) => {
			console.log(error);
		});
	});
}

function benchmark_network_task(put_host, put_path, get_host, get_path) {
	var randomNumbers = generate_random_numbers();
	upload_data(put_host, put_path, randomNumbers);
	download_data(get_host, get_path);
	
}

function benchmark_disk_task() {
	var randomNumbers = generate_random_numbers();
	fs.writeFileSync('randomNumbers.txt', randomNumbers.join());
	const str = fs.readFileSync('randomNumbers.txt');
	console.log(str.toString('utf-8'));
}

app.put('/metric/network/execution', (req, res) => {
	startTime = process.hrtime();
	benchmark_network_task();
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
