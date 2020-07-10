const express = require('express');
const AWS = require('aws-sdk');
const app = express();

const SEC_TO_MS = 1e3;
const NS_TO_MS = 1e-6;

var ec2 = new AWS.EC2({region: 'eu-central-1'});
const filter = { Name: 'tag:Benchmark', Values: [ 'Unikernel' ] };
const filterOSVInstance = { Name: 'tag:Type', Values: [ 'OSV' ] };
const filterOSVInstanceState = [filter, filterOSVInstance, { Name: 'instance-state-name', Values:['stopped', 'running', 'stopping'] }];

var startTimeBoot;
var diffTimeBoot;

var startTimeStop;
var diffTimeStop;

var serviceReady = true;
var resultReady = false;

app.put('/metric/boot/start', (req, res) => {
	if (!serviceReady) {
		res.status(503).end();
	} else {
		ec2.describeInstances({ Filters: filterOSVInstanceState }, function(err, data) {
			if (err) {
				res.status(500).end();
				return;
			}
			instanceIdOSV = data.Reservations[0].Instances[0].InstanceId;
			ec2.startInstances({ InstanceIds: [ instanceIdOSV ] }, function(err, data) {
				if (err) {
					res.status(500).end();
					return;
				}
				startTimeBoot = process.hrtime();
                serviceReady = false;
                resultReady = false;
				res.status(200).end();
			});
		});
	}
});

app.get('/metric/boot/result', (req, res) => {
	if (!resultReady) {
		res.status(503).end();
	} else {
		res.status(200).json({ BootTime: (diffTimeBoot[0] * SEC_TO_MS) + (diffTimeBoot[1] * NS_TO_MS), StopTime:  (diffTimeStop[0] * SEC_TO_MS) + (diffTimeStop[1] * NS_TO_MS)}).end();
	}
});

app.put('/metric/boot', (req, res) => {
	diffTimeBoot = process.hrtime(startTimeBoot);
	ec2.describeInstances({ Filters: filterOSVInstanceState }, function(err, data) {
		if (err) {
			res.status(500).end();
			return;
		}
		ec2.stopInstances({ InstanceIds: [ instanceIdOSV ] }, function(err, data) {
			startTimeStop = process.hrtime();
			if (err) {
				res.status(500).end();
				return;
			}
			resultReady = true;
			ec2.waitFor('instanceStopped', { Filters: filterOSVInstanceState }, function(err, data) {
				diffTimeStop = process.hrtime(startTimeStop);
				serviceReady = true;
				resultReady = true;
            });
            res.status(200).end();
		});
	});
});

app.listen(8080);