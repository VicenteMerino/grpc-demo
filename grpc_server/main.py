import grpc
import test_pb2
import test_pb2_grpc
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import concurrent.futures
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)

load_dotenv()
POSTGRES_URI = os.getenv(
    "POSTGRES_URI", "postgresql://postgres:postgres@postgres:5432/postgres"
)
QUERY = text(
    """
    SELECT * FROM data
    WHERE foo = :foo AND bar = :bar AND baz = :baz
    AND hello = :hello AND world = :world AND lorem = :lorem
    AND ipsum = :ipsum
    """
)

engine = create_engine(POSTGRES_URI)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = engine.connect()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class TestServicer(test_pb2_grpc.TestServicer):
    def execute_query_from_item(self, db_session, request):
        foo = request.foo
        bar = request.bar
        baz = request.baz
        hello = request.hello
        world = request.world
        lorem = request.lorem
        ipsum = request.ipsum
        db_session.execute(
            QUERY,
            {
                "foo": foo,
                "bar": bar,
                "baz": baz,
                "hello": hello,
                "world": world,
                "lorem": lorem,
                "ipsum": ipsum,
            },
        )
        return {
            "foo": foo,
            "bar": bar,
            "baz": baz,
            "hello": hello,
            "world": world,
            "lorem": lorem,
            "ipsum": ipsum,
        }

    def PostData(self, request, context):
        with session_scope() as db_session:
            data = self.execute_query_from_item(db_session, request)
        return test_pb2.Response(message="ok", data=data)

    def PostDataBatch(self, request, context):
        data = request.data
        data_list = []
        with session_scope() as db_session:
            for item in data:
                data = self.execute_query_from_item(db_session, item)
                data_list.append(data)
        return test_pb2.ResponseBatch(message="ok", data=data)

    def PostDataBatchStreamRequest(self, request_iterator, context):
        data_list = []
        with session_scope() as db_session:
            for item in request_iterator:
                data = self.execute_query_from_item(db_session, item)
                data_list.append(data)

        return test_pb2.ResponseBatch(message="ok", data=data_list)

    def PostDataBatchStreamResponse(self, request, context):
        data = request.data
        with session_scope() as db_session:
            for item in data:
                streamed_data = self.execute_query_from_item(db_session, item)
                yield test_pb2.Response(message="ok", data=streamed_data)

    def PostDataBatchStreamBoth(self, request_iterator, context):
        with session_scope() as db_session:
            for item in request_iterator:
                streamed_data = self.execute_query_from_item(db_session, item)
                yield test_pb2.Response(message="ok", data=streamed_data)


def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    test_pb2_grpc.add_TestServicer_to_server(TestServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    logging.info("Server started")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
