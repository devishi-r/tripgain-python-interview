# tripgain_gemini_analysis.py
# ------------------------------------------------------------
# Gemini 2.5 Flash Integration for Intelligent Summarization
# ------------------------------------------------------------
# This script:
# 1. Loads Gemini API key from .env
# 2. Fetches live webpage data automatically.
# 3. Cleans HTML (removes scripts, navs, ads, etc.).
# 4. Sends cleaned content to Gemini 2.5 Flash with a custom prompt.
# 5. Prints and saves the structured summary + insight.
# ------------------------------------------------------------

import os
import requests
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv

# ---------- STEP 1: LOAD API KEY ----------
load_dotenv()  # Loads environment variables from .env
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key = api_key)

# ---------- STEP 2: CONFIGURATION ----------
URL = "https://en.wikipedia.org/wiki/Artificial_intelligence"  # You can change this
OUTPUT_FILE = "summary_output.txt"

# ---------- STEP 3: FETCH WEBPAGE ----------
# ---------- STEP 3: FETCH WEBPAGE ----------
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

response = requests.get(URL, headers=headers, timeout=10)
response.raise_for_status()

# ---------- STEP 4: CLEAN HTML ----------
soup = BeautifulSoup(response.text, "html.parser")

# Remove unnecessary tags
for tag in soup(["script", "style", "header", "footer", "nav", "aside", "noscript", "form"]):
    tag.decompose()

# Extract readable text
text = soup.get_text(separator=" ", strip=True)
cleaned_text = " ".join(text.split())

# Truncate if too long (Gemini Flash supports ~15k-20k characters comfortably)
cleaned_text = cleaned_text[:15000]

# ---------- STEP 5: CREATE PROMPT ----------
prompt = f"""
You are an analytical AI journalist specializing in technology trends.
Analyze the following webpage content about Artificial Intelligence and
produce a structured summary and one interpretive insight.

Instructions:
1. Summarize in exactly 3–5 concise bullet points focusing on technological, ethical, or societal aspects.
2. Each bullet point should represent a distinct idea.
3. End with one single-line insight interpreting what the overall theme suggests about AI’s direction.

Format the response strictly as:
Summary:
• <point 1>
• <point 2>
• <point 3>
• <point 4>
• <point 5>
Insight:
<one-line insight>

Content to analyze:
{cleaned_text}
"""

# ---------- STEP 6: CALL GEMINI 2.5 FLASH ----------
response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
result = response.text.strip()

# ---------- STEP 7: DISPLAY + SAVE ----------
print(result)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(result)

print(f"\n✅ Summary and insight saved to {OUTPUT_FILE}")
