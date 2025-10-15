#!/usr/bin/env python3
"""
Simple CLI for Ad Cloner Platform
"""
import sys
import argparse
from pathlib import Path

from ad_cloner import AdCloner


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Clone winning ads with aggression variations using Sora 2'
    )

    parser.add_argument(
        'video',
        help='Path to winning ad video file or YouTube URL'
    )

    parser.add_argument(
        '-v', '--variants',
        nargs='+',
        choices=['soft', 'medium', 'aggressive', 'ultra'],
        help='Specific variants to generate (default: all 4)'
    )

    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only analyze video, don\'t generate variants'
    )

    args = parser.parse_args()

    # Initialize cloner
    cloner = AdCloner()

    if args.analyze_only:
        # Just analyze
        print("Analyzing video only...")
        analysis, path = cloner.analyzer.analyze_and_save(args.video)
        print(f"\nAnalysis saved to: {path}")
        return

    # Full pipeline
    results = cloner.clone_ad(args.video, variants=args.variants)

    print("\n✓ Done! Check the output/ directory for results.")


if __name__ == "__main__":
    main()
