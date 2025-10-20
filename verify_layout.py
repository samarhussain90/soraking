#!/usr/bin/env python3
"""Verify the new sidebar layout is deployed correctly"""

from playwright.sync_api import sync_playwright

def verify_layout():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=" * 80)
        print("VERIFYING NEW SIDEBAR LAYOUT")
        print("=" * 80)

        url = "https://soraking-ad-cloner-7lwcv.ondigitalocean.app/"
        print(f"\n1. Navigating to: {url}")
        page.goto(url, wait_until="networkidle")

        # Check for sidebar element
        print("\n2. Checking for sidebar element:")
        sidebar = page.query_selector('.sidebar')
        if sidebar:
            print("   ✓ Sidebar element exists")

            # Check sidebar positioning
            sidebar_styles = page.evaluate("""
                () => {
                    const sidebar = document.querySelector('.sidebar');
                    const styles = window.getComputedStyle(sidebar);
                    return {
                        position: styles.position,
                        width: styles.width,
                        left: styles.left,
                        background: styles.background
                    };
                }
            """)
            print(f"   Position: {sidebar_styles['position']}")
            print(f"   Width: {sidebar_styles['width']}")
            print(f"   Left: {sidebar_styles['left']}")

            if sidebar_styles['position'] == 'fixed' and sidebar_styles['width'] == '240px':
                print("   ✓ Sidebar has correct fixed positioning and width")
            else:
                print("   ✗ Sidebar positioning/width incorrect")
        else:
            print("   ✗ Sidebar element NOT found!")

        # Check for top bar
        print("\n3. Checking for top bar:")
        topbar = page.query_selector('.top-bar')
        if topbar:
            print("   ✓ Top bar element exists")
            topbar_styles = page.evaluate("""
                () => {
                    const topbar = document.querySelector('.top-bar');
                    const styles = window.getComputedStyle(topbar);
                    return {
                        position: styles.position,
                        height: styles.height
                    };
                }
            """)
            print(f"   Position: {topbar_styles['position']}")
            print(f"   Height: {topbar_styles['height']}")
        else:
            print("   ✗ Top bar NOT found!")

        # Check for main content
        print("\n4. Checking for main content:")
        main_content = page.query_selector('.main-content')
        if main_content:
            print("   ✓ Main content element exists")
            main_styles = page.evaluate("""
                () => {
                    const main = document.querySelector('.main-content');
                    const styles = window.getComputedStyle(main);
                    return {
                        marginLeft: styles.marginLeft,
                        background: styles.background
                    };
                }
            """)
            print(f"   Margin-left: {main_styles['marginLeft']}")

            if main_styles['marginLeft'] == '240px':
                print("   ✓ Main content has correct offset for sidebar")
            else:
                print("   ✗ Main content margin incorrect")
        else:
            print("   ✗ Main content NOT found!")

        # Check for two-column content grid
        print("\n5. Checking for content wrapper grid:")
        content_wrapper = page.query_selector('.content-wrapper')
        if content_wrapper:
            print("   ✓ Content wrapper element exists")
            grid_styles = page.evaluate("""
                () => {
                    const wrapper = document.querySelector('.content-wrapper');
                    const styles = window.getComputedStyle(wrapper);
                    return {
                        display: styles.display,
                        gridTemplateColumns: styles.gridTemplateColumns
                    };
                }
            """)
            print(f"   Display: {grid_styles['display']}")
            print(f"   Grid columns: {grid_styles['gridTemplateColumns']}")
        else:
            print("   ✗ Content wrapper NOT found!")

        # Check page title changed
        print("\n6. Checking page title:")
        title = page.title()
        print(f"   Title: {title}")
        if title == "Ad Cloner Studio":
            print("   ✓ Title updated to 'Ad Cloner Studio'")
        else:
            print(f"   ✗ Title not updated (expected 'Ad Cloner Studio')")

        # Take screenshot
        print("\n7. Taking screenshot...")
        page.screenshot(path="new_sidebar_layout.png", full_page=True)
        print("   Screenshot saved to: new_sidebar_layout.png")

        # Check CSS version
        print("\n8. Checking CSS version:")
        stylesheets = page.query_selector_all('link[rel="stylesheet"]')
        for sheet in stylesheets:
            href = sheet.get_attribute('href')
            if 'styles.css' in href:
                print(f"   CSS: {href}")
                if '?v=4' in href:
                    print("   ✓ CSS version 4 loaded")
                else:
                    print("   ✗ CSS version not 4")

        browser.close()

        print("\n" + "=" * 80)
        print("VERIFICATION COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    verify_layout()
