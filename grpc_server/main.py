import grpc
import data_pb2
import data_pb2_grpc
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import concurrent.futures
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)

load_dotenv()
POSTGRES_URI = os.getenv(
    "POSTGRES_URI", "postgres://postgres:postgres@postgres:5432/postgres"
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


class TestServicer(data_pb2_grpc.TestServicer):
    def PostData(self, request, context):
        foo = request.foo
        bar = request.bar
        baz = request.baz
        hello = request.hello
        world = request.world
        lorem = request.lorem
        ipsum = request.ipsum
        with session_scope() as db_session:
            db_session.execute(
                text(
                    """
                SELECT * FROM data
                WHERE foo = :foo AND bar = :bar AND baz = :baz
                AND hello = :hello AND world = :world AND lorem = :lorem
                AND ipsum = :ipsum
                """
                ),
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
        return data_pb2.Response(
            message="ok",
            data=data_pb2.Data(
                foo=foo,
                bar=bar,
                baz=baz,
                hello=hello,
                world=world,
                lorem=lorem,
                ipsum=ipsum,
            ),
        )

    def PostDataBatch(self, request, context):
        data = request.data
        data_list = []
        with session_scope() as db_session:
            for item in data:
                foo = item.foo
                bar = item.bar
                baz = item.baz
                hello = item.hello
                world = item.world
                lorem = item.lorem
                ipsum = item.ipsum
                data_list.append(
                    {
                        "foo": foo,
                        "bar": bar,
                        "baz": baz,
                        "hello": hello,
                        "world": world,
                        "lorem": lorem,
                        "ipsum": ipsum,
                    }
                )
                db_session.execute(
                    text(
                        """
                    SELECT * FROM data
                    WHERE foo = :foo AND bar = :bar AND baz = :baz
                    AND hello = :hello AND world = :world AND lorem = :lorem
                    AND ipsum = :ipsum
                    """
                    ),
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

        return data_pb2.ResponseBatch(message="ok", data=data)


def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    data_pb2_grpc.add_TestServicer_to_server(TestServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    logging.info("Server started")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
