#!/usr/bin/env python3
"""Deep verification - check actual HTML/CSS content being served"""

from playwright.sync_api import sync_playwright
import time

def deep_verify():
    with sync_playwright() as p:
        # Launch with no cache
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            bypass_csp=True,
            ignore_https_errors=True
        )
        page = context.new_page()

        print("=" * 80)
        print("DEEP VERIFICATION - CHECKING ACTUAL SERVED CONTENT")
        print("=" * 80)

        url = "https://soraking-ad-cloner-7lwcv.ondigitalocean.app/"

        # Clear cache by using cache: 'reload'
        print(f"\n1. Loading page with cache bypass: {url}")
        page.goto(url, wait_until="networkidle")

        # Force reload
        print("   Forcing hard reload...")
        page.reload(wait_until="networkidle")

        # Get actual HTML content
        print("\n2. Checking actual HTML structure:")
        html_content = page.content()

        # Check for sidebar in HTML
        has_sidebar = '<aside class="sidebar">' in html_content
        has_old_header = '<div class="header">' in html_content
        has_main_content = '<main class="main-content">' in html_content
        has_old_container = '<div class="container">' in html_content

        print(f"   Has <aside class='sidebar'>: {has_sidebar}")
        print(f"   Has <main class='main-content'>: {has_main_content}")
        print(f"   Has old <div class='header'>: {has_old_header}")
        print(f"   Has old <div class='container'>: {has_old_container}")

        if has_sidebar and has_main_content:
            print("   ✓ NEW layout HTML structure detected")
        elif has_old_header or has_old_container:
            print("   ✗ OLD layout HTML structure detected!")
        else:
            print("   ? Unknown HTML structure")

        # Check title in HTML
        print("\n3. Checking page title in HTML:")
        if '<title>Ad Cloner Studio</title>' in html_content:
            print("   ✓ Title is 'Ad Cloner Studio' (NEW)")
        elif '<title>Ad Cloner Platform</title>' in html_content:
            print("   ✗ Title is 'Ad Cloner Platform' (OLD)")
        else:
            title_start = html_content.find('<title>')
            title_end = html_content.find('</title>')
            if title_start != -1:
                actual_title = html_content[title_start+7:title_end]
                print(f"   ? Title is: {actual_title}")

        # Check CSS link
        print("\n4. Checking CSS link in HTML:")
        if 'styles.css?v=4' in html_content:
            print("   ✓ CSS version 4 linked (NEW)")
        elif 'styles.css?v=3' in html_content:
            print("   ✗ CSS version 3 linked (OLD)")
        elif 'styles.css?v=2' in html_content:
            print("   ✗ CSS version 2 linked (OLD)")
        else:
            print("   ? CSS version unclear")

        # Get actual CSS content
        print("\n5. Checking actual CSS content:")
        css_url = url.rstrip('/') + '/styles.css?v=4&bypass=' + str(int(time.time()))
        css_response = page.goto(css_url)

        if css_response.ok:
            css_text = page.evaluate("() => document.body.innerText")
            print(f"   CSS file size: {len(css_text)} characters")

            # Check for key new layout markers
            has_sidebar_css = '.sidebar {' in css_text or '.sidebar{' in css_text
            has_sidebar_width = '--sidebar-width: 240px' in css_text or '--sidebar-width:240px' in css_text
            has_main_content_css = '.main-content {' in css_text or '.main-content{' in css_text
            has_old_container_css = '.container {' in css_text or '.container{' in css_text

            print(f"   Has .sidebar CSS: {has_sidebar_css}")
            print(f"   Has --sidebar-width: {has_sidebar_width}")
            print(f"   Has .main-content CSS: {has_main_content_css}")
            print(f"   Has old .container CSS: {has_old_container_css}")

            if has_sidebar_css and has_sidebar_width:
                print("   ✓ NEW sidebar layout CSS detected")
            else:
                print("   ✗ NEW sidebar layout CSS NOT found")
        else:
            print(f"   ✗ Failed to load CSS: {css_response.status}")

        # Go back to main page
        page.goto(url + '?bypass=' + str(int(time.time())), wait_until="networkidle")

        # Check computed styles with fresh load
        print("\n6. Checking computed styles (after cache bypass):")

        sidebar_exists = page.query_selector('.sidebar')
        print(f"   Sidebar element exists: {sidebar_exists is not None}")

        if sidebar_exists:
            sidebar_computed = page.evaluate("""
                () => {
                    const sidebar = document.querySelector('.sidebar');
                    const styles = window.getComputedStyle(sidebar);
                    return {
                        display: styles.display,
                        position: styles.position,
                        width: styles.width,
                        left: styles.left
                    };
                }
            """)
            print(f"   Sidebar computed styles: {sidebar_computed}")

        main_exists = page.query_selector('.main-content')
        print(f"   Main content element exists: {main_exists is not None}")

        old_header_exists = page.query_selector('.header')
        print(f"   Old .header element exists: {old_header_exists is not None}")

        # Take screenshot with timestamp
        print("\n7. Taking fresh screenshot...")
        screenshot_name = f"verify_{int(time.time())}.png"
        page.screenshot(path=screenshot_name, full_page=True)
        print(f"   Screenshot saved to: {screenshot_name}")

        # Get the raw HTML and save it
        print("\n8. Saving raw HTML...")
        with open('deployed_raw.html', 'w') as f:
            f.write(html_content)
        print("   Raw HTML saved to: deployed_raw.html")

        # Extract first 500 chars of body
        print("\n9. First 500 characters of HTML body:")
        body_start = html_content.find('<body')
        if body_start != -1:
            body_snippet = html_content[body_start:body_start+500]
            print(f"   {body_snippet}...")

        browser.close()

        print("\n" + "=" * 80)
        print("DEEP VERIFICATION COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    deep_verify()
