import logging
from typing import Dict, Any
try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

logger = logging.getLogger("mintuu.tools.browser")

class BrowserTool:
    """Real browser automation using Playwright."""
    
    async def execute(self, action: str, url: str) -> Dict[str, Any]:
        if not async_playwright:
            return {"error": "Playwright not installed. Cannot execute browser automation."}
            
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                if action == "screenshot":
                    await page.goto(url)
                    path = f"./artifacts/screenshot_{url.replace('https://', '').replace('/', '_')}.png"
                    await page.screenshot(path=path)
                    await browser.close()
                    return {"status": "success", "path": path}
                    
                elif action == "extract_text":
                    await page.goto(url)
                    text = await page.evaluate("() => document.body.innerText")
                    await browser.close()
                    return {"status": "success", "text": text[:2000]} # Limit text length
                    
                else:
                    await browser.close()
                    return {"error": f"Unknown action: {action}"}
                    
        except Exception as e:
            logger.error(f"Browser tool error: {e}")
            return {"error": str(e)}
