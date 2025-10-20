#!/usr/bin/env python3
"""
Comprehensive Playwright test script that inspects the DOM and tests all elements
"""
import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

async def test_application_comprehensive():
    """Comprehensive test with DOM inspection"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        # Create screenshots directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshots_dir = f"screenshots_comprehensive_{timestamp}"
        os.makedirs(screenshots_dir, exist_ok=True)
        
        try:
            print("🚀 Navigating to SoraKing application...")
            await page.goto("https://soraking-ad-cloner-7lwcv.ondigitalocean.app/")
            await page.wait_for_load_state('networkidle')
            
            # Take full page screenshot
            await page.screenshot(path=f"{screenshots_dir}/01_full_page.png", full_page=True)
            print("📸 Full page screenshot taken")
            
            # Inspect the DOM structure
            print("\n🔍 Inspecting DOM structure...")
            
            # Get all navigation items
            nav_items = await page.locator('.nav-item').all()
            print(f"Found {len(nav_items)} navigation items")
            
            for i, item in enumerate(nav_items):
                try:
                    text = await item.text_content()
                    href = await item.get_attribute('href')
                    onclick = await item.get_attribute('onclick')
                    print(f"  {i+1}. {text} (href: {href}, onclick: {onclick})")
                except:
                    print(f"  {i+1}. Could not get details")
            
            # Get all buttons
            buttons = await page.locator('button').all()
            print(f"\nFound {len(buttons)} buttons")
            
            for i, button in enumerate(buttons):
                try:
                    text = await button.text_content()
                    button_id = await button.get_attribute('id')
                    onclick = await button.get_attribute('onclick')
                    print(f"  {i+1}. {text} (id: {button_id}, onclick: {onclick})")
                except:
                    print(f"  {i+1}. Could not get details")
            
            # Get all select elements
            selects = await page.locator('select').all()
            print(f"\nFound {len(selects)} select elements")
            
            for i, select in enumerate(selects):
                try:
                    select_id = await select.get_attribute('id')
                    print(f"  {i+1}. Select (id: {select_id})")
                except:
                    print(f"  {i+1}. Could not get details")
            
            # Get all input elements
            inputs = await page.locator('input').all()
            print(f"\nFound {len(inputs)} input elements")
            
            for i, input_elem in enumerate(inputs):
                try:
                    input_type = await input_elem.get_attribute('type')
                    input_id = await input_elem.get_attribute('id')
                    print(f"  {i+1}. Input (type: {input_type}, id: {input_id})")
                except:
                    print(f"  {i+1}. Could not get details")
            
            # Test navigation buttons one by one
            print("\n🧪 Testing navigation buttons individually...")
            
            # Test each navigation item
            for i, item in enumerate(nav_items):
                try:
                    text = await item.text_content()
                    print(f"\nTesting: {text}")
                    
                    # Click the item
                    await item.click()
                    await page.wait_for_timeout(2000)
                    
                    # Take screenshot
                    await page.screenshot(path=f"{screenshots_dir}/nav_{i+1:02d}_{text.replace(' ', '_').replace('/', '_')}.png")
                    print(f"✅ {text} clicked - screenshot taken")
                    
                    # If it's an external link, go back
                    href = await item.get_attribute('href')
                    if href and href.startswith('/'):
                        await page.go_back()
                        await page.wait_for_timeout(2000)
                        print(f"  ↳ Navigated back from {text}")
                    
                except Exception as e:
                    print(f"❌ Error testing {text}: {e}")
            
            # Test all buttons
            print("\n🧪 Testing all buttons...")
            
            for i, button in enumerate(buttons):
                try:
                    text = await button.text_content()
                    button_id = await button.get_attribute('id')
                    print(f"\nTesting button: {text} (id: {button_id})")
                    
                    # Hover over button
                    await button.hover()
                    await page.wait_for_timeout(1000)
                    
                    # Take screenshot
                    await page.screenshot(path=f"{screenshots_dir}/button_{i+1:02d}_{text.replace(' ', '_')}.png")
                    print(f"✅ {text} button hovered - screenshot taken")
                    
                except Exception as e:
                    print(f"❌ Error testing button {text}: {e}")
            
            # Test all select elements
            print("\n🧪 Testing all select elements...")
            
            for i, select in enumerate(selects):
                try:
                    select_id = await select.get_attribute('id')
                    print(f"\nTesting select: {select_id}")
                    
                    # Get options
                    options = await select.locator('option').all()
                    print(f"  Found {len(options)} options")
                    
                    # Try to select different options
                    if len(options) > 1:
                        await select.select_option(index=1)
                        await page.wait_for_timeout(1000)
                        await page.screenshot(path=f"{screenshots_dir}/select_{i+1:02d}_{select_id}_changed.png")
                        print(f"✅ {select_id} select changed - screenshot taken")
                    
                except Exception as e:
                    print(f"❌ Error testing select {select_id}: {e}")
            
            # Test all input elements
            print("\n🧪 Testing all input elements...")
            
            for i, input_elem in enumerate(inputs):
                try:
                    input_type = await input_elem.get_attribute('type')
                    input_id = await input_elem.get_attribute('id')
                    print(f"\nTesting input: {input_id} (type: {input_type})")
                    
                    if input_type == 'range':
                        # Test slider
                        await input_elem.fill('3')
                        await page.wait_for_timeout(1000)
                        await page.screenshot(path=f"{screenshots_dir}/input_{i+1:02d}_{input_id}_slider.png")
                        print(f"✅ {input_id} slider moved - screenshot taken")
                    elif input_type == 'text' or input_type == 'url':
                        # Test text input
                        await input_elem.fill('test input')
                        await page.wait_for_timeout(1000)
                        await page.screenshot(path=f"{screenshots_dir}/input_{i+1:02d}_{input_id}_text.png")
                        print(f"✅ {input_id} text input filled - screenshot taken")
                    else:
                        # Just hover
                        await input_elem.hover()
                        await page.wait_for_timeout(1000)
                        await page.screenshot(path=f"{screenshots_dir}/input_{i+1:02d}_{input_id}_hover.png")
                        print(f"✅ {input_id} input hovered - screenshot taken")
                    
                except Exception as e:
                    print(f"❌ Error testing input {input_id}: {e}")
            
            # Final comprehensive screenshot
            await page.screenshot(path=f"{screenshots_dir}/99_final_comprehensive.png", full_page=True)
            print("📸 Final comprehensive screenshot taken")
            
            print(f"\n✅ Comprehensive testing completed! Screenshots saved in: {screenshots_dir}")
            print(f"📁 Total screenshots taken: {len([f for f in os.listdir(screenshots_dir) if f.endswith('.png')])}")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            await page.screenshot(path=f"{screenshots_dir}/error_screenshot.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_application_comprehensive())
