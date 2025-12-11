"""
CMS Data Agents - Fetch real vendor data using Playwright + LLM extraction
No LangChain - pure Python with our llm_providers abstraction
"""

import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from llm_providers import get_provider, LLMProvider


@dataclass
class VendorData:
    """Structured vendor data extracted by agents"""
    platform: str
    capabilities: Dict[str, int]
    pricing_info: str
    features: List[str]
    source_urls: List[str]
    raw_content: str


class CMSDataAgent:
    """
    Lightweight agent that scrapes vendor sites and extracts structured data.
    Uses Playwright for JS rendering, Ollama for extraction.
    """
    
    # Known vendor documentation URLs
    VENDOR_DOCS = {
        "contentful": [
            "https://www.contentful.com/features/",
            "https://www.contentful.com/pricing/",
        ],
        "sanity": [
            "https://www.sanity.io/features",
            "https://www.sanity.io/pricing",
        ],
        "hubspot": [
            "https://www.hubspot.com/products/cms",
            "https://www.hubspot.com/pricing/cms",
        ],
        "sitecore": [
            "https://www.sitecore.com/products/content-hub",
        ],
        "acquia": [
            "https://www.acquia.com/products/drupal-cloud",
        ],
    }
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.llm = provider or get_provider("ollama")
        self._browser = None
        self._playwright = None
    
    async def _get_browser(self):
        """Lazy init Playwright browser"""
        if self._browser is None:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
        return self._browser
    
    async def close(self):
        """Cleanup browser resources"""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
    
    async def scrape_page(self, url: str, wait_for: str = "body") -> str:
        """
        Scrape a single page using Playwright.
        Handles JS-rendered content.
        """
        browser = await self._get_browser()
        page = await browser.new_page()
        
        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_selector(wait_for, timeout=10000)
            
            # Remove non-content elements
            await page.evaluate("""
                document.querySelectorAll('script, style, nav, header, footer, aside, iframe')
                    .forEach(el => el.remove());
            """)
            
            # Get clean text content
            content = await page.evaluate("document.body.innerText")
            return content[:15000]  # Limit for LLM context
            
        except Exception as e:
            return f"Error scraping {url}: {e}"
        finally:
            await page.close()
    
    async def scrape_vendor(self, platform: str) -> str:
        """Scrape all known docs for a vendor"""
        urls = self.VENDOR_DOCS.get(platform.lower(), [])
        if not urls:
            return f"No known documentation URLs for {platform}"
        
        all_content = []
        for url in urls:
            content = await self.scrape_page(url)
            all_content.append(f"=== Source: {url} ===\n{content}")
        
        return "\n\n".join(all_content)
    
    def extract_capabilities(self, platform: str, raw_content: str) -> Dict:
        """
        Use LLM to extract structured capabilities from raw docs.
        """
        schema = {
            "type": "object",
            "properties": {
                "capabilities": {
                    "type": "object",
                    "properties": {
                        "content_modeling": {"type": "integer"},
                        "delivery": {"type": "integer"},
                        "personalization": {"type": "integer"},
                        "workflow": {"type": "integer"},
                        "integrations": {"type": "integer"},
                        "performance": {"type": "integer"},
                        "operational": {"type": "integer"}
                    }
                },
                "pricing_tier": {"type": "string"},
                "key_features": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "strengths": {
                    "type": "array", 
                    "items": {"type": "string"}
                },
                "weaknesses": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["capabilities", "key_features"]
        }
        
        prompt = f"""
Analyze this CMS vendor documentation for {platform}.

Score each capability from 0-3:
- 0: Not available
- 1: Basic/limited
- 2: Good, industry standard
- 3: Excellent, best-in-class

Capabilities to score:
- content_modeling: Schema flexibility, relationships, versioning
- delivery: API quality, headless support, CDN, performance
- personalization: A/B testing, segmentation, real-time targeting
- workflow: Approval flows, RBAC, audit logging
- integrations: CRM, analytics, martech ecosystem
- performance: Page speed, caching, optimization
- operational: Vendor stability, docs quality, support

DOCUMENTATION:
{raw_content[:12000]}

Extract structured data as JSON.
"""
        
        response = self.llm.chat(prompt, schema)
        return response.content
    
    async def fetch_platform_data(self, platform: str) -> VendorData:
        """
        Full pipeline: scrape → extract → return structured VendorData
        """
        # 1. Scrape vendor docs
        raw_content = await self.scrape_vendor(platform)
        
        # 2. Extract structured data via LLM
        extracted = self.extract_capabilities(platform, raw_content)
        
        # 3. Package into VendorData
        return VendorData(
            platform=platform,
            capabilities=extracted.get("capabilities", {}),
            pricing_info=extracted.get("pricing_tier", "Unknown"),
            features=extracted.get("key_features", []),
            source_urls=self.VENDOR_DOCS.get(platform.lower(), []),
            raw_content=raw_content[:5000]
        )
    
    async def fetch_all_platforms(self, platforms: List[str]) -> Dict[str, VendorData]:
        """Fetch data for multiple platforms concurrently"""
        results = {}
        for platform in platforms:
            try:
                data = await self.fetch_platform_data(platform)
                results[platform] = data
            except Exception as e:
                print(f"Error fetching {platform}: {e}")
        
        await self.close()
        return results


# Convenience function for sync usage
def fetch_vendor_data(platform: str) -> VendorData:
    """Sync wrapper for fetching vendor data"""
    agent = CMSDataAgent()
    return asyncio.run(agent.fetch_platform_data(platform))


# CLI for testing
if __name__ == "__main__":
    import sys
    
    platform = sys.argv[1] if len(sys.argv) > 1 else "contentful"
    print(f"Fetching data for {platform}...")
    
    data = fetch_vendor_data(platform)
    print(f"\nCapabilities: {json.dumps(data.capabilities, indent=2)}")
    print(f"Features: {data.features[:5]}")
