"""
Research planning: turning one question into a research strategy.

A single search reflects whatever the engines rank highest, which is exactly the failure mode
Verity exists to address. So before searching, the question gets decomposed into the
dimensions that actually determine the answer, and each dimension becomes its own query.

Later in the run, plan_counter_searches() does the other half of the job: given what the
first pass concluded, it writes queries designed to surface credible evidence that would
qualify or overturn that conclusion — not queries for "the opposite opinion", which is how
you end up with false balance instead of better evidence.
"""

import json

from analyze import FAST_MODEL, _client, _strip_fences

DECOMPOSE_PROMPT = """A user asked: "{question}"

You are planning research for Verity, a search engine that investigates questions rather \
than just answering them.

Break the question into the distinct dimensions that actually determine the answer — the \
separate things you'd need to know to answer it honestly. For "are EVs better for the \
environment" those would be things like lifecycle emissions, battery manufacturing, \
electricity grid mix, mining impacts, recycling. Aim for 3 to 5 dimensions, each genuinely \
different from the others.

Then write one web search query per dimension. Queries should read like something a \
researcher would actually type — specific, not a restatement of the question.

Reply with ONLY JSON in this shape:
{{
  "dimensions": [
    {{"name": "short dimension name", "query": "the search query for it"}}
  ]
}}"""

COUNTER_PROMPT = """Verity researched the question: "{question}"

Based on the first pass of sources, the emerging conclusion is:
"{conclusion}"

The sources found so far lean as follows: {distribution}

Your job is to plan searches that could CHANGE OR QUALIFY that conclusion. This is not about \
finding people who disagree for the sake of balance — it is about finding credible evidence, \
studies, expert criticism, limitations or counterexamples that a careful researcher would \
want to see before accepting the conclusion.

Good counter-searches target: methodological criticism, limitations and caveats, \
contradictory studies, contexts where the conclusion fails, costs and risks the dominant \
framing downplays.

Write 4 such search queries, plus a short list of the specific gaps you are trying to fill.

Reply with ONLY JSON in this shape:
{{
  "gaps": ["the specific thing missing from current results", "..."],
  "queries": ["search query", "..."]
}}"""


def decompose(question, client=None):
    """Returns [{name, query}] dimensions, falling back to the raw question if the model
    misbehaves — a degraded plan is better than a dead pipeline."""
    client = client or _client()
    fallback = [{"name": "General", "query": question}]

    try:
        response = client.chat.completions.create(
            model=FAST_MODEL,
            max_tokens=600,
            messages=[{"role": "user", "content": DECOMPOSE_PROMPT.format(question=question)}],
        )
        parsed = json.loads(_strip_fences(response.choices[0].message.content))
    except Exception as e:
        print(f"  (decomposition failed: {e})")
        return fallback

    dimensions = [
        {"name": str(d.get("name", "")).strip(), "query": str(d.get("query", "")).strip()}
        for d in parsed.get("dimensions", [])
        if isinstance(d, dict) and d.get("query")
    ]
    return dimensions[:5] or fallback


def plan_counter_searches(question, conclusion, distribution, client=None):
    """Returns {gaps: [...], queries: [...]} aimed at evidence that could change the answer."""
    client = client or _client()
    try:
        response = client.chat.completions.create(
            model=FAST_MODEL,
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": COUNTER_PROMPT.format(
                    question=question, conclusion=conclusion, distribution=distribution
                ),
            }],
        )
        parsed = json.loads(_strip_fences(response.choices[0].message.content))
    except Exception as e:
        print(f"  (counter-search planning failed: {e})")
        return {"gaps": [], "queries": []}

    return {
        "gaps": [g for g in parsed.get("gaps", []) if isinstance(g, str)][:6],
        "queries": [q for q in parsed.get("queries", []) if isinstance(q, str)][:4],
    }
