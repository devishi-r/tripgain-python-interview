# flight_search_api.py
from fastapi import FastAPI, Query
from flight_search_automation import scrape_flights
import traceback

app = FastAPI()

@app.get("/flight-search")
async def flight_search(
    origin: str = Query(..., description="Origin city"),
    destination: str = Query(..., description="Destination city"),
    journey_date: str = Query(..., description="Date of journey in YYYY-MM-DD format")
):
    """Run Playwright-based flight search and return scraped JSON."""
    try:
        flights = await scrape_flights(origin, destination, journey_date)
        return {
            "total_flights": len(flights),
            "data": flights
        }
    except Exception as e:
        tb = traceback.format_exc()
        print("❌ Exception occurred during scraping:\n", tb)
        return {"error": str(e) or "Unknown error occurred", "traceback": tb}
