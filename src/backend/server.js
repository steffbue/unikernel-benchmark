const fs = require('fs')
const axios = require('axios')
const express = require('express');
const app = express();

const SEC_TO_MS = 1e3;
const NS_TO_MS = 1e-6;


ipAddr = fs.readFileSync('ip-info.txt')

axios({
	method: 'put',
	url: `http://${ipAddr}:80/metric/boot`,
	timeout: 500
})
.catch(error => {
	console.log(error)
})



app.get('/metric/execution', (req, res) => {
	startTime = process.hrtime()
	// Executing task
	diffTime = process.hrtime(startTime)

	resJson = {
		ExecutionTime: (diffTime[0] * SEC_TO_MS) + (diffTime[1] * NS_TO_MS) 
	}

	res.json(resJson)
	res.end()
});

app.listen(8080);
