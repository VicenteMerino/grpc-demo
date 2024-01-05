from locust import HttpUser, TaskSet, task
import grpc_user
import test_pb2
import test_pb2_grpc
import random
import json

with open("data.json", "r") as f:
    DATA = json.load(f)


class GrpcUser(grpc_user.GrpcUser):
    host = "grpc-run-enrj7ddetq-uc.a.run.app"
    stub_class = test_pb2_grpc.TestStub

    @task
    def post_data_batch(self):
        self.stub.PostDataBatch(test_pb2.DataBatch(data=random.sample(DATA, 100)))

    @task
    def post_data_batch_server_stream(self):
        self.stub.PostDataBatchStreamResponse(test_pb2.DataBatch(data=random.sample(DATA, 100)))

    @task
    def post_data_batch_client_stream(self):
        self.stub.PostDataBatchStreamRequest(iter([test_pb2.Data(**random.choice(DATA)) for _ in range(100)]))

    @task
    def post_data_batch_bi_stream(self):
        self.stub.PostDataBatchStreamBoth(iter([test_pb2.Data(**random.choice(DATA)) for _ in range(100)]))

# class RestTask(TaskSet):
#     @task
#     def post_data_batch(self):
#         self.client.post("/batch", json={"data": random.sample(DATA, 3000)})
        


# class RestUser(HttpUser):
#     tasks = [RestTask]
#     min_wait = 0
#     max_wait = 0
#     # host = "http://50.18.72.243:8080"
#     host = "https://fastapi-run-enrj7ddetq-uc.a.run.app"
