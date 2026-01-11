import asyncio
from typing import List
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from src.models import SchemeDetails

class MySchemeScraper:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,  # Always headless for deployment
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-zygote',
                '--single-process'
            ]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.page = await self.context.new_page()

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def search_schemes(self, query: str) -> List[str]:
        print("🔥 USING UPDATED SCRAPER VERSION 🔥")
        print(f"Searching for: {query}")

        try:
            await self.page.goto("https://www.myscheme.gov.in/", timeout=60000)
            await self.page.wait_for_load_state("domcontentloaded")
            print("Page Loaded:", await self.page.title())

            # STEP 1 — Click fake placeholder
            placeholder = self.page.get_by_text("Enter scheme name to search...").first

            if await placeholder.is_visible():
                print("Placeholder found — clicking...")
                await placeholder.click()
                await asyncio.sleep(1)
            else:
                print("Could NOT find placeholder!")
                return []

            # STEP 2 — Wait for modal search input
            print("Waiting for REAL modal input...")
            await self.page.wait_for_selector("form.w-full", timeout=10000)

            # STEP 3 — Select real modal input
            real_input = await self.page.wait_for_selector("form.w-full input[name='query']", timeout=8000)
            print("Modal input found — focusing...")
            await real_input.click()
            await asyncio.sleep(0.3)

            # STEP 4 — Type with keyboard (React requires this)
            print("Typing query into modal...")
            await self.page.keyboard.type(query, delay=75)
            await asyncio.sleep(1)

            # STEP 5 — Submit with Enter
            print("Submitting search...")
            await self.page.keyboard.press("Enter")
            await asyncio.sleep(4)

            await self.page.wait_for_load_state("networkidle")
            print("Search executed! Page:", self.page.url)

            # STEP 6 — Extract scheme links
            links = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('a')).map(a => a.href)
            """)

            scheme_urls = [link for link in links if "/schemes/" in link]

            print("Found scheme URLs:", scheme_urls[:4])
            return scheme_urls[:4]

        except Exception as e:
            print("Error during search:", e)
            return []

    # ======================================================================


    # List of valid states on myscheme.gov.in
    VALID_STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    ]

    def _get_normalized_state(self, input_state: str) -> str:
        """
        Normalizes input state to match valid state names.
        """
        cleaned_input = input_state.lower().strip()
        
        # 1. Exact match (case-insensitive) logic
        for state in self.VALID_STATES:
            if cleaned_input == state.lower():
                print(f"Exact match found: {state}")
                return state
                
        # 2. Fuzzy/Substring match
        input_parts = set(cleaned_input.split())
        best_match = None
        max_matches = 0
        
        for state in self.VALID_STATES:
            state_lower = state.lower()
            state_parts = set(state_lower.split())
            matches = len(input_parts.intersection(state_parts))
            if matches > max_matches:
                max_matches = matches
                best_match = state
        
        if best_match:
            print(f"Auto-corrected '{input_state}' to '{best_match}'")
            return best_match

        print(f"No match found for '{input_state}', using original.")
        return input_state
    
    

    async def search_with_filters(self, state: str, category: str, age: int) -> List[str]:
     print("🔥 FILTER SEARCH STARTED 🔥")

     try:
        # Open search page directly
        print("Opening filter page directly...")
        await self.page.goto("https://www.myscheme.gov.in/search?query=a", timeout=60000)
        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        # STEP 1 — SCROLL TO LOAD SIDEBAR
        print("Scrolling to load sidebar...")
        await self.page.evaluate("window.scrollBy(0, 600)")
        await asyncio.sleep(2)

        # NOW WAIT FOR SIDEBAR
        sidebar = self.page.locator("div.rounded-md.shadow-sm")
        await sidebar.wait_for(state="visible", timeout=15000)
        print("Sidebar loaded!")

        # STEP 2 — SELECT STATE
        print(f"Selecting state: {state}")

        # Scroll to make sure element is rendered
        await self.page.evaluate("window.scrollBy(0, 300)")
        await asyncio.sleep(1)
        
        # Remove placeholder so input gets click events
        await self.page.evaluate("""
            const ph = document.querySelector('.facet__placeholder');
            if (ph) ph.style.display = 'none';
        """)
        await asyncio.sleep(0.3)
        
        # Force click into React-Select input
        state_input = self.page.locator("input#react-select-7-input")
        await state_input.wait_for(state="visible", timeout=5000)
        await state_input.click(force=True)
        await asyncio.sleep(0.5)
        
        # Type and select state
        await state_input.fill(state)
        await asyncio.sleep(0.5)
        await self.page.keyboard.press("Enter")
        await asyncio.sleep(1)
        
       

        

        # STEP 3 — SELECT CATEGORY
        print("Selecting category:", category)
        
        # Scroll back up to find the category section
        await self.page.evaluate("window.scrollBy(0, -200)")
        await asyncio.sleep(1)
        
        # Use JavaScript to directly click the category span and then the checkbox
        await self.page.evaluate("""
            // Click to expand category section
            const spans = document.querySelectorAll('span.text-base.font-semibold');
            for (let span of spans) {
                if (span.textContent.includes('Scheme Category')) {
                    span.click();
                    break;
                }
            }
            
            // Wait a bit then click the checkbox
            setTimeout(() => {
                const checkbox = document.querySelector("input[aria-labelledby='Education & Learning']");
                if (checkbox) {
                    checkbox.click();
                    console.log('Checkbox clicked');
                } else {
                    console.log('Checkbox not found');
                }
            }, 1000);
        """)
        await asyncio.sleep(3)
        


        # STEP 4 — SELECT AGE
        print(f"Selecting age: {age}")

        # Convert age
        if age <= 5:
            label = "0-5"
        elif age <= 18:
            label = "6-18"
        elif age <= 25:
            label = "19-25"
        elif age <= 40:
            label = "26-40"
        else:
            label = "41-60"

        # Use JavaScript to handle age dropdown
        await self.page.evaluate(f"""
            // Find and click the age dropdown
            const ageDropdowns = document.querySelectorAll('div.facet__control');
            if (ageDropdowns.length > 1) {{
                ageDropdowns[1].click();
                
                // Wait and then fill the input
                setTimeout(() => {{
                    const ageInput = document.querySelector('input#react-select-8-input');
                    if (ageInput) {{
                        ageInput.value = '{label}';
                        ageInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        
                        // Press Enter
                        setTimeout(() => {{
                            ageInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', bubbles: true }}));
                        }}, 500);
                    }}
                }}, 500);
            }}
        """)
        await asyncio.sleep(3)

        # STEP 5 — WAIT FOR RESULTS
        print("Waiting for filtered results...")
        await asyncio.sleep(5)

        schemes = await self.page.evaluate("""
            () => Array.from(document.querySelectorAll('a'))
                        .map(a => a.href)
                        .filter(h => h.includes('/schemes/'))
        """)
        
        print("Total schemes found:", len(schemes))
        return schemes

     except Exception as e:
        print("Filter search error:", e)
        return []


    async def scrape_scheme_details(self, url: str) -> SchemeDetails:
        print(f"Scraping: {url}")
        page = await self.context.new_page()

        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("networkidle")

            title_el = await page.query_selector("h1.font-bold")
            title = await title_el.inner_text() if title_el else await page.title()

            async def extract(id):
                sec = await page.query_selector(f"#{id}")
                if not sec:
                    return None
                block = await sec.query_selector(".markdown-options")
                return await block.inner_text() if block else await sec.inner_text()

            description = await extract("details")
            eligibility = await extract("eligibility")
            benefits = await extract("benefits")
            application_process = await extract("application-process")
            documents_required = await extract("documents-required")

            return SchemeDetails(
                title=title,
                url=url,
                description=description,
                eligibility=eligibility,
                benefits=benefits,
                application_process=application_process,
                documents_required=documents_required
            )

        except Exception as e:
            print("Error scraping:", e)
            return SchemeDetails(title="Error", url=url, description=str(e))

        finally:
            await page.close()
