const express = require('express')
const AWS = require('aws-sdk');
const app = express();

var ec2 = new AWS.EC2();
const filter = {Name: 'tag:Benchmark', Values: ['Unikernel']};
const filter_osv_instance = [filter, {Name: 'tag:Type', Values: ['OSV']}];


var instanceIdOSV;
ec2.describeInstances({Filters: filter_osv_instance}, function(err, data){
    if (err) throw err;
    instanceIdOSV = data[0].Instances[0].InstanceId; 
});

var startTime;
var diffTime;

app.put('/metric/boot/osv/start', (req, res) => {
    ec2.startInstances({InstanceIds: [instanceIdOSV]}, function(err, data){
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
    ec2.stopInstances({InstanceIds: [instanceIdOSV]}, function(err, data){
        if (err) throw err;
        startTime = process.hrtime();
    });

    res.end();
});

app.listen(8080)