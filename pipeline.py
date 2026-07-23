from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
import os


def _friendly_error_message(err: Exception) -> str:
    text = str(err)
    lowered = text.lower()
    if "quota" in lowered or "resource_exhausted" in lowered or "429" in lowered:
        return (
            "Google API quota exceeded (429). Check your quota at aistudio.google.com "
            "or switch to another API key with available credits."
        )
    if "invalid_api_key" in lowered or "api key" in lowered or "api_key_invalid" in lowered:
        return "API key issue detected. Check GOOGLE_API_KEY and TAVILY_API_KEY in your .env file."
    return f"Runtime error: {text}"


def run_research_pipeline(topic: str, progress_callback=None) -> dict:
    """
    Runs the full multi-agent research pipeline.

    Args:
        topic: The research topic string.
        progress_callback: Optional callable(step: int, message: str) for UI progress updates.
                           step values: 1=search, 2=reader, 3=writer, 4=critic, 5=done

    Returns:
        state dict with keys: search_results, scraped_content, report, feedback
    """
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY missing in .env")
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("TAVILY_API_KEY missing in .env")

    def _notify(step: int, message: str):
        print(message)
        if progress_callback:
            progress_callback(step, message)

    state = {}

    # ── Step 1: Search Agent ──────────────────────────────────────────────────
    _notify(1, "\n" + " =" * 50)
    _notify(1, "Step 1 — Search agent is working ...")
    _notify(1, "*=" * 50)

    try:
        search_agent = build_search_agent()
       # Step 1 — fix invoke key and output key
        search_result = search_agent.invoke({
        "input": f"Find recent, reliable and detailed information about: {topic}"  # FIXED: "messages" → "input"
    })
        state["search_results"] = search_result["output"]  # FIXED: ["messages"][-1].content → ["output"]

    except Exception as e:
        raise RuntimeError(f"Search step failed. {_friendly_error_message(e)}") from e

    _notify(1, f"\nSearch results:\n{state['search_results']}")

    # ── Step 2: Reader Agent ──────────────────────────────────────────────────
    _notify(2, "\n" + " =" * 50)
    _notify(2, "Step 2 — Reader agent is scraping top resource ...")
    _notify(2, "*=" * 50)

    try:
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
        "input": (                                                                  # FIXED: "messages" → "input"
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search results:\n{state['search_results'][:800]}"
        )
    })
    except Exception as e:
        raise RuntimeError(f"Reader step failed. {_friendly_error_message(e)}") from e

    # FIX: was 'scrapped_content' (typo) — now consistently 'scraped_content'
    state["scraped_content"] = reader_result["output"]
    _notify(2, f"\nScraped content:\n{state['scraped_content']}")

    # ── Step 3: Writer Chain ──────────────────────────────────────────────────
    _notify(3, "\n" + " =" * 50)
    _notify(3, "Step 3 — Writer chain is drafting the report ...")
    _notify(3, "*=" * 50)

    # FIX: was referencing 'scrapped_content' (typo) — fixed to 'scraped_content'
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    try:
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })
    except Exception as e:
        raise RuntimeError(f"Writer step failed. {_friendly_error_message(e)}") from e

    _notify(3, f"\nFinal Report:\n{state['report']}")

    # ── Step 4: Critic Chain ──────────────────────────────────────────────────
    _notify(4, "\n" + " =" * 50)
    _notify(4, "Step 4 — Critic is reviewing the report ...")
    _notify(4, "*=" * 50)

    try:
        state["feedback"] = critic_chain.invoke({
            "report": state["report"]
        })
    except Exception as e:
        raise RuntimeError(f"Critic step failed. {_friendly_error_message(e)}") from e

    _notify(4, f"\nCritic feedback:\n{state['feedback']}")
    _notify(5, "\n✅ Pipeline complete.")

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    try:
        run_research_pipeline(topic)
    except Exception as e:
        print(f"\n[ERROR] {e}")