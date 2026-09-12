"""
Final synthesis: the answer, the evidence map, the perspectives, and what you're missing.

This runs once, over every source Verity read — both the initial results and the ones found
by the counterargument search — and it's where the product's editorial rules are enforced:

  * Citations are indices into the real source list. The prompt is told the numbers and told
    not to use any others, because a fabricated citation is worse than no citation.
  * No false balance. If the good evidence lands mostly on one side, say so. A 90/10 split
    presented as 50/50 is its own kind of dishonesty, and the spec is explicit about it.
  * Uncertainty is a first-class output, not a hedge bolted on at the end.
  * "Missing perspectives" draws on the counter-search sources, so it reports things Verity
    actually went and found rather than things it imagines might exist.
"""

import json

from analyze import ANALYSIS_MODEL, _client, _strip_fences

CHARS_PER_SOURCE = 3200

SYNTHESIS_PROMPT = """You are the synthesis engine for Verity, a research tool that shows \
people the evidence behind an answer instead of just handing them the answer.

QUESTION: "{question}"

Verity read {count} sources. Sources marked [COUNTER-SEARCH] were found by deliberately \
searching for evidence that could qualify or overturn the initial conclusion — they matter \
for the "missing" section.

The initial results leaned: {distribution}

{sources_block}

Produce the final research report. Reply with ONLY JSON in this shape:

{{
  "answer": "2-3 paragraphs answering the question directly, in plain prose. Put citation markers like [1] or [2][5] after factual claims, using the SOURCE numbers above. Lead with what the evidence actually supports rather than hedging.",
  "verdict_note": "One sentence on how evenly the evidence is actually divided — e.g. 'The evidence strongly favours X, though real uncertainty remains about Y.' Do NOT manufacture a 50/50 split if the evidence is lopsided.",
  "claims": [
    {{
      "claim": "a specific, checkable assertion central to the question",
      "strength": "one of: Strong, Moderate, Limited, Conflicting, Insufficient",
      "strength_reason": "one short sentence on why it got that rating",
      "supporting": [1, 2],
      "challenging": [4],
      "caveats": ["an important limitation, if any"]
    }}
  ],
  "perspectives": [
    {{
      "name": "a group defined by their actual position or field, e.g. 'Grid operators' or 'Public-health researchers' — NOT a political label unless the source self-identifies that way",
      "argument": "their main argument in one or two sentences",
      "evidence": "what they base it on",
      "caveat": "the main weakness or conflict of interest in their position, if any",
      "sources": [1, 3]
    }}
  ],
  "missing": [
    {{
      "topic": "something relevant that the initial results underplayed or omitted",
      "why_it_matters": "why a careful person would want to know this",
      "evidence": "what Verity actually found about it",
      "sources": [7]
    }}
  ],
  "uncertainties": ["a genuine open question the evidence does not settle"],
  "why": {{
    "supports": ["a concrete reason to trust the conclusion, e.g. '3 independent primary sources agree'"],
    "cautions": ["a concrete reason for caution, e.g. '2 of the supportive sources are industry-funded'"]
  }}
}}

Hard rules:
- Citation numbers must be source numbers from the list above. Never cite a number not listed.
- Never attribute a claim to a source that did not make it. Never invent studies, statistics, \
quotes or funding details. If the sources don't establish something, leave it out or put it in \
"uncertainties".
- Give 3 to 5 claims, 2 to 4 perspectives, and 2 to 4 missing items.
- "strength" must reflect the evidence actually present: Strong needs several good independent \
sources agreeing; Conflicting is the right answer when solid sources genuinely disagree; \
Insufficient is the right answer when Verity simply didn't find enough.
- Prefer primary research and official data over news write-ups when they conflict."""


def synthesize(question, sources, distribution_text="unknown", client=None):
    """Returns the full report dict, with citation indices resolved against `sources`."""
    if not sources:
        return None

    client = client or _client()

    block = "\n\n".join(
        f"=== SOURCE {i+1}"
        f"{' [COUNTER-SEARCH]' if s.get('from_counter_search') else ''}"
        f" | domain: {s['domain']}"
        f" | type: {s.get('type', 'Unclear')}"
        f" | stance: {s.get('stance', 'Unclear')}"
        f" | title: {s.get('title', '')[:110]} ===\n"
        f"{s.get('text', '')[:CHARS_PER_SOURCE]}"
        for i, s in enumerate(sources)
    )

    prompt = SYNTHESIS_PROMPT.format(
        question=question,
        count=len(sources),
        distribution=distribution_text,
        sources_block=block,
    )

    try:
        response = client.chat.completions.create(
            model=ANALYSIS_MODEL,
            max_tokens=3500,
            messages=[{"role": "user", "content": prompt}],
        )
        parsed = json.loads(_strip_fences(response.choices[0].message.content))
    except json.JSONDecodeError as e:
        print(f"  (synthesis returned unparseable JSON: {e})")
        return None
    except Exception as e:
        print(f"  (synthesis failed: {e})")
        return None

    valid = set(range(1, len(sources) + 1))

    def clean_refs(refs):
        """Drops any citation the model invented. A wrong citation is worse than none."""
        if not isinstance(refs, list):
            return []
        return [n for n in refs if isinstance(n, int) and n in valid]

    claims = []
    for c in parsed.get("claims", []):
        if not isinstance(c, dict) or not c.get("claim"):
            continue
        claims.append({
            "claim": c.get("claim", ""),
            "strength": c.get("strength", "Insufficient"),
            "strength_reason": c.get("strength_reason", ""),
            "supporting": clean_refs(c.get("supporting")),
            "challenging": clean_refs(c.get("challenging")),
            "caveats": [x for x in c.get("caveats", []) if isinstance(x, str)],
        })

    perspectives = []
    for p in parsed.get("perspectives", []):
        if not isinstance(p, dict) or not p.get("name"):
            continue
        perspectives.append({
            "name": p.get("name", ""),
            "argument": p.get("argument", ""),
            "evidence": p.get("evidence", ""),
            "caveat": p.get("caveat", ""),
            "sources": clean_refs(p.get("sources")),
        })

    missing = []
    for m in parsed.get("missing", []):
        if not isinstance(m, dict) or not m.get("topic"):
            continue
        missing.append({
            "topic": m.get("topic", ""),
            "why_it_matters": m.get("why_it_matters", ""),
            "evidence": m.get("evidence", ""),
            "sources": clean_refs(m.get("sources")),
        })

    why = parsed.get("why", {}) if isinstance(parsed.get("why"), dict) else {}

    return {
        "answer": parsed.get("answer", ""),
        "verdict_note": parsed.get("verdict_note", ""),
        "claims": claims,
        "perspectives": perspectives,
        "missing": missing,
        "uncertainties": [u for u in parsed.get("uncertainties", []) if isinstance(u, str)],
        "why": {
            "supports": [s for s in why.get("supports", []) if isinstance(s, str)],
            "cautions": [c for c in why.get("cautions", []) if isinstance(c, str)],
        },
    }
