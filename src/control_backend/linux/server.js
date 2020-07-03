const express = require('express');
const AWS = require('aws-sdk');
const app = express();

const SEC_TO_MS = 1e3;
const NS_TO_MS = 1e-6;

var ec2 = new AWS.EC2({region: 'eu-central-1'});
const filter = { Name: 'tag:Benchmark', Values: [ 'Unikernel' ] };
const filterLinuxInstance = { Name: 'tag:Type', Values: [ 'Linux' ] };
const filterLinuxInstanceState = [filter, filterLinuxInstance, { Name: 'instance-state-name', Values:['stopped', 'running', 'stopping'] }];

var startTime;
var diffTime;

var serviceReady = true;
var resultReady = false;

app.put('/metric/boot/start', (req, res) => {
	if (!serviceReady) {
		res.status(503).end();
	} else {
		ec2.describeInstances({ Filters: filterLinuxInstanceState }, function(err, data) {
			if (err) {
				res.status(500).end();
				return;
			}
			instanceIdLinux = data.Reservations[0].Instances[0].InstanceId;
			ec2.startInstances({ InstanceIds: [ instanceIdLinux ] }, function(err, data) {
				if (err) {
					res.status(500).end();
					return;
				}
				startTime = process.hrtime();
				serviceReady = false;
				res.status(200).end();
			});
		});
	}
});

app.get('/metric/boot/result', (req, res) => {
	if (!resultReady) {
		res.status(404).end();
	} else {
		serviceReady = true;
		resultReady = false;
		res.status(200).json({ BootTime: diffTime[0] * SEC_TO_MS + diffTime[1] * NS_TO_MS }).end();
	}
});

app.put('/metric/boot', (req, res) => {
	diffTime = process.hrtime(startTime);
	ec2.describeInstances({ Filters: filterLinuxInstanceState }, function(err, data) {
		if (err) {
			res.status(500).end();
			return;
		}
		ec2.stopInstances({ InstanceIds: [ instanceIdLinux ] }, function(err, data) {
			if (err) {
				res.status(500).end();
				return;
			}
			ec2.waitFor('instanceStopped', { Filters: filterLinuxInstanceState }, function(err, data) {
				resultReady = true;
            });
            res.status(200).end();
		});
	});
});

app.listen(8080);