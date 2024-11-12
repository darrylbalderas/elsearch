run_mongo:
	# Run MongoDB
	docker run -d --name mongodb -p 27017:27017 mongo

run_elastic:
	# Run Elasticsearch (set password to `elastic`)
	docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "ELASTIC_PASSWORD=elastic" docker.elastic.co/elasticsearch/elasticsearch:8.5.0

run_api:
	uvicorn main:app --reload

load_data:
	curl -X POST http://127.0.0.1:8000/load-data/ -H "Content-Type: application/json"
	curl -X POST http://127.0.0.1:8000/index-data/ -H "Content-Type: application/json"

purge_data:
	curl -X POST http://127.0.0.1:8000/purge-data/ -H "Content-Type: application/json"

sample_search:
	curl -X GET "http://127.0.0.1:8000/search/?query=speakers" -H "Content-Type: application/json"
