import { MongoClient, Collection, Document } from 'mongodb';

import { env } from '../env.js';

export class BenchmarkDataSaver {
  constructor(private readonly collection: Collection) {}

  async save(data: Document): Promise<void> {
    await this.collection.insertOne(data);
  }
}

export const mongoClient = new MongoClient(env.MONGO_URI);

export const database = mongoClient.db('arion_benchmark');

export const collection = database.collection('benchmark_data');

export const benchmarkDataSaver = new BenchmarkDataSaver(collection);
