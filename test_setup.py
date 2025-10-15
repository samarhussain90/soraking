#!/usr/bin/env python3
"""
Test script to verify Ad Cloner setup
"""
import sys
from pathlib import Path

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    try:
        import google.generativeai as genai
        print("✓ google-generativeai")
    except ImportError as e:
        print(f"✗ google-generativeai: {e}")
        return False

    try:
        from openai import OpenAI
        print("✓ openai")
    except ImportError as e:
        print(f"✗ openai: {e}")
        return False

    try:
        import config
        print("✓ config")
    except ImportError as e:
        print(f"✗ config: {e}")
        return False

    return True

def test_api_keys():
    """Test API keys are configured"""
    print("\nTesting API keys...")
    from config import Config

    if Config.OPENAI_API_KEY:
        key_preview = Config.OPENAI_API_KEY[:15] + "..." + Config.OPENAI_API_KEY[-4:]
        print(f"✓ OPENAI_API_KEY: {key_preview}")
    else:
        print("✗ OPENAI_API_KEY not found")
        return False

    if Config.GEMINI_API_KEY:
        key_preview = Config.GEMINI_API_KEY[:15] + "..." + Config.GEMINI_API_KEY[-4:]
        print(f"✓ GEMINI_API_KEY: {key_preview}")
    else:
        print("✗ GEMINI_API_KEY not found")
        return False

    return True

def test_directories():
    """Test output directories are created"""
    print("\nTesting directories...")
    from config import Config

    for dir_name, dir_path in [
        ("OUTPUT", Config.OUTPUT_DIR),
        ("ANALYSIS", Config.ANALYSIS_DIR),
        ("VIDEOS", Config.VIDEOS_DIR),
        ("LOGS", Config.LOGS_DIR),
        ("TEMPLATES", Config.TEMPLATES_DIR)
    ]:
        if dir_path.exists():
            print(f"✓ {dir_name}: {dir_path}")
        else:
            print(f"✗ {dir_name} not found: {dir_path}")
            return False

    return True

def test_ffmpeg():
    """Test ffmpeg availability"""
    print("\nTesting ffmpeg...")
    import subprocess

    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        version_line = result.stdout.decode().split('\n')[0]
        print(f"✓ ffmpeg: {version_line}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ffmpeg not found. Install with: brew install ffmpeg")
        return False

def test_modules():
    """Test custom modules can be imported"""
    print("\nTesting custom modules...")

    modules = [
        "modules.gemini_analyzer",
        "modules.aggression_variants",
        "modules.sora_prompt_builder",
        "modules.sora_client",
        "modules.video_assembler"
    ]

    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"✗ {module_name}: {e}")
            return False

    return True

def main():
    """Run all tests"""
    print("="*70)
    print("AD CLONER SETUP TEST")
    print("="*70)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("API Keys", test_api_keys()))
    results.append(("Directories", test_directories()))
    results.append(("ffmpeg", test_ffmpeg()))
    results.append(("Modules", test_modules()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s} {status}")
        if not passed:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\n✓ All tests passed! System ready.")
        print("\nTry running:")
        print("  python cli.py --help")
        return 0
    else:
        print("\n✗ Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
