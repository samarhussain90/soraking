#!/usr/bin/env python3
"""Debug script to check what CSS is loading on the deployed site"""

from playwright.sync_api import sync_playwright
import json

def debug_site():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=" * 80)
        print("DEBUGGING CSS ON DEPLOYED SITE")
        print("=" * 80)

        # Navigate to the deployed site
        url = "https://soraking-ad-cloner-7lwcv.ondigitalocean.app/"
        print(f"\n1. Navigating to: {url}")
        page.goto(url, wait_until="networkidle")

        # Check what stylesheets are loaded
        print("\n2. Checking loaded stylesheets:")
        stylesheets = page.query_selector_all('link[rel="stylesheet"]')
        for i, sheet in enumerate(stylesheets, 1):
            href = sheet.get_attribute('href')
            print(f"   [{i}] {href}")

        # Check if styles.css is loading
        print("\n3. Checking styles.css response:")
        try:
            response = page.goto(url.rstrip('/') + '/styles.css', wait_until="networkidle")
            print(f"   Status: {response.status}")
            print(f"   OK: {response.ok}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")

            # Get first 500 chars of CSS
            css_content = page.content()
            if 'CSS IS LOADING' in css_content:
                print(f"   ✓ CSS marker found!")
            else:
                print(f"   ✗ CSS marker NOT found")
        except Exception as e:
            print(f"   Error loading styles.css: {e}")

        # Go back to main page
        page.goto(url, wait_until="networkidle")

        # Check computed styles on body
        print("\n4. Checking computed styles on <body>:")
        body_bg = page.evaluate("""
            () => window.getComputedStyle(document.body).background
        """)
        body_padding = page.evaluate("""
            () => window.getComputedStyle(document.body).padding
        """)
        print(f"   Background: {body_bg[:100] if len(body_bg) > 100 else body_bg}")
        print(f"   Padding: {body_padding}")

        # Check computed styles on header
        print("\n5. Checking computed styles on .header:")
        header_exists = page.query_selector('.header')
        if header_exists:
            header_bg = page.evaluate("""
                () => window.getComputedStyle(document.querySelector('.header')).background
            """)
            header_padding = page.evaluate("""
                () => window.getComputedStyle(document.querySelector('.header')).padding
            """)
            header_backdrop = page.evaluate("""
                () => window.getComputedStyle(document.querySelector('.header')).backdropFilter ||
                      window.getComputedStyle(document.querySelector('.header')).webkitBackdropFilter
            """)
            print(f"   Background: {header_bg[:100] if len(header_bg) > 100 else header_bg}")
            print(f"   Padding: {header_padding}")
            print(f"   Backdrop Filter: {header_backdrop}")
        else:
            print("   ✗ .header element not found!")

        # Check computed styles on first card
        print("\n6. Checking computed styles on .card:")
        card_exists = page.query_selector('.card')
        if card_exists:
            card_bg = page.evaluate("""
                () => window.getComputedStyle(document.querySelector('.card')).background
            """)
            card_padding = page.evaluate("""
                () => window.getComputedStyle(document.querySelector('.card')).padding
            """)
            card_backdrop = page.evaluate("""
                () => window.getComputedStyle(document.querySelector('.card')).backdropFilter ||
                      window.getComputedStyle(document.querySelector('.card')).webkitBackdropFilter
            """)
            print(f"   Background: {card_bg[:100] if len(card_bg) > 100 else card_bg}")
            print(f"   Padding: {card_padding}")
            print(f"   Backdrop Filter: {card_backdrop}")
        else:
            print("   ✗ .card element not found!")

        # Take a screenshot
        print("\n7. Taking screenshot...")
        page.screenshot(path="deployed_site_debug.png", full_page=True)
        print("   Screenshot saved to: deployed_site_debug.png")

        # Check network requests for CSS
        print("\n8. Checking CSS file content:")
        css_url = url.rstrip('/') + '/styles.css?v=2'
        response = page.goto(css_url)
        if response.ok:
            css_text = page.evaluate("() => document.body.innerText")
            print(f"   CSS file size: {len(css_text)} bytes")

            # Check for key markers
            markers = [
                ('Gradient background', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'),
                ('Large padding', '--spacing-2xl: 64px'),
                ('Glassmorphism', 'backdrop-filter: blur(20px)'),
                ('CSS marker', 'CSS IS LOADING'),
            ]

            print("\n   Key CSS features:")
            for name, marker in markers:
                if marker in css_text:
                    print(f"   ✓ {name}: FOUND")
                else:
                    print(f"   ✗ {name}: MISSING")
        else:
            print(f"   ✗ Failed to load CSS: {response.status}")

        browser.close()

        print("\n" + "=" * 80)
        print("DEBUG COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    debug_site()
