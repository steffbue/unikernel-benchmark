const express = require('express')
const AWS = require('aws-sdk');
const app = express();

const SEC_TO_MS = 1e3;
const NS_TO_MS = 1e-6;

var ec2 = new AWS.EC2();
const filter = {Name: 'tag:Benchmark', Values: ['Unikernel']};
const filterLinuxInstance = [filter, {Name: 'tag:Type', Values: ['Linux']}];


var instanceIdLinux;
ec2.describeInstances({Filters: filterLinuxInstance}, function(err, data){
    if (err) throw err;
    instanceIdLinux = data[0].Instances[0].InstanceId; 
});

var startTime;
var diffTime;

var serviceReady = true;
var resultReady = false;

app.put('/metric/boot/start', (req, res) => {
    if(!serviceReady) {
        res.writeHead(503);
        res.end();
    } else {
        ec2.startInstances({InstanceIds: [instanceIdLinux]}, function(err, data){
            if (err) {
                res.writeHead(500);
                res.end();
            }
            startTime = process.hrtime();
            res.writeHead(200);

            serviceReady = false;

            res.end();
        });
    }
    
});


app.get('/metric/boot/result', (req, res) => {
    if(!resultReady) {
        res.writeHead(404);
        res.end();
    } else {
        res.writeHead(200);
        res.json({BootTime: (diffTime[0] * SEC_TO_MS) + (diffTime[1] * NS_TO_MS)});

        serviceReady = true;
        resultReady = false;

        res.end();
    }
});

app.put('/metric/boot', (req, res) => {
    ec2.stopInstances({InstanceIds: [instanceIdLinux]}, function(err, data){
        if (err) throw err;
        ec2.waitFor('instanceStopped', {Filters: filterLinuxInstance}, function(err, data) {
            diffTime = process.hrtime(startTime);
            resultReady = true;
            res.end();
        });
    });  
});

app.listen(8080)