const goproTelemetry = require('gopro-telemetry');
const gpmfExtract = require('gpmf-extract');
const fs = require('fs');
const fastcsv = require('fast-csv');

var myArgs = process.argv.slice(2);

const file = fs.readFileSync(myArgs[0]);

gpmfExtract(file)
    .then(extracted => {
    //gpmfExtract is first used to extract the video in an object named "extracted"
        goproTelemetry(extracted, {}, telemetry => {
            //goproTelemetry then manipulates this extracted object in "telemetry" object

            //prints the values, timestamp and count of GPS metadata per point
            var GPS_data = telemetry[1].streams.GPS5.samples;
            //console.log(GPS_data);
            //console.log('\nThere are ', GPS_data.length, ' GPS data samples\n');

            //prints the values, timestamp and count of IMU metadata per point (in rad/s)
            var IMU_data = telemetry[1].streams.GYRO.samples;
            //console.log(IMU_data.slice(0,3));
            

            
            output_IMU = fs.createWriteStream(myArgs[1]);
            fastcsv.write(IMU_data, {headers: true})
            .pipe(output_IMU);

            output_GPS = fs.createWriteStream(myArgs[2]);
            fastcsv.write(GPS_data, {headers: true})
            .pipe(output_GPS);

        });
    })
    .catch(error => console.error(error));
