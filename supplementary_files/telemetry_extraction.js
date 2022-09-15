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


            //prints the values, timestamp and count of GYRO metadata per point (in rad/s)
            var GYRO_data = telemetry[1].streams.GYRO.samples;
            
            //prints the values, timestamp and count of ACCL metadata per point (in m/s^2)
            var ACCL_data = telemetry[1].streams.ACCL.samples;

            //prints the values, timestamp and count of MAGN metadata per point (in micro teslas)
            //var MAGN_data = telemetry[1].streams.MAGN.samples;
            
            output_GYRO = fs.createWriteStream(myArgs[1]);
            fastcsv.write(GYRO_data, {headers: true})
            .pipe(output_GYRO);

            output_ACCL = fs.createWriteStream(myArgs[2]);
            fastcsv.write(ACCL_data, {headers: true})
            .pipe(output_ACCL);

            //output_MAGN = fs.createWriteStream(myArgs[3]);
            //fastcsv.write(MAGN_data, {headers : true})
            //.pipe(output_MAGN);

            output_GPS = fs.createWriteStream(myArgs[4]);
            fastcsv.write(GPS_data, {headers: true})
            .pipe(output_GPS);

        });
    })
    .catch(error => console.error(error));
