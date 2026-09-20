def get_taka_response(question):
    """
    Provide helpful answers to common TakaLink questions.

    This is a rule-based assistant for the hackathon.
    A real AI provider can be connected later.
    """

    question = question.lower().strip()

    if "collection" in question and (
        "request" in question or "schedule" in question
    ):
        return (
            "To request waste collection, go to your Resident Dashboard "
            "and select 'Request Collection'. Choose the waste category, "
            "describe the waste, provide your location, and select a "
            "collection date."
        )

    if "green point" in question or "green points" in question:
        return (
            "You can earn Green Points through successful waste collections, "
            "correctly sorting your waste, recyclable waste, and verified "
            "waste reports. Check your Green Points history to see your progress."
        )

    if "recycl" in question:
        return (
            "Common recyclable materials include paper, cardboard, plastics, "
            "glass, and metals. Try to keep recyclable waste separated from "
            "general waste."
        )

    if "report" in question and (
        "waste" in question or "dump" in question
    ):
        return (
            "You can report a waste problem from your Resident Dashboard. "
            "Provide a description, location, and optionally upload a photo "
            "as evidence."
        )

    if "status" in question or "request" in question:
        return (
            "Your collection request can move through several stages: "
            "Pending, Accepted, and Collected. Check Collection History "
            "for the latest status."
        )

    return (
        "I'm Taka AI. I can help you with waste collection, recycling, "
        "Green Points, waste reporting, and your collection status."
    )