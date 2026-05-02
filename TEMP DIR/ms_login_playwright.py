import asyncio
import urllib.parse
import random
from playwright.async_api import async_playwright

class MSALoginPlaywright:
    def __init__(self):
        self.login_url = "https://login.live.com/oauth20_authorize.srf?client_id=000000004C12AE29&response_type=token&scope=service::user.auth.xboxlive.com::ABI&redirect_uri=https://login.live.com/oauth20_desktop.srf&display=touch&locale=en"

    async def login(self, email, password):
        async with async_playwright() as p:
            # Use a stealthy context
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 720},
                device_scale_factor=1,
            )
            
            # Stealth: Hide WebDriver
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page = await context.new_page()
            
            try:
                # Go to login page
                await page.goto(self.login_url, wait_until="networkidle")
                await asyncio.sleep(random.uniform(1.5, 3.0))
                
                # Check for "removed" page or other errors
                if "removed=true" in page.url:
                    return False, "Caught by bot detection"

                # Enter email
                await page.type('input[name="loginfmt"]', email, delay=random.randint(50, 150))
                await asyncio.sleep(random.uniform(0.5, 1.2))
                await page.click('input[type="submit"]') # Next button
                
                # Wait for password field
                await page.wait_for_selector('input[name="passwd"]', timeout=15000)
                await asyncio.sleep(random.uniform(1.0, 2.5))
                
                # Enter password
                await page.type('input[name="passwd"]', password, delay=random.randint(50, 150))
                await asyncio.sleep(random.uniform(0.5, 1.2))
                
                # Submit
                await page.click('input[type="submit"]')
                
                # Wait for redirect or 2FA
                try:
                    await page.wait_for_url(lambda url: "access_token=" in url or "identity/confirm" in url or "Abuse" in url or "removed=true" in url, timeout=45000)
                except:
                    return False, "Timed out waiting for redirect"

                final_url = page.url
                
                if "removed=true" in final_url:
                    return False, "Caught by bot detection (redirected)"
                
                if "access_token=" in final_url:
                    fragment = urllib.parse.urlparse(final_url).fragment
                    params = urllib.parse.parse_qs(fragment)
                    token = params.get('access_token', [None])[0]
                    return True, token
                
                if "identity/confirm" in final_url:
                    return False, "2FA required"
                    
                if "Abuse" in final_url:
                    return False, "Security Challenge / Abuse detected"
                
                return False, f"Unexpected redirect: {final_url}"

            except Exception as e:
                return False, f"Playwright Error: {str(e)}"
            finally:
                await browser.close()

async def test():
    bot = MSALoginPlaywright()
    success, result = await bot.login("test@outlook.com", "pass")
    print(f"Success: {success}, Result: {result}")

if __name__ == "__main__":
    asyncio.run(test())
