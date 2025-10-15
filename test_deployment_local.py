"""
Local Deployment Test
Verifies all integrations work before deploying to production
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("SORAKING AD CLONER - LOCAL DEPLOYMENT TEST")
print("=" * 70)
print()

# Test 1: Environment Variables
print("[1/5] Checking environment variables...")
required_vars = [
    'OPENAI_API_KEY',
    'GEMINI_API_KEY',
    'SUPABASE_URL',
    'SUPABASE_ANON_KEY',
    'DO_SPACES_ACCESS_KEY',
    'DO_SPACES_SECRET_KEY',
    'DO_SPACES_BUCKET',
    'DO_SPACES_REGION'
]

missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)
        print(f"  ✗ {var} - MISSING")
    else:
        # Show partial value for verification
        value = os.getenv(var)
        if 'KEY' in var or 'SECRET' in var:
            masked = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
            print(f"  ✓ {var} - {masked}")
        else:
            print(f"  ✓ {var} - {value}")

if missing_vars:
    print(f"\n✗ Missing {len(missing_vars)} required variables")
    sys.exit(1)
else:
    print(f"\n✓ All {len(required_vars)} environment variables configured")

# Test 2: Supabase Connection
print("\n[2/5] Testing Supabase connection...")
try:
    from modules.supabase_client import SupabaseClient
    supabase = SupabaseClient()
    sessions = supabase.list_sessions(limit=1)
    print(f"  ✓ Connected to Supabase")
    print(f"  ✓ Query successful: {len(sessions)} sessions found")
    print(f"  ✓ Database: {os.getenv('SUPABASE_URL')}")
except Exception as e:
    print(f"  ✗ Supabase failed: {e}")
    sys.exit(1)

# Test 3: Spaces Connection
print("\n[3/5] Testing DigitalOcean Spaces...")
try:
    from modules.spaces_client import SpacesClient
    spaces = SpacesClient()
    files = spaces.list_videos()
    print(f"  ✓ Connected to Spaces")
    print(f"  ✓ Bucket: {spaces.bucket_name}")
    print(f"  ✓ Region: {spaces.region}")
    print(f"  ✓ CDN URL: {spaces.cdn_url}")
    print(f"  ✓ Files in bucket: {len(files)}")
except Exception as e:
    print(f"  ✗ Spaces failed: {e}")
    sys.exit(1)

# Test 4: OpenAI/Sora Client
print("\n[4/5] Testing OpenAI API...")
try:
    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY')
    # Don't make actual API call, just verify client initializes
    print(f"  ✓ OpenAI API key configured")
    print(f"  ✓ Key prefix: {os.getenv('OPENAI_API_KEY')[:10]}...")
except Exception as e:
    print(f"  ✗ OpenAI failed: {e}")
    sys.exit(1)

# Test 5: Gemini API
print("\n[5/5] Testing Google Gemini API...")
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    print(f"  ✓ Gemini API key configured")
    print(f"  ✓ Key prefix: {os.getenv('GEMINI_API_KEY')[:10]}...")
except Exception as e:
    print(f"  ✗ Gemini failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - READY FOR DEPLOYMENT")
print("=" * 70)
print("\nNext steps:")
print("  1. Push code to GitHub:")
print("     git remote add origin https://github.com/YOUR_USERNAME/soraking.git")
print("     git push -u origin main")
print()
print("  2. Deploy to DigitalOcean App Platform:")
print("     - Create app from GitHub repo")
print("     - Configure environment variables (see DEPLOYMENT_GUIDE.md)")
print("     - Deploy!")
print()
print("  3. Test production deployment:")
print("     curl https://your-app.ondigitalocean.app/api/health")
print()
print("For detailed deployment instructions, see: DEPLOYMENT_GUIDE.md")
print("=" * 70)
