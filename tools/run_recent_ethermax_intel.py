#!/usr/bin/env python3
import asyncio
import argparse
from maxx_intelligence_analyzer import MAXXIntelligenceAnalyzer

async def main():
    parser = argparse.ArgumentParser(description="Fetch last N MAXX transfers and export intelligence")
    parser.add_argument('--limit', type=int, default=1000, help='Number of recent transfers to fetch')
    parser.add_argument('--page-size', type=int, default=100, help='Page size per API request')
    parser.add_argument('--csv', type=str, help='Path to BaseScan/Etherscan CSV export to import instead of API')
    args = parser.parse_args()

    analyzer = MAXXIntelligenceAnalyzer()
    if args.csv:
        trades = await analyzer.import_trades_from_csv(args.csv, limit=args.limit)
    else:
        trades = await analyzer.collect_recent_trades(limit=args.limit, page_size=args.page_size)
        if not trades:
            # Fallback to logs-based scan
            trades = await analyzer.collect_recent_trades_via_logs(limit=args.limit, step=2000)
    # Run core analyses on these trades
    pumps = await analyzer.analyze_pump_patterns(trades)
    whales = await analyzer.identify_whale_activity(trades)
    coordinated = await analyzer.detect_coordinated_activity(trades)
    await analyzer.generate_trading_signals(trades, pumps, whales, coordinated)
    report = await analyzer.export_intelligence_report()
    print("Summary:", report["summary"])  # compact output

if __name__ == '__main__':
    asyncio.run(main())
