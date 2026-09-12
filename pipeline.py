"""
The Verity research run, as a generator of progress events.

This is the multi-stage workflow the product is actually about:

    question -> dimensions -> parallel search -> read sources -> classify
             -> plan counter-searches -> search again -> read -> independence -> synthesis

The counterargument stage is the point of the whole thing. A single search returns whatever
the engines rank highest, so Verity looks at what that first pass concluded and then goes
hunting specifically for credible evidence that would qualify or overturn it. What that stage
digs up is what the "what you might be missing" section reports.

Yields ("status", message) throughout and finally ("result", report) or ("error", message),
so the web app can stream real progress and the CLI can consume the identical pipeline.
"""

import time

from analyze import classify_sources, describe_distribution, stance_distribution
from browser import steel_page
from discover import discover_for_queries, discover_sources
from fetch import read_until
from independence import analyze_independence
from plan import decompose, plan_counter_searches
from synthesize import synthesize

INITIAL_READ_LIMIT = 6
COUNTER_READ_LIMIT = 4
MIN_SOURCES = 3
SEARCH_WORKERS = 3
READ_WORKERS = 4


def run_verity(question):
    question = (question or "").strip()
    if not question:
        yield "error", "Ask a question first."
        return

    started = time.time()
    stats = {
        "initial_searches": 0,
        "counter_searches": 0,
        "sources_seen": 0,
        "sources_read": 0,
        "dimensions": 0,
    }

    # ---- stage 1: understand the question -------------------------------------------
    yield "status", "Breaking the question into researchable parts..."
    dimensions = decompose(question)
    stats["dimensions"] = len(dimensions)
    yield "status", f"Investigating {len(dimensions)} dimensions: " + ", ".join(
        d["name"] for d in dimensions if d.get("name")
    )[:120]

    # ---- stage 2: initial search across dimensions ----------------------------------
    yield "status", "Searching multiple engines in parallel..."
    queries = [d["query"] for d in dimensions]
    stats["initial_searches"] = len(queries)

    events = []
    initial = discover_for_queries(
        queries, per_engine=6, workers=SEARCH_WORKERS, on_event=events.append
    )
    for message in events:
        yield "status", message

    if not initial:
        yield "error", "No search engine returned usable results. Try rephrasing the question."
        return

    stats["sources_seen"] += len(initial)
    yield "status", f"Found {len(initial)} distinct sources across engines and queries"

    # ---- stage 3: read the initial sources ------------------------------------------
    yield "status", f"Opening sources to read in full (targeting {INITIAL_READ_LIMIT})..."
    read_events = []
    read = read_until(
        initial, target=INITIAL_READ_LIMIT, workers=READ_WORKERS,
        max_attempts=INITIAL_READ_LIMIT * 3, on_event=read_events.append,
    )
    for message in read_events:
        yield "status", message

    if len(read) < MIN_SOURCES:
        yield "error", (
            f"Only {len(read)} source(s) could be read — not enough to compare evidence. "
            "Many pages block automated readers; try rephrasing the question."
        )
        return

    # ---- stage 4: where does this first pass stand? ---------------------------------
    yield "status", "Identifying what each source claims and what stake it has..."
    first_pass = classify_sources(question, read)
    if first_pass:
        read = first_pass["sources"]
        initial_distribution = first_pass["distribution"]
        preliminary = first_pass["preliminary_conclusion"]
    else:
        initial_distribution = stance_distribution(read)
        preliminary = ""

    lean = describe_distribution(initial_distribution)
    yield "status", f"Initial results lean: {lean}"

    # ---- stage 5: go looking for what's missing -------------------------------------
    yield "status", "Searching specifically for evidence that could change this conclusion..."
    counter_plan = plan_counter_searches(question, preliminary or question, lean)
    counter_queries = counter_plan.get("queries", [])
    stats["counter_searches"] = len(counter_queries)

    counter_read = []
    if counter_queries:
        seen_domains = {s["domain"] for s in read}
        counter_events = []
        counter_candidates = discover_for_queries(
            counter_queries, per_engine=5, workers=SEARCH_WORKERS,
            on_event=counter_events.append,
        )
        for message in counter_events:
            yield "status", message

        fresh = [s for s in counter_candidates if s["domain"] not in seen_domains]
        stats["sources_seen"] += len(counter_candidates)
        yield "status", f"{len(fresh)} sources found that the first search missed entirely"

        if fresh:
            counter_events = []
            counter_read = read_until(
                fresh, target=COUNTER_READ_LIMIT, workers=READ_WORKERS,
                max_attempts=COUNTER_READ_LIMIT * 4, on_event=counter_events.append,
            )
            for message in counter_events:
                yield "status", message
            for s in counter_read:
                s["from_counter_search"] = True
            yield "status", (
                f"Read {len(counter_read)} source(s) the first search had missed"
                if counter_read else
                "Counter-search sources could not be read (most blocked automated readers)"
            )

    all_sources = read + counter_read
    stats["sources_read"] = len(all_sources)

    # ---- stage 6: are these sources independent? ------------------------------------
    yield "status", "Tracing citations to check whether these sources are independent..."
    independence = analyze_independence(all_sources)

    # ---- stage 7: synthesis ----------------------------------------------------------
    yield "status", f"Weighing the evidence across {len(all_sources)} sources..."
    report = synthesize(question, all_sources, distribution_text=lean)
    if not report:
        yield "error", "Synthesis failed. Try again, or rephrase the question."
        return

    # Citations are 1-based indices into all_sources; ship the sources in that exact order
    # so [1] on the page always points at the source the model meant.
    citations = [
        {
            "n": i + 1,
            "domain": s["domain"],
            "url": s["url"],
            "title": s.get("title", ""),
            "type": s.get("type", "Unclear"),
            "primary_or_secondary": s.get("primary_or_secondary", "Unclear"),
            "stance": s.get("stance", "Unclear"),
            "summary": s.get("summary", ""),
            "interest": s.get("interest", ""),
            "published": s.get("published", ""),
            "engines": s.get("engines", []),
            "from_counter_search": bool(s.get("from_counter_search")),
        }
        for i, s in enumerate(all_sources)
    ]

    report.update({
        "question": question,
        "dimensions": dimensions,
        "initial_distribution": initial_distribution,
        "initial_lean_text": lean,
        "counter_gaps": counter_plan.get("gaps", []),
        "counter_queries": counter_queries,
        "independence": independence,
        "sources": citations,
        "stats": {**stats, "seconds": round(time.time() - started)},
    })

    yield "result", report


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) or "are electric vehicles better for the environment"
    print(f"Question: {question!r}\n")

    final = None
    for kind, payload in run_verity(question):
        if kind == "status":
            print(f"  ... {payload}")
        elif kind == "error":
            print(f"\nERROR: {payload}")
        else:
            final = payload

    if final:
        print("\n" + "=" * 72)
        print("ANSWER")
        print("=" * 72)
        print(final["answer"])
        print(f"\n>> {final['verdict_note']}")

        print("\n" + "=" * 72)
        print("EVIDENCE")
        print("=" * 72)
        for c in final["claims"]:
            print(f"\n[{c['strength']}] {c['claim']}")
            print(f"   supporting {c['supporting']}  challenging {c['challenging']}")

        print("\n" + "=" * 72)
        print("WHAT YOU MIGHT BE MISSING")
        print("=" * 72)
        for m in final["missing"]:
            print(f"\n- {m['topic']}")
            print(f"  {m['why_it_matters']}")

        print("\n" + "=" * 72)
        print("SOURCE INDEPENDENCE")
        print("=" * 72)
        print(final["independence"]["summary"] if final["independence"] else "n/a")

        print(f"\nStats: {final['stats']}")
