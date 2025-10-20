#!/usr/bin/env python3
"""
Improved Playwright test script with better selectors
"""
import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

async def test_application_improved():
    """Test all buttons with improved selectors"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        # Create screenshots directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshots_dir = f"screenshots_improved_{timestamp}"
        os.makedirs(screenshots_dir, exist_ok=True)
        
        try:
            print("🚀 Navigating to SoraKing application...")
            await page.goto("https://soraking-ad-cloner-7lwcv.ondigitalocean.app/")
            await page.wait_for_load_state('networkidle')
            
            # Take initial screenshot
            await page.screenshot(path=f"{screenshots_dir}/01_initial_page.png")
            print("📸 Initial page screenshot taken")
            
            # Test navigation buttons with better selectors
            print("\n🧪 Testing navigation buttons...")
            
            # Test Analytics button
            try:
                analytics_button = page.locator('text=Analytics').first
                if await analytics_button.count() > 0:
                    await analytics_button.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=f"{screenshots_dir}/02_analytics_clicked.png")
                    print("✅ Analytics button clicked")
                    # Handle any alert
                    page.on('dialog', lambda dialog: dialog.accept())
                else:
                    print("❌ Analytics button not found")
            except Exception as e:
                print(f"❌ Analytics button error: {e}")
            
            # Test Library button
            try:
                library_button = page.locator('text=Library').first
                if await library_button.count() > 0:
                    await library_button.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=f"{screenshots_dir}/03_library_clicked.png")
                    print("✅ Library button clicked")
                else:
                    print("❌ Library button not found")
            except Exception as e:
                print(f"❌ Library button error: {e}")
            
            # Test Settings button
            try:
                settings_button = page.locator('text=Settings').first
                if await settings_button.count() > 0:
                    await settings_button.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=f"{screenshots_dir}/04_settings_page.png")
                    print("✅ Settings button clicked - navigated to settings page")
                    
                    # Go back to main page
                    await page.go_back()
                    await page.wait_for_timeout(2000)
                else:
                    print("❌ Settings button not found")
            except Exception as e:
                print(f"❌ Settings button error: {e}")
            
            # Test A/B Testing button
            try:
                ab_testing_button = page.locator('text=A/B Testing').first
                if await ab_testing_button.count() > 0:
                    await ab_testing_button.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=f"{screenshots_dir}/05_ab_testing_page.png")
                    print("✅ A/B Testing button clicked - navigated to A/B testing page")
                    
                    # Go back to main page
                    await page.go_back()
                    await page.wait_for_timeout(2000)
                else:
                    print("❌ A/B Testing button not found")
            except Exception as e:
                print(f"❌ A/B Testing button error: {e}")
            
            # Test Video Extension button
            try:
                video_extension_button = page.locator('text=Video Extension').first
                if await video_extension_button.count() > 0:
                    await video_extension_button.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=f"{screenshots_dir}/06_video_extension_page.png")
                    print("✅ Video Extension button clicked - navigated to video extension page")
                    
                    # Go back to main page
                    await page.go_back()
                    await page.wait_for_timeout(2000)
                else:
                    print("❌ Video Extension button not found")
            except Exception as e:
                print(f"❌ Video Extension button error: {e}")
            
            # Test input method tabs
            print("\n🧪 Testing input method tabs...")
            
            # Test Video Upload tab
            try:
                video_upload_tab = page.locator('text=Video Upload').first
                if await video_upload_tab.count() > 0:
                    await video_upload_tab.click()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/07_video_upload_tab.png")
                    print("✅ Video Upload tab clicked")
                else:
                    print("❌ Video Upload tab not found")
            except Exception as e:
                print(f"❌ Video Upload tab error: {e}")
            
            # Test Script Only tab
            try:
                script_only_tab = page.locator('text=Script Only').first
                if await script_only_tab.count() > 0:
                    await script_only_tab.click()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/08_script_only_tab.png")
                    print("✅ Script Only tab clicked")
                else:
                    print("❌ Script Only tab not found")
            except Exception as e:
                print(f"❌ Script Only tab error: {e}")
            
            # Test Image Upload tab
            try:
                image_upload_tab = page.locator('text=Image Upload').first
                if await image_upload_tab.count() > 0:
                    await image_upload_tab.click()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/09_image_upload_tab.png")
                    print("✅ Image Upload tab clicked")
                else:
                    print("❌ Image Upload tab not found")
            except Exception as e:
                print(f"❌ Image Upload tab error: {e}")
            
            # Test generation settings
            print("\n🧪 Testing generation settings...")
            
            # Test output dimension dropdown
            try:
                output_dimension = page.locator('select').first
                if await output_dimension.count() > 0:
                    await output_dimension.select_option('1280x720')  # YouTube format
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/10_youtube_dimension_selected.png")
                    print("✅ Output dimension changed to YouTube")
                else:
                    print("❌ Output dimension dropdown not found")
            except Exception as e:
                print(f"❌ Output dimension error: {e}")
            
            # Test Sora model dropdown
            try:
                sora_model = page.locator('select').nth(1)
                if await sora_model.count() > 0:
                    await sora_model.select_option('sora-2-pro')
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/11_sora_2_pro_selected.png")
                    print("✅ Sora model changed to Sora 2 Pro")
                else:
                    print("❌ Sora model dropdown not found")
            except Exception as e:
                print(f"❌ Sora model error: {e}")
            
            # Test aggression slider
            try:
                aggression_slider = page.locator('input[type="range"]').first
                if await aggression_slider.count() > 0:
                    await aggression_slider.fill('3')  # Set to aggressive
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/12_aggression_slider_moved.png")
                    print("✅ Aggression slider moved to aggressive")
                else:
                    print("❌ Aggression slider not found")
            except Exception as e:
                print(f"❌ Aggression slider error: {e}")
            
            # Test main generation button
            try:
                generate_button = page.locator('button:has-text("Generate Scene 1")').first
                if await generate_button.count() > 0:
                    await generate_button.hover()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/13_generate_button_hover.png")
                    print("✅ Generate button is interactive (hovered)")
                else:
                    print("❌ Generate button not found")
            except Exception as e:
                print(f"❌ Generate button error: {e}")
            
            # Test cost optimization display
            try:
                cost_panel = page.locator('.cost-panel').first
                if await cost_panel.count() > 0:
                    await cost_panel.hover()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"{screenshots_dir}/14_cost_panel_hover.png")
                    print("✅ Cost panel is interactive")
                else:
                    print("❌ Cost panel not found")
            except Exception as e:
                print(f"❌ Cost panel error: {e}")
            
            # Final screenshot
            await page.screenshot(path=f"{screenshots_dir}/15_final_state.png")
            print("📸 Final state screenshot taken")
            
            print(f"\n✅ Testing completed! Screenshots saved in: {screenshots_dir}")
            print(f"📁 Total screenshots taken: {len([f for f in os.listdir(screenshots_dir) if f.endswith('.png')])}")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            await page.screenshot(path=f"{screenshots_dir}/error_screenshot.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_application_improved())
