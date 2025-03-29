const goproTelemetry = require('gopro-telemetry');
const gpmfExtract = require('gpmf-extract');
const fs = require('fs');
const fastcsv = require('fast-csv');

// Get command-line arguments (after the first two: node and script path)
// myArgs[0] : input video
// myArgs[1] : output file for GPS stream (optional)
// myArgs[2] : output file for ACCL stream (optional)
// myArgs[3] : output file for GYRO stream (optional)
// myArgs[4] : output file for GRAV stream (optional)
// myArgs[5] : output file for IORI stream (optional)
var myArgs = process.argv.slice(2);
const inputFile = myArgs[0];

// Create a buffer appender to process the video file in chunks.
function bufferAppender(filepath, chunkSize) {
    return function(mp4boxFile) {
        var stream = fs.createReadStream(filepath, { highWaterMark: chunkSize });
        var bytesRead = 0;
        stream.on('end', () => {
            mp4boxFile.flush();
        });
        stream.on('data', (chunk) => {
            var arrayBuffer = new Uint8Array(chunk).buffer;
            arrayBuffer.fileStart = bytesRead;
            mp4boxFile.appendBuffer(arrayBuffer);
            bytesRead += chunk.length;
        });
        stream.resume();
    }
}

// Extract telemetry from the input file.
gpmfExtract(bufferAppender(inputFile, 10 * 1024 * 1024))
    .then(extracted => {
        // Process telemetry data.
        goproTelemetry(extracted, {}, telemetry => {

            // Conditionally extract GPS stream if an output file is provided.
            if (myArgs[1] && myArgs[1].trim() !== '') {
                var GPS_data = telemetry[1].streams.GPS5.samples;
                var output_GPS = fs.createWriteStream(myArgs[1]);
                fastcsv.write(GPS_data, { headers: true }).pipe(output_GPS);
            }

            // Conditionally extract accelerometer stream.
            if (myArgs[2] && myArgs[2].trim() !== '') {
                var ACCL_data = telemetry[1].streams.ACCL.samples;
                var output_ACCL = fs.createWriteStream(myArgs[2]);
                fastcsv.write(ACCL_data, { headers: true }).pipe(output_ACCL);
            }

            // Conditionally extract gyroscope stream.
            if (myArgs[3] && myArgs[3].trim() !== '') {
                var GYRO_data = telemetry[1].streams.GYRO.samples;
                var output_GYRO = fs.createWriteStream(myArgs[3]);
                fastcsv.write(GYRO_data, { headers: true }).pipe(output_GYRO);
            }

            // Conditionally extract gravity vector stream.
            if (myArgs[4] && myArgs[4].trim() !== '') {
                var GRAV_data = telemetry[1].streams.GRAV.samples;
                var output_GRAV = fs.createWriteStream(myArgs[4]);
                fastcsv.write(GRAV_data, { headers: true }).pipe(output_GRAV);
            }

            // Conditionally extract image orientation quaternion stream.
            if (myArgs[5] && myArgs[5].trim() !== '') {
                var IORI_data = telemetry[1].streams.IORI.samples;
                var output_IORI = fs.createWriteStream(myArgs[5]);
                fastcsv.write(IORI_data, { headers: true }).pipe(output_IORI);
            }
        });
    })
    .catch(error => console.error(error));
