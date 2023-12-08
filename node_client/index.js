const express = require('express');
const app = express();
const axios = require('axios');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';
const GRPC_URL = process.env.GRPC_URL || 'http://localhost:50051';
const PORT = process.env.PORT || 3000;

const PROTO_PATH = `${__dirname}/proto/test.proto`;
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});
const test = grpc.loadPackageDefinition(packageDefinition).test;
const stub = new test.TestService(GRPC_URL, grpc.credentials.createInsecure());

app.use(express.json());

app.get('/', (req, res) => {
  res.send('Hello from Node.js app \n');
});

app.post("/rest/single-query", async (req, res) => {
  const { query } = req.body;
  const response = await axios.post(`${FASTAPI_URL}/`, { query });
  res.send(response.data);
});

app.post("/rest/multi-query", async (req, res) => {
  const { queries } = req.body;
  const response = await axios.post(`${FASTAPI_URL}/batch`, { queries });
  res.send(response.data);
});

app.post("/grpc/single-query", async (req, res) => {
  const { query } = req.body;
  const response = stub.Query({ query });
  res.send(response);
});

app.post("/grpc/multi-query", async (req, res) => {
  const { queries } = req.body;
  const response = stub.BatchQuery({ queries });
  res.send(response);
});

app.listen(PORT, () => {
  console.log(`Node.js app listening at http://localhost:${PORT}`);
});