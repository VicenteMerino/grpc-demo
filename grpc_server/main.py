import grpc
import test_pb2
import test_pb2_grpc
from dotenv import load_dotenv
import concurrent.futures
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()


class TestServicer(test_pb2_grpc.TestServicer):
    def PostData(self, request, context):
        return test_pb2.Response(message="ok", data=request.data)

    def PostDataBatch(self, request, context):
        data = request.data
        return test_pb2.ResponseBatch(message="ok", data=data)

    def PostDataBatchStreamRequest(self, request_iterator, context):
        data_list = []
        for item in request_iterator:
            data_list.append(item)
        return test_pb2.ResponseBatch(message="ok", data=data_list)

    def PostDataBatchStreamResponse(self, request, context):
        data = request.data
        for item in data:
            yield test_pb2.Response(message="ok", data=item)

    def PostDataBatchStreamBoth(self, request_iterator, context):
        for item in request_iterator:
            yield test_pb2.Response(message="ok", data=item)


def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    test_pb2_grpc.add_TestServicer_to_server(TestServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    logging.info("Server started")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
