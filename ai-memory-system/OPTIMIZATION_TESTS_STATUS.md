# Parameter Optimization Tests - Status & Monitoring

**Started**: 2025-11-03 05:32 (UTC+3)
**Status**: IN PROGRESS

---

## Test Configuration

### Tests Running
4 sequential tests, each on **300 BSL files**:

1. **Baseline (current)** - batch_size=5, max_workers=2
2. **Moderate (2x batch)** - batch_size=10, max_workers=3
3. **Aggressive (3x batch)** - batch_size=15, max_workers=4
4. **Maximum (4x batch)** - batch_size=20, max_workers=6

### Estimated Time
- **Per test**: 20-30 minutes
- **Total**: 2-3 hours

---

## Monitoring Commands

### Check Current Progress
```bash
tail -f ai-memory-system/logs/parameter_optimization.log
```

### Quick Status Check
```bash
cd ai-memory-system
echo "=== Last 30 lines of log ==="
tail -30 logs/parameter_optimization.log
```

### Check Test Results
```bash
cd ai-memory-system
ls -lh data/optimization_tests/
```

### Check Specific Test Logs
```bash
cd ai-memory-system/data/optimization_tests
tail -50 test_baseline_(current).log
tail -50 test_moderate_(2x_batch).log
tail -50 test_aggressive_(3x_batch).log
tail -50 test_maximum_(4x_batch).log
```

---

## Expected Output Files

After completion, the following files will be created:

### Logs (per test)
- `data/optimization_tests/test_baseline_(current).log`
- `data/optimization_tests/test_moderate_(2x_batch).log`
- `data/optimization_tests/test_aggressive_(3x_batch).log`
- `data/optimization_tests/test_maximum_(4x_batch).log`

### Index Files (per test)
- `data/optimization_tests/index_baseline_(current).json`
- `data/optimization_tests/index_moderate_(2x_batch).json`
- `data/optimization_tests/index_aggressive_(3x_batch).json`
- `data/optimization_tests/index_maximum_(4x_batch).json`

### Results Summary
- `data/optimization_tests/optimization_results.json` - Complete results with comparison
- `logs/parameter_optimization.log` - Main execution log

---

## Success Criteria

### Metrics to Compare
1. **Total time** (minutes)
2. **Speedup** vs baseline (Nx faster)
3. **Success rate** (% of 300 files)
4. **Speed** (files/sec)
5. **Projected time for 3973 files** (hours)

### Target
- **Goal**: Find configuration with 2-3x speedup
- **Acceptable**: ≥95% success rate
- **Optimal**: Best balance of speed and reliability

---

## What Happens Next

### Upon Completion
1. Script will print comparison table
2. Best configuration will be recommended
3. Projection for full 3973-file indexing will be calculated
4. Results saved to JSON

### Manual Analysis
After tests complete, check:
```bash
cd ai-memory-system
cat data/optimization_tests/optimization_results.json
```

Look for the "best configuration" section in the comparison output.

---

## If Tests Fail

### Check for Errors
```bash
grep -i "error\|failed\|exception" logs/parameter_optimization.log
```

### Check Process Status
```bash
ps aux | grep parameter_optimization
```

### Restart Individual Test
If a test fails, you can run it manually:
```bash
cd ai-memory-system
python scripts/indexing/bsl_indexer_async.py ../src \
  --output data/optimization_tests \
  --batch-size 15 \
  --max-workers 4 \
  --max-files 300 \
  --retry-attempts 2
```

---

## Background Process ID
- PID: 44819 (or check with `ps aux | grep parameter_optimization`)
- Log: `logs/parameter_optimization.log`
- Status: Running in background via `nohup`

---

**Last Updated**: 2025-11-03 05:35 UTC+3
