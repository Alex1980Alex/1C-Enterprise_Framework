"""
Embedding Cache Service
File hash-based caching for embeddings

Benefits:
- Skip unchanged files (instant indexing)
- Disk-based persistence
- Hash-based validation (detects file changes)
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """
    File hash-based embedding cache

    Architecture:
    cache/embeddings/
    ├── metadata.json (cache info)
    └── <file_hash>.json (per-file embeddings)

    Features:
    - SHA256 hash-based file identification
    - Automatic invalidation on file changes
    - Disk persistence
    - Statistics tracking
    """

    def __init__(self, cache_dir: str = "cache/embeddings"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"

        # Initialize metadata
        self.metadata = self._load_metadata()

        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0
        }

        logger.info(f"EmbeddingCache initialized: {self.cache_dir}")
        logger.info(f"Cached files: {self.metadata.get('total_cached', 0)}")

    def _load_metadata(self) -> Dict:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")

        return {
            'created_at': datetime.now().isoformat(),
            'total_cached': 0,
            'last_updated': None
        }

    def _save_metadata(self):
        """Save cache metadata"""
        self.metadata['last_updated'] = datetime.now().isoformat()
        self.metadata['total_cached'] = len(list(self.cache_dir.glob("*.json"))) - 1  # Exclude metadata.json

        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")

    def _file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file content

        Args:
            file_path: Path to file

        Returns:
            SHA256 hex digest
        """
        sha256 = hashlib.sha256()

        try:
            with open(file_path, 'rb') as f:
                # Read in chunks for memory efficiency
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)

            return sha256.hexdigest()

        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return None

    def get(self, file_path: str) -> Optional[Dict]:
        """
        Get cached embedding if file unchanged

        Args:
            file_path: Path to BSL file

        Returns:
            Dictionary with embedding and metadata, or None if not cached/changed
        """
        file_hash = self._file_hash(file_path)
        if not file_hash:
            return None

        cache_file = self.cache_dir / f"{file_hash}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)

                # Validate file path matches
                if cached_data.get('file_path') != file_path:
                    # Hash collision or file moved
                    logger.warning(f"Cache path mismatch for {file_path}")
                    return None

                self.stats['hits'] += 1
                logger.debug(f"Cache HIT: {file_path}")

                return cached_data

            except Exception as e:
                logger.error(f"Error reading cache for {file_path}: {e}")
                return None

        self.stats['misses'] += 1
        logger.debug(f"Cache MISS: {file_path}")
        return None

    def put(self, file_path: str, embedding: List[float], metadata: Optional[Dict] = None):
        """
        Cache embedding with file hash

        Args:
            file_path: Path to BSL file
            embedding: Embedding vector
            metadata: Optional metadata
        """
        file_hash = self._file_hash(file_path)
        if not file_hash:
            logger.error(f"Cannot cache {file_path}: hash calculation failed")
            return

        cache_file = self.cache_dir / f"{file_hash}.json"

        cache_data = {
            'file_path': file_path,
            'file_hash': file_hash,
            'embedding': embedding,
            'metadata': metadata or {},
            'cached_at': datetime.now().isoformat()
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            self.stats['saves'] += 1
            logger.debug(f"Cached: {file_path}")

            # Update metadata periodically
            if self.stats['saves'] % 10 == 0:
                self._save_metadata()

        except Exception as e:
            logger.error(f"Error caching {file_path}: {e}")

    def clear(self):
        """Clear all cached embeddings"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file != self.metadata_file:
                    cache_file.unlink()

            self.metadata['total_cached'] = 0
            self._save_metadata()

            logger.info("Cache cleared")

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_stats(self) -> Dict:
        """
        Get cache statistics

        Returns:
            Dictionary with statistics
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'saves': self.stats['saves'],
            'total_requests': total_requests,
            'hit_rate_percent': hit_rate,
            'total_cached': self.metadata.get('total_cached', 0),
            'cache_dir': str(self.cache_dir),
            'cache_size_mb': self._get_cache_size()
        }

    def _get_cache_size(self) -> float:
        """Calculate cache size in MB"""
        total_size = 0

        try:
            for cache_file in self.cache_dir.rglob("*.json"):
                total_size += cache_file.stat().st_size

            return total_size / (1024 * 1024)

        except Exception as e:
            logger.error(f"Error calculating cache size: {e}")
            return 0.0

    def print_stats(self):
        """Print cache statistics"""
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("EMBEDDING CACHE STATISTICS")
        print("=" * 60)
        print(f"Total requests:  {stats['total_requests']}")
        print(f"Cache hits:      {stats['hits']}")
        print(f"Cache misses:    {stats['misses']}")
        print(f"Hit rate:        {stats['hit_rate_percent']:.1f}%")
        print(f"New saves:       {stats['saves']}")
        print(f"Total cached:    {stats['total_cached']} files")
        print(f"Cache size:      {stats['cache_size_mb']:.2f} MB")
        print(f"Cache directory: {stats['cache_dir']}")
        print("=" * 60 + "\n")


# Example usage
if __name__ == "__main__":
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create cache
    cache = EmbeddingCache()

    # Test file
    test_file = "../src/projects/configuration/251029_GKSTCPLK-1831/src/Ext/ManagedApplicationModule.bsl"

    if Path(test_file).exists():
        # Test GET (should be miss)
        result = cache.get(test_file)
        print(f"First GET: {'HIT' if result else 'MISS'}")

        # Test PUT
        test_embedding = [0.1] * 768  # Dummy embedding
        test_metadata = {'functions_count': 3, 'module_type': 'Unknown'}
        cache.put(test_file, test_embedding, test_metadata)
        print("PUT: Cached test embedding")

        # Test GET again (should be hit)
        result = cache.get(test_file)
        print(f"Second GET: {'HIT' if result else 'MISS'}")

        if result:
            print(f"Cached embedding length: {len(result['embedding'])}")
            print(f"Cached metadata: {result['metadata']}")

    # Print statistics
    cache.print_stats()
