"""
Embedding Models Benchmark
Test different embedding models for speed and quality

Models to test:
1. nomic-embed-text:latest (current, 768-dim)
2. nomic-embed-text:v1.5 (newer version, 768-dim)
3. all-minilm-l6-v2 (faster, 384-dim)
4. mxbai-embed-large (quality, 1024-dim)

Expected Results:
- all-minilm-l6-v2: 2-3x faster than nomic (smaller dim)
- mxbai-embed-large: 1.5x slower but better quality
"""

import sys
import time
import json
import logging
import statistics
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.embedding_service import EmbeddingService
from utils.bsl_parser import BSLParser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmbeddingBenchmark:
    """
    Benchmark different embedding models

    Metrics:
    - Average embedding time (ms)
    - Embeddings per second
    - Model dimension
    - Error rate
    """

    def __init__(
        self,
        test_files: List[str],
        ollama_host: str = "http://localhost:11434"
    ):
        self.test_files = test_files
        self.ollama_host = ollama_host
        self.parser = BSLParser()

        # Models to test
        self.models = [
            {
                'name': 'nomic-embed-text:latest',
                'dimension': 768,
                'description': 'Current model (default)'
            },
            {
                'name': 'nomic-embed-text:v1.5',
                'dimension': 768,
                'description': 'Newer nomic version'
            },
            {
                'name': 'all-minilm:l6-v2',
                'dimension': 384,
                'description': 'Smaller/faster model'
            },
            {
                'name': 'mxbai-embed-large',
                'dimension': 1024,
                'description': 'Higher quality model'
            }
        ]

        self.results = []

    def prepare_test_texts(self) -> List[str]:
        """Parse test files and create searchable texts"""
        texts = []

        logger.info(f"Preparing {len(self.test_files)} test files...")

        for file_path in self.test_files:
            try:
                metadata = self.parser.parse_file(file_path)
                if metadata:
                    text = self.parser.extract_searchable_text(metadata)
                    texts.append(text)
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")

        logger.info(f"Prepared {len(texts)} test texts")
        return texts

    def benchmark_model(
        self,
        model_name: str,
        test_texts: List[str],
        warmup_runs: int = 2
    ) -> Dict:
        """
        Benchmark a single embedding model

        Args:
            model_name: Name of the model to test
            test_texts: List of texts to embed
            warmup_runs: Number of warmup iterations

        Returns:
            Dictionary with benchmark results
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Benchmarking: {model_name}")
        logger.info(f"{'='*60}")

        # Create embedding service
        try:
            service = EmbeddingService(
                ollama_host=self.ollama_host,
                model=model_name,
                cache_embeddings=False,
                timeout=120
            )
        except Exception as e:
            logger.error(f"Failed to create service for {model_name}: {e}")
            return {
                'model': model_name,
                'status': 'error',
                'error': str(e)
            }

        # Warmup (exclude from timing)
        logger.info(f"Warmup: {warmup_runs} iterations...")
        for i in range(min(warmup_runs, len(test_texts))):
            try:
                service.create_embedding(test_texts[i])
            except Exception as e:
                logger.warning(f"Warmup failed: {e}")

        # Benchmark
        times = []
        errors = 0
        successful_embeddings = []

        logger.info(f"Running benchmark on {len(test_texts)} texts...")

        for i, text in enumerate(test_texts, 1):
            start_time = time.time()

            try:
                embedding = service.create_embedding(text)

                if embedding:
                    elapsed_ms = (time.time() - start_time) * 1000
                    times.append(elapsed_ms)
                    successful_embeddings.append(embedding)

                    if i % 5 == 0:
                        avg_time = statistics.mean(times)
                        logger.info(
                            f"Progress: {i}/{len(test_texts)} | "
                            f"Avg: {avg_time:.1f} ms"
                        )
                else:
                    errors += 1
                    logger.warning(f"Failed to create embedding for text {i}")

            except Exception as e:
                errors += 1
                logger.error(f"Error processing text {i}: {e}")

        # Calculate statistics
        if not times:
            return {
                'model': model_name,
                'status': 'failed',
                'error': 'No successful embeddings'
            }

        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0

        embeddings_per_sec = 1000 / avg_time if avg_time > 0 else 0

        # Verify embedding dimension
        embedding_dim = len(successful_embeddings[0]) if successful_embeddings else 0

        result = {
            'model': model_name,
            'status': 'success',
            'total_texts': len(test_texts),
            'successful': len(times),
            'errors': errors,
            'error_rate_percent': (errors / len(test_texts)) * 100,
            'embedding_dimension': embedding_dim,
            'timing': {
                'avg_ms': round(avg_time, 2),
                'median_ms': round(median_time, 2),
                'min_ms': round(min_time, 2),
                'max_ms': round(max_time, 2),
                'std_dev_ms': round(std_dev, 2)
            },
            'throughput': {
                'embeddings_per_sec': round(embeddings_per_sec, 3),
                'embeddings_per_min': round(embeddings_per_sec * 60, 1),
                'embeddings_per_hour': round(embeddings_per_sec * 3600, 0)
            },
            'benchmarked_at': datetime.now().isoformat()
        }

        # Print results
        self._print_result(result)

        return result

    def _print_result(self, result: Dict):
        """Print formatted benchmark result"""
        print("\n" + "=" * 60)
        print(f"MODEL: {result['model']}")
        print("=" * 60)

        if result['status'] != 'success':
            print(f"[ERROR] {result.get('error', 'Unknown error')}")
            return

        print(f"Total texts:         {result['total_texts']}")
        print(f"Successful:          {result['successful']}")
        print(f"Errors:              {result['errors']} ({result['error_rate_percent']:.1f}%)")
        print(f"Embedding dimension: {result['embedding_dimension']}")
        print("\nTiming:")
        print(f"  Average:   {result['timing']['avg_ms']:.2f} ms")
        print(f"  Median:    {result['timing']['median_ms']:.2f} ms")
        print(f"  Min:       {result['timing']['min_ms']:.2f} ms")
        print(f"  Max:       {result['timing']['max_ms']:.2f} ms")
        print(f"  Std Dev:   {result['timing']['std_dev_ms']:.2f} ms")
        print("\nThroughput:")
        print(f"  Embeddings/sec:  {result['throughput']['embeddings_per_sec']:.3f}")
        print(f"  Embeddings/min:  {result['throughput']['embeddings_per_min']:.1f}")
        print(f"  Embeddings/hour: {result['throughput']['embeddings_per_hour']:.0f}")
        print("=" * 60)

    def run_benchmark(self) -> List[Dict]:
        """Run benchmark on all models"""
        logger.info("\n" + "=" * 60)
        logger.info("EMBEDDING MODELS BENCHMARK")
        logger.info("=" * 60)

        # Prepare test texts
        test_texts = self.prepare_test_texts()

        if not test_texts:
            logger.error("No test texts available!")
            return []

        logger.info(f"Testing {len(self.models)} models on {len(test_texts)} texts")

        # Benchmark each model
        for model_info in self.models:
            model_name = model_info['name']

            result = self.benchmark_model(model_name, test_texts)
            result['model_info'] = model_info

            self.results.append(result)

            # Brief pause between models
            time.sleep(2)

        return self.results

    def print_comparison(self):
        """Print comparison table of all models"""
        print("\n" + "=" * 80)
        print("MODELS COMPARISON")
        print("=" * 80)

        if not self.results:
            print("[WARNING] No results to compare")
            return

        # Find baseline (nomic-embed-text:latest)
        baseline = next(
            (r for r in self.results if r['model'] == 'nomic-embed-text:latest'),
            None
        )

        if not baseline or baseline['status'] != 'success':
            baseline = next((r for r in self.results if r['status'] == 'success'), None)

        if not baseline:
            print("[ERROR] No successful benchmarks to compare")
            return

        baseline_time = baseline['timing']['avg_ms']

        # Print header
        print(f"{'Model':<30} {'Dim':<6} {'Avg Time':<12} {'Speedup':<10} {'Emb/sec':<10} {'Status':<10}")
        print("-" * 80)

        # Print results
        for result in self.results:
            model = result['model'][:28]
            status = result['status']

            if status == 'success':
                dim = result['embedding_dimension']
                avg_time = result['timing']['avg_ms']
                speedup = baseline_time / avg_time if avg_time > 0 else 0
                emb_per_sec = result['throughput']['embeddings_per_sec']

                speedup_str = f"{speedup:.2f}x" if speedup != 1.0 else "1.00x (base)"

                print(
                    f"{model:<30} {dim:<6} {avg_time:>8.2f} ms  {speedup_str:<10} "
                    f"{emb_per_sec:>6.3f}     {'✅':<10}"
                )
            else:
                error = result.get('error', 'Unknown')[:20]
                print(f"{model:<30} {'N/A':<6} {'N/A':<12} {'N/A':<10} {'N/A':<10} ❌ {error}")

        print("=" * 80)

    def save_results(self, output_file: str = "benchmark_results.json"):
        """Save benchmark results to JSON file"""
        output_path = Path("data/benchmarks") / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            'metadata': {
                'benchmarked_at': datetime.now().isoformat(),
                'total_models': len(self.models),
                'test_files_count': len(self.test_files),
                'ollama_host': self.ollama_host
            },
            'results': self.results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logger.info(f"\n[OK] Results saved to: {output_path}")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Benchmark embedding models for BSL files"
    )
    parser.add_argument(
        "--source",
        default="../src",
        help="Source directory with BSL files"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=20,
        help="Maximum files to test (default: 20)"
    )
    parser.add_argument(
        "--ollama-host",
        default="http://localhost:11434",
        help="Ollama API host"
    )

    args = parser.parse_args()

    # Get test files
    source_path = Path(args.source)
    test_files = list(source_path.rglob("*.bsl"))[:args.max_files]

    if not test_files:
        logger.error(f"No BSL files found in {source_path}")
        sys.exit(1)

    logger.info(f"Selected {len(test_files)} test files from {source_path}")

    # Run benchmark
    benchmark = EmbeddingBenchmark(
        test_files=[str(f) for f in test_files],
        ollama_host=args.ollama_host
    )

    try:
        benchmark.run_benchmark()
        benchmark.print_comparison()
        benchmark.save_results()

    except KeyboardInterrupt:
        logger.info("\n[INTERRUPTED] Benchmark cancelled by user")
        if benchmark.results:
            benchmark.print_comparison()
            benchmark.save_results(output_file="benchmark_results_partial.json")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
