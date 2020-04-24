import net from 'net';
import fs from 'fs';
import * as bodyPix from '@tensorflow-models/body-pix';
import * as tf from '@tensorflow/tfjs-node';
import { Tensor3D } from '@tensorflow/tfjs-node';

const SOCKET_FILE = '/tmp/partitioner.sock';

export default async function () {
  const model = await bodyPix.load({
    architecture: 'MobileNetV1',
    outputStride: 16,
    multiplier: 0.75,
    quantBytes: 2,
  });

  if (fs.existsSync(SOCKET_FILE)) {
    fs.unlinkSync(SOCKET_FILE);
  }

  net
    .createServer((stream) => {
      let chunks: Buffer[] = [];
      stream.on('data', async (chunk) => {
        chunks.push(chunk);

        try {
          const image = tf.node.decodeImage(Buffer.concat(chunks)) as Tensor3D;
          const segmentation = await model.segmentPerson(image, {
            flipHorizontal: false,
            internalResolution: 'medium',
            segmentationThreshold: 0.8,
          });
          const data = Buffer.from(segmentation.data);
          stream.write(data);
          tf.dispose(image);
          chunks = [];
        } catch (e) {
          console.error(e);
        }
      });

      stream.on('close', () => console.log('client closed connection.'));
    })
    .listen(SOCKET_FILE)
    .on('listening', () => console.log('server ready.'))
    .on('connection', () => console.log('connection received.'));
}
