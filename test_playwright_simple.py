#!/usr/bin/env python3
"""
Simple Playwright test script that won't hang
"""
import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

async def test_application_simple():
    """Simple test that takes screenshots of key elements"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        # Create screenshots directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshots_dir = f"screenshots_simple_{timestamp}"
        os.makedirs(screenshots_dir, exist_ok=True)
        
        try:
            print("🚀 Navigating to SoraKing application...")
            await page.goto("https://soraking-ad-cloner-7lwcv.ondigitalocean.app/", timeout=30000)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Take full page screenshot
            await page.screenshot(path=f"{screenshots_dir}/01_full_page.png", full_page=True)
            print("📸 Full page screenshot taken")
            
            # Test navigation buttons
            print("\n🧪 Testing navigation buttons...")
            
            # Test Settings button
            try:
                settings_link = page.locator('a[href="/settings.html"]')
                if await settings_link.count() > 0:
                    await settings_link.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=f"{screenshots_dir}/02_settings_page.png")
                    print("✅ Settings button clicked")
                    
                    # Go back
                    await page.go_back()
                    await page.wait_for_timeout(2000)
                else:
                    print("❌ Settings button not found")
            except Exception as e:
                print(f"❌ Settings error: {e}")
            
            # Test A/B Testing button
            try:
                ab_link = page.locator('a[href="/ab-testing.html"]')
                if await ab_link.count() > 0:
                    await ab_link.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=f"{screenshots_dir}/03_ab_testing_page.png")
                    print("✅ A/B Testing button clicked")
                    
                    # Go back
                    await page.go_back()
                    await page.wait_for_timeout(2000)
                else:
                    print("❌ A/B Testing button not found")
            except Exception as e:
                print(f"❌ A/B Testing error: {e}")
            
            # Test Video Extension button
            try:
                video_link = page.locator('a[href="/video-extension.html"]')
                if await video_link.count() > 0:
                    await video_link.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=f"{screenshots_dir}/04_video_extension_page.png")
                    print("✅ Video Extension button clicked")
                    
                    # Go back
                    await page.go_back()
                    await page.wait_for_timeout(2000)
                else:
                    print("❌ Video Extension button not found")
            except Exception as e:
                print(f"❌ Video Extension error: {e}")
            
            # Test input method tabs
            print("\n🧪 Testing input method tabs...")
            
            # Test Video Upload tab
            try:
                video_upload_tab = page.locator('button[data-method="video-upload"]')
                if await video_upload_tab.count() > 0:
                    await video_upload_tab.click()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/05_video_upload_tab.png")
                    print("✅ Video Upload tab clicked")
                else:
                    print("❌ Video Upload tab not found")
            except Exception as e:
                print(f"❌ Video Upload tab error: {e}")
            
            # Test Script Only tab
            try:
                script_tab = page.locator('button[data-method="script-only"]')
                if await script_tab.count() > 0:
                    await script_tab.click()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/06_script_only_tab.png")
                    print("✅ Script Only tab clicked")
                else:
                    print("❌ Script Only tab not found")
            except Exception as e:
                print(f"❌ Script Only tab error: {e}")
            
            # Test Image Upload tab
            try:
                image_tab = page.locator('button[data-method="image-upload"]')
                if await image_tab.count() > 0:
                    await image_tab.click()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/07_image_upload_tab.png")
                    print("✅ Image Upload tab clicked")
                else:
                    print("❌ Image Upload tab not found")
            except Exception as e:
                print(f"❌ Image Upload tab error: {e}")
            
            # Test generation settings
            print("\n🧪 Testing generation settings...")
            
            # Test output dimension dropdown
            try:
                output_dim = page.locator('select[id="output-dimension"]')
                if await output_dim.count() > 0:
                    await output_dim.select_option('1280x720')
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/08_output_dimension.png")
                    print("✅ Output dimension changed")
                else:
                    print("❌ Output dimension not found")
            except Exception as e:
                print(f"❌ Output dimension error: {e}")
            
            # Test Sora model dropdown
            try:
                sora_model = page.locator('select[id="sora-model"]')
                if await sora_model.count() > 0:
                    await sora_model.select_option('sora-2-pro')
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/09_sora_model.png")
                    print("✅ Sora model changed")
                else:
                    print("❌ Sora model not found")
            except Exception as e:
                print(f"❌ Sora model error: {e}")
            
            # Test aggression slider
            try:
                slider = page.locator('input[id="aggression-slider"]')
                if await slider.count() > 0:
                    await slider.fill('3')
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/10_aggression_slider.png")
                    print("✅ Aggression slider moved")
                else:
                    print("❌ Aggression slider not found")
            except Exception as e:
                print(f"❌ Aggression slider error: {e}")
            
            # Test main generation button
            try:
                generate_btn = page.locator('button[id="start-btn"]')
                if await generate_btn.count() > 0:
                    await generate_btn.hover()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/11_generate_button.png")
                    print("✅ Generate button hovered")
                else:
                    print("❌ Generate button not found")
            except Exception as e:
                print(f"❌ Generate button error: {e}")
            
            # Final screenshot
            await page.screenshot(path=f"{screenshots_dir}/12_final.png", full_page=True)
            print("📸 Final screenshot taken")
            
            print(f"\n✅ Testing completed! Screenshots saved in: {screenshots_dir}")
            print(f"📁 Total screenshots taken: {len([f for f in os.listdir(screenshots_dir) if f.endswith('.png')])}")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            await page.screenshot(path=f"{screenshots_dir}/error.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_application_simple())
