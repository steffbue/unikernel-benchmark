const fs = require('fs')
const axios = require('axios')
const express = require('express');
const app = express();

const SEC_TO_MS = 1e3;
const NS_TO_MS = 1e-6;

const NUMBER_ITERATIONS = 100;

ipAddr = fs.readFileSync('/ip-info.txt')

axios({
	method: 'put',
	url: `http://${ipAddr}:8080/metric/boot`
})
.catch(error => {
	console.log(error)
})

function execution_benchmark_task() {
	for(let i = 0; i < NUMBER_ITERATIONS; i++) {
		var randomNumber = Math.floor(Math.random() * 1500);
		fs.writeFileSync(`randomNumber${i}.txt`, randomNumber);
	}

	for(let i = 0; i < NUMBER_ITERATIONS; i++) {
		var number = fs.readFileSync(`randomNumber${i}.txt`);
		console.log(number)
	}
}



app.get('/metric/execution', (req, res) => {
	startTime = process.hrtime();
	execution_benchmark_task();
	diffTime = process.hrtime(startTime)

	resJson = {
		ExecutionTime: (diffTime[0] * SEC_TO_MS) + (diffTime[1] * NS_TO_MS) 
	}

	res.json(resJson)
	res.end()
});

app.listen(8080);
