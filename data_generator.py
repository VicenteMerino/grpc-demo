import random
import string
import json

ALPHABET = string.ascii_letters + string.digits
data = [
    {
        "foo": "".join(random.choices(ALPHABET, k=255)),
        "bar": random.randint(0, 100000),
        "baz": random.choice([True, False]),
        "hello": "".join(random.choices(ALPHABET, k=255)),
        "world": random.randint(0, 100000),
        "lorem": random.choice([True, False]),
        "ipsum": "".join(random.choices(ALPHABET, k=255)),
    }
    for _ in range(10000)
]

with open("load-tests/data.json", "w") as f:
    json.dump(data, f)