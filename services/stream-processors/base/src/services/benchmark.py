import os

from pymongo import MongoClient


class BenchmarkDataSaver:
    def __init__(self, collection):
        self._collection = collection

    def save(self, benchmark_data):
        self._collection.insert_one(benchmark_data)


mongo_client = MongoClient(os.getenv("MONGO_URI"))
database = mongo_client.get_database("arion_benchmark")
collection = database.get_collection("benchmark_data")
benchmark_data_saver = BenchmarkDataSaver(collection)
