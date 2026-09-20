from decimal import Decimal

from .models import WasteCategory


class MockAIProvider:
    """
    A deterministic mock AI provider for TakaLink.

    This simulates AI waste classification using keywords.
    It can later be replaced with a real AI provider without
    changing the rest of the application.
    """

    KEYWORD_RULES = [
        (
            ["phone", "computer", "laptop", "charger", "battery", "electronics"],
            "Electronic Waste",
            Decimal("0.96"),
        ),
        (
            ["plastic", "bottle", "bottles", "container", "nylon"],
            "Plastic",
            Decimal("0.95"),
        ),
        (
            ["food", "banana", "vegetable", "fruit", "peel", "organic"],
            "Organic Waste",
            Decimal("0.96"),
        ),
        (
            ["paper", "cardboard", "carton", "newspaper", "magazine"],
            "Recyclable",
            Decimal("0.94"),
        ),
        (
            ["glass", "metal", "can", "cans", "tin", "recyclable"],
            "Recyclable",
            Decimal("0.93"),
        ),
    ]

    def classify(self, description):
        text = description.lower()

        for keywords, category_name, confidence in self.KEYWORD_RULES:
            if any(keyword in text for keyword in keywords):
                category = WasteCategory.objects.filter(
                    name=category_name
                ).first()

                if category:
                    return category, confidence

        category = WasteCategory.objects.filter(
            name="General Waste"
        ).first()

        return category, Decimal("0.50")


def classify_waste(description):
    """
    Classify waste using the currently configured AI provider.

    For now, TakaLink uses the mock provider.
    """

    provider = MockAIProvider()

    return provider.classify(description)