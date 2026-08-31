"""AI engine for intelligent price analysis and item filtering."""
from typing import List, Dict, Optional
from loguru import logger
from openai import OpenAI
import json


class PennyAIEngine:
    """Uses OpenAI to analyze and filter deals intelligently."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_items(self, items: List[Dict], max_price: float = 1.00) -> List[Dict]:
        """Use AI to analyze and rank items by deal quality."""
        if not items:
            return []

        logger.info(f"Analyzing {len(items)} items with AI")
        try:
            prompt = self._build_analysis_prompt(items, max_price)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            result = response.choices[0].message.content
            analyzed_items = self._parse_ai_response(result, items)
            logger.info(f"AI ranked {len(analyzed_items)} items")
            return analyzed_items
        except Exception as e:
            logger.error(f"Error analyzing items with AI: {e}")
            return items

    def identify_penny_items(self, items: List[Dict]) -> List[Dict]:
        """Identify items priced at $0.01 or very close to it."""
        penny_items = [item for item in items if item.get("price", 999) <= 0.01]
        logger.info(f"Found {len(penny_items)} penny items")
        return penny_items

    def find_lowest_prices(self, items: List[Dict], top_n: int = 10) -> List[Dict]:
        """Find the lowest-priced items across all sources."""
        sorted_items = sorted(items, key=lambda x: x.get("price", 999))
        lowest = sorted_items[:top_n]
        logger.info(f"Found {len(lowest)} lowest-priced items")
        return lowest

    def _build_analysis_prompt(self, items: List[Dict], max_price: float) -> str:
        """Build a prompt for AI analysis."""
        items_json = json.dumps(items[:20], indent=2)  # Limit to 20 items to save tokens
        return f"""You are a smart shopping assistant. Analyze these retail items and rate them.

Criteria:
1. Price point (items at $0.01 are PREMIUM)
2. Item quality/usefulness
3. Deal legitimacy (flag suspicious listings)
4. Rarity of low prices for this item

Items to analyze:
{items_json}

Return a JSON array with fields: title, price, deal_score (0-100), reason, is_legitimate (true/false).
Only include items with deal_score > 70.
"""

    def _parse_ai_response(self, response: str, original_items: List[Dict]) -> List[Dict]:
        """Parse AI response and merge with original item data."""
        try:
            # Extract JSON from response
            start = response.find("[")
            end = response.rfind("]")
            if start != -1 and end != -1:
                json_str = response[start:end+1]
                analyzed = json.loads(json_str)
                return analyzed
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
        return original_items
