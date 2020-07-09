const fs = require('fs')
const axios = require('axios')
const express = require('express');
const NodeRSA = require('node-rsa');
const app = express();

const SEC_TO_MS = 1e3;
const NS_TO_MS = 1e-6;

const NUMBER_ITERATIONS = 1e2;

ipAddr = fs.readFileSync('/ip-info.txt')

axios({
	method: 'put',
	url: `http://${ipAddr}:8080/metric/boot`
})
.catch(error => {
	console.log(error)
})

function benchmark_task() {
	const keys = new NodeRSA({b: 2048});

	for(let i = 0; i < NUMBER_ITERATIONS; i++) {
		const randomNumber = Math.floor(Math.random() * 1500);
		const encrypted = keys.encrypt(randomNumber, 'base64');
		const decrypted = keys.decrypt(encrypted, 'utf-8');
		console.log(randomNumber);
		console.log(encrypted);
		console.log(decrypted);
	}
}



app.get('/metric/execution', (req, res) => {
	startTime = process.hrtime();
	benchmark_task();
	diffTime = process.hrtime(startTime)

	resJson = {
		ExecutionTime: (diffTime[0] * SEC_TO_MS) + (diffTime[1] * NS_TO_MS) 
	}

	res.json(resJson)
	res.end()
});

app.listen(8080);
