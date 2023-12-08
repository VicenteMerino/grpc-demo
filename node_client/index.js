const express = require('express');
const axios = require('axios');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://fastapi-server:8080';
const GRPC_URL = process.env.GRPC_URL || 'grpc-server:50051';
const PORT = process.env.PORT || 3000;

const PROTO_PATH = `${__dirname}/protos/test.proto`;
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {});
const test = grpc.loadPackageDefinition(packageDefinition).test;
const stub = new test.Test(GRPC_URL, grpc.credentials.createInsecure());
const app = express();

app.use(express.json());

app.get('/', (req, res) => {
  res.send('Hello from Node.js app \n');
});

app.post("/rest/single-query", async (req, res) => {
  const data = req.body;
  await axios.post(`${FASTAPI_URL}/`, data);
  res.send("Received from FastAPI server");
});

app.post("/rest/multi-query", async (req, res) => {
  const dataBatch = req.body;
  await axios.post(`${FASTAPI_URL}/batch`, dataBatch);
  res.send("Received from FastAPI server");
});

app.post("/grpc/single-query", (req, res) => {
  const data = req.body;
  stub.PostData(data, (err, response) => {
    if (err) {
      console.log(err);
      res.status(500).send(err);
    } else {
      console.log(`"Received from gRPC server: ${JSON.stringify(response)}"`);
      res.send("Received from gRPC server");
    }
  }
  );
});

app.post("/grpc/multi-query", (req, res) => {
  const dataBatch = req.body;
  stub.PostDataBatch(dataBatch, (err, response) => {
    if (err) {
      console.log(err);
      res.status(500).send(err);
    } else {
      console.log(`"Received from gRPC server: ${JSON.stringify(response)}"`);
      res.send("Received from gRPC server");
    }
  });
});


app.post("/grpc/multi-query/stream-request", (req, res) => {
  const dataBatchStream = stub.PostDataBatchStreamRequest((err, response) => {
    if (err) {
      console.log(err);
      res.status(500).send(err);
    } else {
      console.log(`"Received from gRPC server: ${JSON.stringify(response)}"`);
      res.send("Received from gRPC server");
    }
  });

  const { data: dataBatch } = req.body;
  dataBatch.forEach(data => {
    dataBatchStream.write(data);
  });

  dataBatchStream.end();
});

app.post("/grpc/multi-query/stream-response", (req, res) => {
  const dataBatch = req.body;
  const dataBatchStream = stub.PostDataBatchStreamResponse(dataBatch, (err, response) => {
    console.log(`"Received from gRPC server: ${JSON.stringify(response)}"`);
  });

  dataBatchStream.on('data', (response) => {
    console.log(`"Received from gRPC server: ${JSON.stringify(response)}"`);
  }
  );
  dataBatchStream.on('end', () => {
    res.send("Received from gRPC server");
  });
});


app.post("/grpc/multi-query/stream-both", (req, res) => {
  const dataBatchStream = stub.PostDataBatchStreamBoth((err, response) => {
    console.log(`"Received from gRPC server: ${JSON.stringify(response)}"`);
  });
  dataBatchStream.on('data', (response) => {
    console.log(`"Received from gRPC server: ${JSON.stringify(response)}"`);
  });

  dataBatchStream.on('end', () => {
    res.send("Received from gRPC server");
  });

  const { data: dataBatch } = req.body;

  dataBatch.forEach(data => {
    dataBatchStream.write(data);
  });
  dataBatchStream.end();
});

app.listen(PORT, () => {
  console.log(`Node.js app listening at http://localhost:${PORT}`);
});