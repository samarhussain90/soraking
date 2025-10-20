#!/usr/bin/env python3
"""
Simple CLI for Viral Hook Generator
"""
import sys
import argparse
from pathlib import Path

from ad_cloner import ViralHookGenerator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Generate viral 12-second hooks for any affiliate marketing vertical using Sora 2 Pro'
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

    # Initialize hook generator
    generator = ViralHookGenerator()

    if args.analyze_only:
        # Just analyze
        print("Analyzing video only...")
        analysis, path = generator.analyzer.analyze_and_save(args.video)
        print(f"\nAnalysis saved to: {path}")
        return

    # Full pipeline
    results = generator.generate_hooks(args.video, variants=args.variants)

    print("\n✓ Done! Check the output/ directory for viral hooks.")


if __name__ == "__main__":
    main()
