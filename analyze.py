"""
First-pass classification, plus the shared LLM plumbing the rest of Verity uses.

This pass is deliberately cheap. Its only jobs are to work out where each source stands and
what stake it has, and to name the conclusion the first round of results is pointing at —
because that conclusion is what the counterargument search then goes hunting for evidence
against. The heavy reasoning happens later, in synthesize.py, once the counter-search sources
are in hand too.

Note on Verity's own bias: it lives here and in synthesize.py. An LLM deciding "this source
leans X" is an unaccountable judgement, so the prompt asks for *disclosed interests* —
observable, checkable facts about who runs a source — rather than a vibes-based political
score, and the UI ships every label with a link so a reader can overrule it.
"""

import json

from openai import OpenAI

from browser import OPENROUTER_API_KEY

# Both default to a cheap model that's known to work on this key. Synthesis is where output
# quality actually shows, so ANALYSIS_MODEL is the first thing to upgrade if results look thin.
FAST_MODEL = "openai/gpt-4o-mini"
ANALYSIS_MODEL = "openai/gpt-4o-mini"

CHARS_PER_SOURCE = 2600

CLASSIFY_PROMPT = """A user asked: "{question}"

Below is the real text of {count} sources a search engine returned for it.

{sources_block}

For each source, work out where it stands on the question and what stake it has in the answer.
Then name the conclusion this set of sources is collectively pointing toward.

Reply with ONLY JSON in this shape:
{{
  "preliminary_conclusion": "one sentence naming what these sources collectively suggest",
  "sources": [
    {{
      "domain": "exact domain as given above",
      "stance": "one of: Supportive, Critical, Mixed, Neutral, Unclear",
      "summary": "one sentence on what this source concludes about the question",
      "type": "one of: Primary research, Academic study, Meta-analysis, Government data, Expert analysis, News report, Opinion, Corporate source, Advocacy organization, Encyclopedia, Blog, Unclear",
      "primary_or_secondary": "Primary or Secondary or Unclear",
      "interest": "what stake this source has in the answer, as a checkable fact about who they are (e.g. 'Trade body funded by nuclear operators'). Write 'No obvious stake' only if there genuinely isn't one."
    }}
  ]
}}

Rules:
- Include every domain listed above exactly once, using the domain spelling given.
- "stance" is the source's position on the QUESTION, not its tone.
- If you label a source Corporate source, Advocacy organization, Government data or Opinion, \
you MUST name a concrete interest — those categories have a stake by definition. "No obvious \
stake" is only valid for research, news, encyclopedia or blog sources.
- Never invent funding or affiliation you cannot support from the text or from well-known \
public fact. Unknown is an acceptable answer."""


def _client():
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)


def _strip_fences(reply):
    text = (reply or "").strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] if "\n" in text else text
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    return text.strip()


def sources_block(sources, chars=CHARS_PER_SOURCE):
    return "\n\n".join(
        f"=== SOURCE {i+1} | domain: {s['domain']} | title: {s.get('title','')[:110]} ===\n"
        f"{s.get('text','')[:chars]}"
        for i, s in enumerate(sources)
    )


def classify_sources(question, sources, client=None):
    """First pass: per-source stance/type/interest plus the conclusion the set points at.

    Returns {preliminary_conclusion, sources: [...], distribution: {...}} or None."""
    if not sources:
        return None

    client = client or _client()
    prompt = CLASSIFY_PROMPT.format(
        question=question, count=len(sources), sources_block=sources_block(sources)
    )

    try:
        response = client.chat.completions.create(
            model=FAST_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        parsed = json.loads(_strip_fences(response.choices[0].message.content))
    except Exception as e:
        print(f"  (classification failed: {e})")
        return None

    verdicts = {v.get("domain"): v for v in parsed.get("sources", []) if isinstance(v, dict)}
    merged = []
    for s in sources:
        v = verdicts.get(s["domain"], {})
        merged.append({
            **s,
            "stance": v.get("stance", "Unclear"),
            "summary": v.get("summary", ""),
            "type": v.get("type", "Unclear"),
            "primary_or_secondary": v.get("primary_or_secondary", "Unclear"),
            "interest": v.get("interest", ""),
        })

    return {
        "preliminary_conclusion": parsed.get("preliminary_conclusion", ""),
        "sources": merged,
        "distribution": stance_distribution(merged),
    }


def stance_distribution(sources):
    """The lean of a result set, as percentages. This is what justifies going looking for
    what's missing: a 90/10 split is a signal the first page of results is narrow."""
    if not sources:
        return {}

    buckets = {"Supportive": 0, "Critical": 0, "Mixed": 0, "Neutral": 0, "Unclear": 0}
    for s in sources:
        buckets[s.get("stance", "Unclear") if s.get("stance") in buckets else "Unclear"] += 1

    total = len(sources)
    return {
        "counts": buckets,
        "percent": {k: round(v * 100 / total) for k, v in buckets.items() if v},
        "total": total,
    }


def describe_distribution(distribution):
    """Human-readable lean, for prompts and for the UI."""
    pct = (distribution or {}).get("percent", {})
    if not pct:
        return "unknown"
    return ", ".join(f"{k.lower()} {v}%" for k, v in sorted(pct.items(), key=lambda kv: -kv[1]))
