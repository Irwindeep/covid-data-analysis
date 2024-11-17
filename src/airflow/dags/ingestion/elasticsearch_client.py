from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

class ElasticsearchClient:
    def __init__(
            self,
            host : str ="localhost",
            port : int = 9200,
            scheme : str = "http"
    ) -> None:
        self.host = host
        self.port = port
        self.scheme = scheme
        self.client = Elasticsearch([{"host": self.host, "port": self.port, "scheme": self.scheme}])
        if not self.client.ping():
            raise ValueError("Connection to Elasticsearch failed!")
        logger.info(f"Connected to Elasticsearch at {self.host}:{self.port}")

    def create_index(self, index_name: str, body: dict) -> bool:
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name, body=body)
            logger.info(f"Created index: {index_name}")
            return True
        
        logger.warning(f"Index {index_name} already exists")
        return False

    def index_data(self, index_name: str, data: list) -> bool:
        try:
            actions = [
                {
                    "_op_type": "index",
                    "_index": index_name,
                    "_source": record
                }
                for record in data
            ]
            success, failed = bulk(self.client, actions)
            logger.info(f"Successfully indexed {success} documents. {failed} failed.")
            return True
        except Exception as e:
            logger.error(f"Error indexing data: {e}")
            return False

    def search_data(self, index_name: str, query: dict) -> list:
        try:
            response = self.client.search(index=index_name, body=query)
            hits = response.get("hits", {}).get("hits", [])
            logger.info(f"Found {len(hits)} documents in index {index_name}")
            return [hit["_source"] for hit in hits]
        except Exception as e:
            logger.error(f"Error searching data: {e}")
            return []
