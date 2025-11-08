import asyncio
from playwright.async_api import async_playwright
import json
import re
from datetime import datetime, timezone
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def scrape_flights(origin_city, destination_city, date="2025-12-12"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=70)
        page = await browser.new_page()

        print("Opening BudgetTicket...")
        await page.goto("https://www.budgetticket.in", timeout=90000)

        print("Waiting for input boxes...")
        await page.wait_for_selector("input[placeholder='Select Origin City']", state="visible")
        await page.wait_for_selector("input[placeholder='Select Destination City']", state="visible")

        # --- Set search parameters ---
        # origin_city = "Bangalore"
        # destination_city = "Delhi"

        print(f"Selecting Origin city: {origin_city}")
        origin = page.locator("input[placeholder='Select Origin City']").nth(0)
        await origin.click()
        await origin.type(origin_city, delay=100)
        await page.wait_for_timeout(1500)
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")

        print(f"Selecting Destination city: {destination_city}")
        dest = page.locator("input[placeholder='Select Destination City']").nth(0)
        await dest.click()
        await dest.type(destination_city, delay=100)
        await page.wait_for_timeout(1500)
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")

        print("Selecting Departure Date...")
        try:
            await page.locator("label.select_city:text('Departure')").click()
            await page.wait_for_timeout(1500)
            await page.locator("td.available").first.click()
        except Exception:
            print("Date picker not interactive — using default date.")

        print("Clicking Search Flights...")
        await page.locator("input[type='submit'][value='Search']").click()

        print("Waiting dynamically for flight results to appear...")
        success = False
        for attempt in range(60):  # wait up to 60 * 2 = 120 seconds
            html = await page.content()
            if "₹" in html or "Air India" in html or "IndiGo" in html:
                success = True
                print(f"✅ Flights detected on attempt {attempt + 1}")
                break
            await page.wait_for_timeout(2000)
        if not success:
            raise TimeoutError("❌ Flights did not appear in time.")

        # --- Extract visible flight rows by visual grouping ---
        print("Extracting visible flight text blocks...")
        flight_divs = await page.locator("div:has-text('₹')").element_handles()
        print(f"Found {len(flight_divs)} potential flight containers.")

        flights = []
        for handle in flight_divs:
            text = (await handle.inner_text()).strip()
            if not text or "₹" not in text:
                continue

            # Extract approximate details using regex and heuristics
            airline_match = re.search(r"(IndiGo|Air\s?India|Vistara|SpiceJet|Akasa|Go\s?First|Alliance\s?Air)", text, re.I)
            flight_no_match = re.search(r"[A-Z]{1,2}-?\d{2,4}", text)
            price_match = re.search(r"₹\s?[\d,]+", text)
            time_match = re.findall(r"\b\d{1,2}:\d{2}\b", text)

            flight = {
                "airline": airline_match.group(0) if airline_match else None,
                "flight_number": flight_no_match.group(0) if flight_no_match else None,
                "departure_time": time_match[0] if len(time_match) > 0 else None,
                "arrival_time": time_match[1] if len(time_match) > 1 else None,
                "price": price_match.group(0) if price_match else None,
                "raw_text": text
            }

            if flight["price"] and flight["airline"]:
                flights.append(flight)

        print(f"✅ Extracted {len(flights)} flights.")

        # 🧩 Add metadata fields
        search_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for f in flights:
            f["searchdatetime"] = search_time
            f["origin"] = origin_city
            f["destination"] = destination_city

        # 💾 Save results
        with open("flight_results_dom_fallback.json", "w", encoding="utf-8") as f:
            json.dump(flights, f, indent=4, ensure_ascii=False)

        print("💾 Saved results to flight_results_dom_fallback.json")

        await page.screenshot(path="flight_results_verified.png", full_page=True)
        print("📸 Screenshot saved as flight_results_verified.png")

        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(scrape_flights())
