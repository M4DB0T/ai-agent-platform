import requests


WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"


def search_wikipedia(query: str) -> dict:
    """
    Searches Wikipedia by topic title and returns a short summary context.

    For v1, this uses Wikipedia's page summary endpoint.
    It works best when the query is close to a real Wikipedia page title.
    """

    clean_query = query.strip().replace(" ", "_")

    if not clean_query:
        raise ValueError("Wikipedia query cannot be empty.")

    url = WIKIPEDIA_API_URL.format(title=clean_query)

    headers = {
        "User-Agent": "ai-agent-platform/0.1 (local development project)"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 404:
        return {
            "query": query,
            "title": None,
            "summary": "No Wikipedia page was found for this query.",
            "url": None,
        }

    response.raise_for_status()

    data = response.json()

    return {
        "query": query,
        "title": data.get("title"),
        "summary": data.get("extract"),
        "url": data.get("content_urls", {})
        .get("desktop", {})
        .get("page"),
    }