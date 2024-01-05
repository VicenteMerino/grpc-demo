import grpc
import test_pb2
import test_pb2_grpc
from dotenv import load_dotenv
import concurrent.futures
import logging
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)

load_dotenv()


class TestServicer(test_pb2_grpc.TestServicer):
    def PostDataBatch(self, request, context):
        data = request.data
        return test_pb2.ResponseBatch(data=data)

    def PostDataBatchStreamRequest(self, request_iterator, context):
        return test_pb2.ResponseBatch(data=[item for item in request_iterator])

    def PostDataBatchStreamResponse(self, request, context):
        data = request.data
        for item in data:
            yield test_pb2.Response(data=item)

    def PostDataBatchStreamBoth(self, request_iterator, context):
        for item in request_iterator:
            yield test_pb2.Response(data=item)


def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    test_pb2_grpc.add_TestServicer_to_server(TestServicer(), server)
    server.add_insecure_port(f"[::]:{os.getenv('PORT', 50051)}")
    server.start()
    logging.info("Server started")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
