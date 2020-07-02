const express = require('express')
const AWS = require('aws-sdk');
const app = express();

var ec2 = new AWS.EC2();
const filter = {Name: 'tag:Benchmark', Values: ['Unikernel']};
const filter_linux_instance = [filter, {Name: 'tag:Type', Values: ['Linux']}];


var instanceIdLinux;
ec2.describeInstances({Filters: filter_linux_instance}, function(err, data){
    if (err) throw err;
    instanceIdLinux = data[0].Instances[0].InstanceId; 
});

var startTime;
var diffTime;

app.put('/metric/boot/start', (req, res) => {
    ec2.startInstances({InstanceIds: [instanceIdLinux]}, function(err, data){
        if (err) {
            res.writeHead(500);
            res.end();
        }
        startTime = process.hrtime();
        res.writeHead(200)
        res.end();
    }); 
});


app.get('/metric/boot/result', (req, res) => {

});

app.put('/metric/boot', (req, res) => {
    diffTime = process.hrtime(startTime);
    //TODO Condition
    ec2.stopInstances({InstanceIds: [instanceIdLinux]}, function(err, data){
        if (err) throw err;
        startTime = process.hrtime();
    });

    res.end();
});

app.listen(8080)