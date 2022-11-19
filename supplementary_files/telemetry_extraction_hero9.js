const goproTelemetry = require('gopro-telemetry');
const gpmfExtract = require('gpmf-extract');
const fs = require('fs');
const fastcsv = require('fast-csv');

var myArgs = process.argv.slice(2);
const file = myArgs[0]

//create buffer here
function bufferAppender(filepath, chunkSize) {
    return function(mp4boxFile) {
        var stream = fs.createReadStream(filepath, {highWaterMark: chunkSize});
        var bytesRead = 0;
        stream.on('end', () => {
            mp4boxFile.flush();
        });
        stream.on('data', (chunk) => {
            var arrayBuffer = new Uint8Array(chunk).buffer;
            arrayBuffer.fileStart = bytesRead;
            var next = mp4boxFile.appendBuffer(arrayBuffer);
            bytesRead += chunk.length;
        });
        stream.resume();
    }
}


//specify chunk size in second argument here (after "file"); larger chunk sizes for larger files
gpmfExtract(bufferAppender(file, 10*1024*1024))
    .then(extracted => {
    //gpmfExtract is first used to extract the video in an object named "extracted"
        goproTelemetry(extracted, {}, telemetry => {
            //goproTelemetry then manipulates this extracted object in "telemetry" object

            // retrieve GPS
            var GPS_data = telemetry[1].streams.GPS5.samples;

            // retrieve accelerometer
            var ACCL_data = telemetry[1].streams.ACCL.samples;

            // retrieve gyroscope
            var GYRO_data = telemetry[1].streams.GYRO.samples;
            
            // retrieve gravity vector
            var GRAV_data = telemetry[1].streams.GRAV.samples;

            // retrieve camera orientation quaternion
            var CORI_data = telemetry[1].streams.CORI.samples;

            // retrieve image orientation quaternion
            var IORI_data = telemetry[1].streams.IORI.samples;
            
            output_GPS = fs.createWriteStream(myArgs[1]);
            fastcsv.write(GPS_data, {headers: true})
            .pipe(output_GPS);

            output_ACCL = fs.createWriteStream(myArgs[2]);
            fastcsv.write(ACCL_data, {headers: true})
            .pipe(output_ACCL);

            output_GYRO = fs.createWriteStream(myArgs[3]);
            fastcsv.write(GYRO_data, {headers: true})
            .pipe(output_GYRO);

            output_GRAV = fs.createWriteStream(myArgs[4]);
            fastcsv.write(GRAV_data, {headers: true})
            .pipe(output_GRAV);

            output_CORI = fs.createWriteStream(myArgs[5]);
            fastcsv.write(CORI_data, {headers: true})
            .pipe(output_CORI);

            output_IORI = fs.createWriteStream(myArgs[6]);
            fastcsv.write(IORI_data, {headers: true})
            .pipe(output_IORI);

        });
    })
    .catch(error => console.error(error));
