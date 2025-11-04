"""
Upload indexed BSL modules from JSON to Qdrant
Загрузка проиндексированных BSL модулей из JSON в Qdrant
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QdrantUploader:
    """Upload embeddings to Qdrant from JSON index"""

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "bsl_code"
    ):
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.collection_name = collection_name

        logger.info(f"Connecting to Qdrant at {qdrant_host}:{qdrant_port}")
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)

    def recreate_collection(self, vector_dim: int = 768):
        """Recreate Qdrant collection with proper settings"""

        # Delete existing collection
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"[OK] Deleted existing collection: {self.collection_name}")
        except Exception as e:
            logger.info(f"Collection doesn't exist yet: {e}")

        # Create new collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_dim,
                distance=Distance.COSINE
            )
        )
        logger.info(f"[OK] Created collection: {self.collection_name} ({vector_dim}-dim, COSINE)")

    def load_index_json(self, json_path: str) -> Dict:
        """Load index JSON file"""
        logger.info(f"Loading index from: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"[OK] Loaded {len(data['files'])} files")
        logger.info(f"Metadata: {data['metadata']}")

        return data

    def upload_batch(self, files: List[Dict], batch_size: int = 100):
        """Upload files to Qdrant in batches"""

        total_files = len(files)
        logger.info(f"Starting upload: {total_files} points in batches of {batch_size}")

        uploaded = 0
        failed = 0

        for i in tqdm(range(0, total_files, batch_size), desc="Uploading batches"):
            batch = files[i:i+batch_size]

            try:
                points = []
                for idx, file_data in enumerate(batch, start=i):
                    # Create point
                    point = PointStruct(
                        id=idx,
                        vector=file_data['embedding'],
                        payload={
                            'file_path': file_data['file_path'],
                            'module_type': file_data.get('module_type', 'Unknown'),
                            'functions_count': file_data.get('functions_count', 0),
                            'variables_count': file_data.get('variables_count', 0),
                            'searchable_text': file_data.get('searchable_text', '')
                        }
                    )
                    points.append(point)

                # Upload batch
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )

                uploaded += len(points)

            except Exception as e:
                logger.error(f"[ERROR] Failed to upload batch {i}-{i+batch_size}: {e}")
                failed += len(batch)

        logger.info(f"\n[DONE] Upload complete!")
        logger.info(f"  Uploaded: {uploaded}/{total_files}")
        logger.info(f"  Failed:   {failed}")

        return uploaded, failed

    def verify_upload(self):
        """Verify collection status"""
        collection_info = self.client.get_collection(collection_name=self.collection_name)

        logger.info(f"\n[VERIFICATION]")
        logger.info(f"  Collection: {self.collection_name}")
        logger.info(f"  Points:     {collection_info.points_count}")
        logger.info(f"  Status:     {collection_info.status}")

        return collection_info.points_count


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Upload BSL index to Qdrant"
    )
    parser.add_argument(
        "--index",
        default="data/index/bsl_index_full.json",
        help="Path to index JSON file"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Qdrant host"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6333,
        help="Qdrant port"
    )
    parser.add_argument(
        "--collection",
        default="bsl_code",
        help="Collection name"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Upload batch size"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate collection (deletes existing data!)"
    )

    args = parser.parse_args()

    try:
        # Initialize uploader
        uploader = QdrantUploader(
            qdrant_host=args.host,
            qdrant_port=args.port,
            collection_name=args.collection
        )

        # Load index
        data = uploader.load_index_json(args.index)

        # Recreate collection if requested
        if args.recreate:
            logger.warning("[WARNING] Recreating collection - existing data will be DELETED!")
            vector_dim = data['metadata']['embedding_dimension']
            uploader.recreate_collection(vector_dim=vector_dim)

        # Upload files
        uploaded, failed = uploader.upload_batch(
            files=data['files'],
            batch_size=args.batch_size
        )

        # Verify
        points_count = uploader.verify_upload()

        if points_count == len(data['files']):
            logger.info(f"\n[SUCCESS] All {points_count} points uploaded successfully!")
        else:
            logger.warning(f"\n[WARNING] Expected {len(data['files'])} points, got {points_count}")

    except KeyboardInterrupt:
        logger.info("\n[INTERRUPTED] Upload cancelled by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
