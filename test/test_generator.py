import sys
import os
import inspect
from inspect import signature

sys.path.append("..")

from data_api_client import DataAPIClient

client = DataAPIClient(data_type="mock", stage="dev", region_name=os.getenv("AWS_REGION"))

methods = inspect.getmembers(client, predicate=inspect.ismethod)

tests = []
methods.sort()

for m in methods:
    name = m[0]
    if not name[0:1] == "_":
        args = inspect.getfullargspec(m[1].__func__).args
        args.remove("self")
        print(f"def test_{name}(self):")
        for a in args:
            print(f"  {a} = None")
        print(f"  self.assertTrue(self.client.{name}({','.join(args)}))\n")
