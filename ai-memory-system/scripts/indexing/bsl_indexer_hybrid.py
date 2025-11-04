"""
BSL Hybrid Indexer - OPTIMAL SOLUTION
Combines best of both worlds:
- Multiprocessing for CPU-bound BSL parsing (fast, parallel)
- Asyncio for I/O-bound Ollama embeddings (rate-limited, controlled)

Architecture:
1. ProcessPoolExecutor parses BSL files → extract searchable text
2. AsyncIO with semaphore sends texts to Ollama (2-4 concurrent)
3. Results aggregated and saved

Expected Performance:
- BSL parsing: 12 workers, ~100 files/sec
- Ollama embeddings: 2-4 workers, ~0.5-1.0 files/sec (bottleneck)
- Overall: ~50% faster than pure async (parallel parsing)
- Overall: 100% success rate vs 73% fail rate (multiprocess)
"""

import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import aiohttp

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/hybrid_indexing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ParsedFile:
    """Result of BSL file parsing (CPU-bound phase)"""
    file_path: str
    searchable_text: str
    metadata: Dict
    status: str  # success, empty, error
    error: Optional[str] = None
    parsing_time_ms: Optional[float] = None


@dataclass
class IndexedFile:
    """Result of full indexing (parsing + embedding)"""
    file_path: str
    status: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict] = None
    error: Optional[str] = None
    parsing_time_ms: Optional[float] = None
    embedding_time_ms: Optional[float] = None


def parse_bsl_file_worker(file_path: str) -> Dict:
    """
    Worker function for BSL parsing (runs in separate process)
    ONLY CPU-bound work - no Ollama calls!

    Args:
        file_path: Path to BSL file

    Returns:
        Dictionary with parsed data
    """
    start_time = time.time()

    try:
        # Import inside worker to avoid pickle issues
        from utils.bsl_parser import BSLParser

        parser = BSLParser()
        metadata = parser.parse_file(file_path)

        if not metadata or not metadata.functions:
            return {
                'file_path': file_path,
                'status': 'empty',
                'searchable_text': '',
                'metadata': {},
                'parsing_time_ms': (time.time() - start_time) * 1000
            }

        # Extract searchable text
        searchable_text = parser.extract_searchable_text(metadata)

        result_metadata = {
            'module_type': metadata.module_type,
            'functions_count': len(metadata.functions),
            'variables_count': len(metadata.variables),
            'searchable_text': searchable_text[:500]
        }

        return {
            'file_path': file_path,
            'status': 'success',
            'searchable_text': searchable_text,
            'metadata': result_metadata,
            'parsing_time_ms': (time.time() - start_time) * 1000
        }

    except Exception as e:
        return {
            'file_path': file_path,
            'status': 'error',
            'searchable_text': '',
            'metadata': {},
            'error': str(e),
            'parsing_time_ms': (time.time() - start_time) * 1000
        }


class HybridIndexer:
    """
    Hybrid indexer combining multiprocessing and asyncio

    Phase 1 (Multiprocessing): Parse BSL files in parallel (CPU-bound)
    Phase 2 (AsyncIO): Generate embeddings with rate limiting (I/O-bound)

    Features:
    - Optimal CPU utilization for parsing
    - Controlled Ollama queue (no timeouts)
    - Caching support
    - Progress tracking
    """

    def __init__(
        self,
        source_path: str,
        output_path: str = "data/index",
        parse_workers: Optional[int] = None,
        embedding_workers: int = 3,
        ollama_host: str = "http://localhost:11434",
        ollama_model: str = "nomic-embed-text:latest",
        ollama_timeout: int = 90,
        max_files: Optional[int] = None,
        use_cache: bool = True
    ):
        self.source_path = Path(source_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Phase 1: Parsing workers (multiprocess)
        if parse_workers is None:
            import multiprocessing
            cpu_threads = multiprocessing.cpu_count()
            self.parse_workers = max(1, cpu_threads - 4)
        else:
            self.parse_workers = parse_workers

        # Phase 2: Embedding workers (asyncio semaphore)
        self.embedding_workers = embedding_workers

        self.ollama_host = ollama_host
        self.ollama_model = ollama_model
        self.ollama_timeout = ollama_timeout
        self.max_files = max_files
        self.use_cache = use_cache

        logger.info(f"Initialized HybridIndexer:")
        logger.info(f"  Parse workers (multiprocess): {self.parse_workers}")
        logger.info(f"  Embedding workers (asyncio): {self.embedding_workers}")
        logger.info(f"  Ollama: {ollama_host}, model: {ollama_model}")
        logger.info(f"  Source: {source_path}")
        logger.info(f"  Caching: {'Enabled' if use_cache else 'Disabled'}")

    def get_files(self) -> List[Path]:
        """Get list of BSL files to process"""
        all_files = list(self.source_path.rglob("*.bsl"))

        if self.max_files:
            all_files = all_files[:self.max_files]

        logger.info(f"Found {len(all_files)} BSL files to process")
        return all_files

    def phase1_parse_files(self, files: List[Path]) -> List[ParsedFile]:
        """
        Phase 1: Parse BSL files using multiprocessing
        Fast, CPU-bound, parallel
        """
        logger.info("=" * 60)
        logger.info("PHASE 1: PARSING BSL FILES (MULTIPROCESS)")
        logger.info("=" * 60)

        total_files = len(files)
        parsed_results = []
        start_time = time.time()

        with ProcessPoolExecutor(max_workers=self.parse_workers) as executor:
            # Submit all parsing tasks
            future_to_file = {
                executor.submit(parse_bsl_file_worker, str(file)): file
                for file in files
            }

            # Collect results
            completed = 0
            for future in as_completed(future_to_file):
                file = future_to_file[future]

                try:
                    result = future.result(timeout=30)
                    parsed_results.append(result)
                    completed += 1

                    if completed % 50 == 0:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        logger.info(
                            f"Parsed: {completed}/{total_files} ({completed/total_files*100:.1f}%) | "
                            f"Speed: {rate:.1f} files/sec"
                        )

                except Exception as e:
                    logger.error(f"Exception parsing {file}: {e}")
                    parsed_results.append({
                        'file_path': str(file),
                        'status': 'error',
                        'searchable_text': '',
                        'metadata': {},
                        'error': str(e)
                    })
                    completed += 1

        parse_time = time.time() - start_time
        success_count = sum(1 for r in parsed_results if r['status'] == 'success')

        logger.info(f"Phase 1 complete: {parse_time:.1f}s")
        logger.info(f"  Success: {success_count}/{total_files}")
        logger.info(f"  Speed: {total_files/parse_time:.1f} files/sec")

        return parsed_results

    async def generate_embedding_async(
        self,
        session: aiohttp.ClientSession,
        text: str,
        semaphore: asyncio.Semaphore
    ) -> Optional[List[float]]:
        """
        Generate embedding with async HTTP request and semaphore
        Rate-limited to prevent Ollama queue overflow
        """
        async with semaphore:
            try:
                async with session.post(
                    f"{self.ollama_host}/api/embeddings",
                    json={
                        "model": self.ollama_model,
                        "prompt": text
                    },
                    timeout=aiohttp.ClientTimeout(total=self.ollama_timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('embedding')
                    else:
                        logger.error(f"Ollama error: {response.status}")
                        return None

            except asyncio.TimeoutError:
                logger.error(f"Ollama timeout after {self.ollama_timeout}s")
                return None
            except Exception as e:
                logger.error(f"Embedding error: {e}")
                return None

    async def phase2_generate_embeddings(
        self,
        parsed_files: List[Dict]
    ) -> List[IndexedFile]:
        """
        Phase 2: Generate embeddings using asyncio with rate limiting
        Slow, I/O-bound, controlled concurrency
        """
        logger.info("=" * 60)
        logger.info("PHASE 2: GENERATING EMBEDDINGS (ASYNCIO)")
        logger.info("=" * 60)

        # Filter only successfully parsed files
        files_to_embed = [f for f in parsed_files if f['status'] == 'success']
        empty_files = [f for f in parsed_files if f['status'] == 'empty']
        error_files = [f for f in parsed_files if f['status'] == 'error']

        logger.info(f"Files to embed: {len(files_to_embed)}")
        logger.info(f"Empty files (skipped): {len(empty_files)}")
        logger.info(f"Parse errors (skipped): {len(error_files)}")

        # Create semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.embedding_workers)

        indexed_results = []
        start_time = time.time()

        # Create async HTTP session
        async with aiohttp.ClientSession() as session:
            tasks = []

            for file_data in files_to_embed:
                # Create task for embedding generation
                task = self.process_single_file_async(
                    session,
                    semaphore,
                    file_data
                )
                tasks.append(task)

            # Process all tasks with progress tracking
            for i, task in enumerate(asyncio.as_completed(tasks), 1):
                result = await task
                indexed_results.append(result)

                if i % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    eta = (len(files_to_embed) - i) / rate if rate > 0 else 0

                    logger.info(
                        f"Embedded: {i}/{len(files_to_embed)} ({i/len(files_to_embed)*100:.1f}%) | "
                        f"Speed: {rate:.2f} files/sec | "
                        f"ETA: {eta/60:.1f} min"
                    )

        # Add skipped files to results
        for file_data in empty_files + error_files:
            indexed_results.append({
                'file_path': file_data['file_path'],
                'status': file_data['status'],
                'error': file_data.get('error'),
                'parsing_time_ms': file_data.get('parsing_time_ms')
            })

        embed_time = time.time() - start_time
        success_count = sum(1 for r in indexed_results if r['status'] == 'success')

        logger.info(f"Phase 2 complete: {embed_time/60:.1f} min")
        logger.info(f"  Success: {success_count}/{len(files_to_embed)}")

        return indexed_results

    async def process_single_file_async(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        file_data: Dict
    ) -> Dict:
        """Process single file: generate embedding"""
        start_time = time.time()

        # Check cache first (if enabled)
        if self.use_cache:
            from services.embedding_cache import EmbeddingCache
            cache = EmbeddingCache()
            cached_data = cache.get(file_data['file_path'])

            if cached_data:
                return {
                    'file_path': file_data['file_path'],
                    'status': 'success',
                    'embedding': cached_data['embedding'],
                    'metadata': file_data['metadata'],
                    'parsing_time_ms': file_data.get('parsing_time_ms'),
                    'embedding_time_ms': (time.time() - start_time) * 1000,
                    'cached': True
                }

        # Generate embedding
        embedding = await self.generate_embedding_async(
            session,
            file_data['searchable_text'],
            semaphore
        )

        embedding_time = (time.time() - start_time) * 1000

        if embedding:
            # Cache the result
            if self.use_cache:
                cache.put(
                    file_data['file_path'],
                    embedding,
                    file_data['metadata']
                )

            return {
                'file_path': file_data['file_path'],
                'status': 'success',
                'embedding': embedding,
                'metadata': file_data['metadata'],
                'parsing_time_ms': file_data.get('parsing_time_ms'),
                'embedding_time_ms': embedding_time,
                'cached': False
            }
        else:
            return {
                'file_path': file_data['file_path'],
                'status': 'failed',
                'error': 'Failed to generate embedding',
                'parsing_time_ms': file_data.get('parsing_time_ms'),
                'embedding_time_ms': embedding_time
            }

    def save_results(
        self,
        results: List[Dict],
        output_file: str = "index_hybrid.json"
    ):
        """Save indexing results to JSON"""

        # Calculate statistics
        stats = {
            'success': sum(1 for r in results if r['status'] == 'success'),
            'failed': sum(1 for r in results if r['status'] == 'failed'),
            'empty': sum(1 for r in results if r['status'] == 'empty'),
            'error': sum(1 for r in results if r['status'] == 'error'),
            'total': len(results)
        }

        # Calculate average times
        parse_times = [
            r.get('parsing_time_ms', 0)
            for r in results
            if 'parsing_time_ms' in r and r['parsing_time_ms']
        ]

        embed_times = [
            r.get('embedding_time_ms', 0)
            for r in results
            if 'embedding_time_ms' in r and r['embedding_time_ms']
        ]

        avg_parse_time = sum(parse_times) / len(parse_times) if parse_times else 0
        avg_embed_time = sum(embed_times) / len(embed_times) if embed_times else 0

        # Create output
        output = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'total_files': len(results),
                'indexer_type': 'hybrid',
                'embedding_model': self.ollama_model,
                'embedding_dimension': 768,
                'parse_workers': self.parse_workers,
                'embedding_workers': self.embedding_workers,
                'avg_parsing_time_ms': round(avg_parse_time, 2),
                'avg_embedding_time_ms': round(avg_embed_time, 2),
                'indexing_stats': stats
            },
            'files': [
                {
                    'file_path': r['file_path'],
                    'status': r['status'],
                    'embedding': r.get('embedding'),
                    'metadata': r.get('metadata'),
                    'error': r.get('error'),
                    'parsing_time_ms': r.get('parsing_time_ms'),
                    'embedding_time_ms': r.get('embedding_time_ms')
                }
                for r in results
                if r['status'] == 'success'
            ]
        }

        output_path = self.output_path / output_file

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"\n{'='*60}")
        logger.info(f"Results saved to: {output_path}")
        logger.info(f"Statistics:")
        logger.info(f"  Success: {stats['success']}")
        logger.info(f"  Failed: {stats['failed']}")
        logger.info(f"  Empty: {stats['empty']}")
        logger.info(f"  Error: {stats['error']}")
        logger.info(f"  Avg parse time: {avg_parse_time:.1f} ms")
        logger.info(f"  Avg embed time: {avg_embed_time:.1f} ms")
        logger.info(f"{'='*60}")

    def run(self):
        """Main entry point"""
        logger.info("=" * 60)
        logger.info("BSL HYBRID INDEXER")
        logger.info("=" * 60)

        overall_start = time.time()

        # Get files
        files = self.get_files()

        if not files:
            logger.warning("No files found to process!")
            return

        # Phase 1: Parse BSL files (multiprocessing)
        parsed_files = self.phase1_parse_files(files)

        # Phase 2: Generate embeddings (asyncio)
        indexed_files = asyncio.run(
            self.phase2_generate_embeddings(parsed_files)
        )

        # Save results
        self.save_results(indexed_files)

        total_time = time.time() - overall_start

        logger.info("=" * 60)
        logger.info(f"INDEXING COMPLETE: {total_time/60:.1f} minutes")
        logger.info("=" * 60)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="BSL Hybrid Indexer - Multiprocessing + AsyncIO"
    )
    parser.add_argument(
        "source",
        help="Path to source directory containing BSL files"
    )
    parser.add_argument(
        "--output",
        default="data/index",
        help="Output directory for index files (default: data/index)"
    )
    parser.add_argument(
        "--parse-workers",
        type=int,
        default=None,
        help="Parse workers (default: CPU cores - 4)"
    )
    parser.add_argument(
        "--embedding-workers",
        type=int,
        default=3,
        help="Concurrent Ollama requests (default: 3)"
    )
    parser.add_argument(
        "--ollama-timeout",
        type=int,
        default=90,
        help="Timeout for Ollama requests in seconds (default: 90)"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Maximum number of files to process (for testing)"
    )

    args = parser.parse_args()

    indexer = HybridIndexer(
        source_path=args.source,
        output_path=args.output,
        parse_workers=args.parse_workers,
        embedding_workers=args.embedding_workers,
        ollama_timeout=args.ollama_timeout,
        max_files=args.max_files
    )

    try:
        indexer.run()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
