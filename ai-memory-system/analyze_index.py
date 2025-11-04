"""
Анализ JSON файлов индекса
"""
import json
from pathlib import Path

index_file = Path("data/index/bsl_index_full.json")

print(f"[INFO] Analyzing file: {index_file}")
print(f"[INFO] File size: {index_file.stat().st_size / (1024*1024):.2f} MB")
print()

try:
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"[OK] File successfully read")
    print(f"[INFO] Data type: {type(data).__name__}")

    if isinstance(data, list):
        print(f"[INFO] Total records: {len(data)}")
        if len(data) > 0:
            print(f"\n[INFO] Example of first record:")
            first = data[0]
            print(f"   Keys: {list(first.keys()) if isinstance(first, dict) else 'N/A'}")
            if isinstance(first, dict):
                for key, value in first.items():
                    if key == 'embedding':
                        print(f"   {key}: <vector length {len(value) if isinstance(value, list) else 'N/A'}>")
                    else:
                        value_str = str(value)[:100]
                        print(f"   {key}: {value_str}")

    elif isinstance(data, dict):
        print(f"[INFO] Total keys: {len(data)}")
        print(f"   Keys: {list(data.keys())}")

        # Анализ metadata
        if 'metadata' in data:
            print(f"\n[INFO] Metadata:")
            for key, value in data['metadata'].items():
                print(f"   {key}: {value}")

        # Анализ files
        if 'files' in data:
            files = data['files']
            print(f"\n[INFO] Files section:")
            print(f"   Type: {type(files).__name__}")
            print(f"   Total files indexed: {len(files) if isinstance(files, (list, dict)) else 'N/A'}")

            if isinstance(files, list) and len(files) > 0:
                print(f"\n[INFO] Example of first file:")
                first_file = files[0]
                if isinstance(first_file, dict):
                    for key, value in first_file.items():
                        if key == 'embedding':
                            print(f"   {key}: <vector length {len(value) if isinstance(value, list) else 'N/A'}>")
                        else:
                            value_str = str(value)[:150]
                            print(f"   {key}: {value_str}")

            elif isinstance(files, dict):
                print(f"   First 3 file paths: {list(files.keys())[:3]}")

    print("\n[SUCCESS] Analysis complete!")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
