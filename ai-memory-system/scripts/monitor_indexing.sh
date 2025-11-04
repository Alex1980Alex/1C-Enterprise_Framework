#!/bin/bash
# Monitoring script for Qdrant indexing progress

LOG_FILE="logs/full_qdrant_indexing.log"

echo "🔍 Monitoring Qdrant Indexing Progress"
echo "======================================="
echo ""

while true; do
    clear
    echo "🔍 Qdrant Indexing Progress Monitor"
    echo "======================================="
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    if [ -f "$LOG_FILE" ]; then
        echo "📊 Latest Status:"
        tail -10 "$LOG_FILE" | grep -E "(Прогресс|Progress|Успешно|Обработано)"

        echo ""
        echo "📈 File Statistics:"
        echo "Total lines in log: $(wc -l < "$LOG_FILE")"

        echo ""
        echo "❌ Errors (last 5):"
        grep -i "error" "$LOG_FILE" | tail -5 || echo "  No errors found"

        echo ""
        echo "⚠️  Warnings (last 5):"
        grep -i "warning" "$LOG_FILE" | tail -5 || echo "  No warnings found"
    else
        echo "❌ Log file not found: $LOG_FILE"
    fi

    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo "Next update in 30 seconds..."

    sleep 30
done
