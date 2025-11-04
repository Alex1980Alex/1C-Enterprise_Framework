"""
Compare Search Quality: all-minilm:l6-v2 vs nomic-embed-text:latest
Automatic testing of 5 typical queries on both collections
"""

import sys
from pathlib import Path

# Add parent directory to path BEFORE other imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict
from qdrant_client import QdrantClient
from services.embedding_service import EmbeddingService

def search_collection(
    qdrant: QdrantClient,
    collection_name: str,
    query_embedding: List[float],
    limit: int = 5
) -> List[Dict]:
    """Search in Qdrant collection"""
    results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=limit
    )

    return [{
        'score': hit.score,
        'file_path': hit.payload.get('file_path', ''),
        'module_type': hit.payload.get('module_type', ''),
        'functions_count': hit.payload.get('functions_count', 0)
    } for hit in results]


def compare_results(results1: List[Dict], results2: List[Dict]) -> Dict:
    """Compare two result sets"""
    files1 = {r['file_path'] for r in results1}
    files2 = {r['file_path'] for r in results2}

    overlap = files1.intersection(files2)
    overlap_percent = (len(overlap) / len(files1)) * 100 if files1 else 0

    return {
        'total': len(results1),
        'overlap': len(overlap),
        'overlap_percent': overlap_percent,
        'unique_to_1': len(files1 - files2),
        'unique_to_2': len(files2 - files1)
    }


def main():
    print("="*70)
    print("SEARCH QUALITY COMPARISON: all-minilm vs nomic")
    print("="*70)

    # Initialize services
    print("\n1. Initializing services...")
    qdrant = QdrantClient(host="localhost", port=6333)

    embedding_nomic = EmbeddingService(
        ollama_host="http://localhost:11434",
        model="nomic-embed-text:latest",
        cache_embeddings=False,
        timeout=60
    )

    embedding_minilm = EmbeddingService(
        ollama_host="http://localhost:11434",
        model="all-minilm:l6-v2",
        cache_embeddings=False,
        timeout=60
    )

    # Check collections exist
    try:
        collections = [c.name for c in qdrant.get_collections().collections]

        if 'bsl_code' not in collections:
            print("\n[ERROR] Collection 'bsl_code' not found!")
            print("   Wait for production Qdrant indexing to complete.")
            return

        if 'bsl_allminilm_test' not in collections:
            print("\n[ERROR] Collection 'bsl_allminilm_test' not found!")
            print("   Run test_allminilm_quality.py first.")
            return

    except Exception as e:
        print(f"\n[ERROR] connecting to Qdrant: {e}")
        return

    # Test queries (typical for 1C BSL code)
    test_queries = [
        "работа с документами",
        "проведение документа",
        "запись в регистр",
        "расчет остатков",
        "формирование отчета"
    ]

    print(f"\n2. Testing {len(test_queries)} queries on both collections...")
    print()

    total_overlap = 0
    results_data = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'-'*70}")
        print(f"Query {i}/5: \"{query}\"")
        print(f"{'-'*70}")

        # Create embeddings
        emb_nomic = embedding_nomic.create_embedding(query)
        emb_minilm = embedding_minilm.create_embedding(query)

        if not emb_nomic or not emb_minilm:
            print("  [FAILED] Failed to create embeddings, skipping...")
            continue

        # Search in both collections
        results_nomic = search_collection(qdrant, 'bsl_code', emb_nomic, limit=5)
        results_minilm = search_collection(qdrant, 'bsl_allminilm_test', emb_minilm, limit=5)

        # Compare
        comparison = compare_results(results_nomic, results_minilm)
        total_overlap += comparison['overlap_percent']

        results_data.append({
            'query': query,
            'comparison': comparison,
            'nomic_results': results_nomic,
            'minilm_results': results_minilm
        })

        # Print comparison
        print(f"\n  Top-5 Overlap: {comparison['overlap']}/5 ({comparison['overlap_percent']:.1f}%)")

        # Show top-3 from each
        print(f"\n  [NOMIC] nomic-embed-text (768-dim):")
        for j, r in enumerate(results_nomic[:3], 1):
            file_name = Path(r['file_path']).name if r['file_path'] else 'unknown'
            print(f"    {j}. {file_name[:50]:<50} (score: {r['score']:.4f})")

        print(f"\n  [MINILM] all-minilm:l6-v2 (384-dim):")
        for j, r in enumerate(results_minilm[:3], 1):
            file_name = Path(r['file_path']).name if r['file_path'] else 'unknown'
            marker = "*" if any(r['file_path'] == nr['file_path'] for nr in results_nomic[:3]) else " "
            print(f"    {j}. {marker} {file_name[:50]:<50} (score: {r['score']:.4f})")

    # Final summary
    avg_overlap = total_overlap / len(test_queries) if test_queries else 0

    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"\nQueries tested: {len(test_queries)}")
    print(f"Average top-5 overlap: {avg_overlap:.1f}%")

    # Verdict
    print("\n" + "-"*70)
    print("VERDICT:")
    print("-"*70)

    if avg_overlap >= 70:
        print("[OK] EXCELLENT - Top-5 overlap >= 70%")
        print("   Recommendation: SWITCH to all-minilm:l6-v2")
        print("   Benefit: 19x faster indexing (21h -> 1.1h)")
        verdict = "SWITCH"
    elif avg_overlap >= 50:
        print("[WARN] ACCEPTABLE - Top-5 overlap >= 50%")
        print("   Recommendation: SWITCH with monitoring")
        print("   Benefit: 19x faster vs slight quality drop")
        verdict = "SWITCH_WITH_CAUTION"
    else:
        print("[ERROR] POOR - Top-5 overlap < 50%")
        print("   Recommendation: STAY on nomic-embed-text")
        print("   Quality loss too significant for speedup")
        verdict = "STAY"

    print("\n" + "="*70)

    # Save detailed results
    output_file = Path("logs/search_quality_comparison.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("SEARCH QUALITY COMPARISON RESULTS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Average top-5 overlap: {avg_overlap:.1f}%\n")
        f.write(f"Verdict: {verdict}\n\n")

        for data in results_data:
            f.write(f"\nQuery: {data['query']}\n")
            f.write(f"Overlap: {data['comparison']['overlap_percent']:.1f}%\n")
            f.write("\nnomic-embed-text top-5:\n")
            for j, r in enumerate(data['nomic_results'], 1):
                f.write(f"  {j}. {r['file_path']} (score: {r['score']:.4f})\n")
            f.write("\nall-minilm:l6-v2 top-5:\n")
            for j, r in enumerate(data['minilm_results'], 1):
                f.write(f"  {j}. {r['file_path']} (score: {r['score']:.4f})\n")
            f.write("\n" + "="*70 + "\n")

    print(f"\nDetailed results saved to: {output_file}")
    print("="*70)


if __name__ == "__main__":
    main()
