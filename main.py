# app.py
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError
import json

app = FastAPI()

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["example_db"]
mongo_collection = mongo_db["example_collection"]

# Elasticsearch setup
ES_HOST = "http://localhost:9200"
es_client = Elasticsearch(ES_HOST, basic_auth=("elastic", "elastic"))


@app.get("/")
async def root():
    return {"message": "Welcome to the MongoDB + Elasticsearch + FastAPI prototype!"}


@app.post("/load-data/")
async def load_data():
    with open("products.json") as fin:
        data = json.load(fin)
    try:
        mongo_collection.insert_many(data)
        return {"message": "Data loaded successfully into MongoDB"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index-data/")
async def index_data():
    try:
        # Fetch data from MongoDB
        documents = list(mongo_collection.find({}, {"_id": 0}))

        # Index documents in Elasticsearch
        for doc in documents:
            es_client.index(index="products", id=doc["id"], document=doc)

        return {"message": "Data indexed in Elasticsearch"}
    except ESConnectionError:
        raise HTTPException(status_code=500, detail="Error connecting to Elasticsearch")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/purge-data/")
async def purge_data():
    try:
        # Purge data from MongoDB
        mongo_collection.delete_many({})  # Deletes all documents in the collection

        # Purge data from Elasticsearch
        es_client.indices.delete(
            index="products", ignore=[400, 404]
        )  # Deletes the 'products' index if it exists

        return {"message": "Data purged from MongoDB and Elasticsearch"}
    except ESConnectionError:
        raise HTTPException(status_code=500, detail="Error connecting to Elasticsearch")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/")
async def search(query: str):
    try:
        # Perform search in Elasticsearch
        response = es_client.search(
            index="products", query={"match": {"description": query}}
        )

        # Extract relevant search results
        hits = response["hits"]["hits"]
        results = [hit["_source"] for hit in hits]

        return {"results": results}
    except ESConnectionError:
        raise HTTPException(status_code=500, detail="Error connecting to Elasticsearch")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
