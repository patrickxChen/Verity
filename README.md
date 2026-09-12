# Verity

**Search beyond the obvious.**

Built for Battle of the Schools — Steel.dev web agents track.

Search engines optimise for finding information. AI assistants optimise for producing an
answer. Neither tells you how strong the evidence is, where it actually came from, or what
you're not being shown.

Verity is a research agent that investigates a question instead of answering it. It searches
across multiple engines, reads the sources in full, then deliberately goes looking for the
credible evidence the first page of results left out — and it shows you when a dozen
"independent" articles all trace back to the same document.

Verity does not claim to be unbiased. It claims to make bias visible.

## What it actually does

1. **Decomposes the question** into the dimensions that determine the answer (for EVs: battery
   manufacturing, grid mix, mining, recycling, lifecycle emissions) and searches each one.
2. **Searches multiple engines in parallel** — DuckDuckGo and Bing — so no single engine's
   ranking decides what you see. One source per domain: ten pages from one outlet is one
   perspective, not ten.
3. **Reads every source in full** in its own Steel cloud browser, concurrently. Search
   snippets are written to be clicked, not to be accurate.
4. **Classifies each source** — stance, type, primary vs secondary, and what stake it has in
   the answer, stated as a checkable fact ("trade body funded by nuclear operators").
5. **Searches for what's missing.** Given the conclusion the first pass points at, it plans
   and runs fresh searches aimed at evidence that could qualify or overturn it — then reports
   what it found. This is the point of the whole product.
6. **Checks source independence** by tracing real outbound links. If eight articles all cite
   the same government report, that's one line of evidence, not eight. This step is
   deterministic — computed from links the pages actually published, not inferred by a model.
7. **Synthesises** an answer with inline citations, an evidence map with strength ratings,
   perspectives grouped by position rather than politics, and open uncertainties.

No false balance: if the good evidence lands mostly on one side, Verity says so.

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env` and fill in a [Steel.dev](https://steel.dev) key and an
[OpenRouter](https://openrouter.ai) key.

## Run

```
.venv\Scripts\python.exe app.py
```

Then open <http://localhost:5001>.

Each stage of the run streams to the browser as it happens, so you can watch the agent query
engines, open sources, and go hunting for counter-evidence.

## Run it from the terminal instead

Any stage works standalone, which is handy for debugging:

```
.venv\Scripts\python.exe pipeline.py "are electric vehicles better for the environment"
.venv\Scripts\python.exe discover.py "is nuclear power safe"
.venv\Scripts\python.exe independence.py "is nuclear power safe"
```

## Layout

| File | Job |
| --- | --- |
| `browser.py` | Steel cloud browser sessions |
| `plan.py` | Question decomposition, counter-search planning |
| `discover.py` | Multi-engine, multi-query source discovery |
| `fetch.py` | Parallel full-text reading + outbound link extraction |
| `analyze.py` | First-pass source classification, stance distribution |
| `independence.py` | Source clustering from real citations (no LLM) |
| `synthesize.py` | Final answer, evidence map, perspectives, missing |
| `pipeline.py` | The whole run, as a stream of progress events |
| `app.py` | Flask + server-sent events |

## Known limits

- Roughly a third of pages block automated readers (publisher portals especially). Verity
  overfetches candidates to compensate and tells you what it skipped and why.
- Source labels, stances and evidence ratings are AI judgements and can be wrong. Every source
  links out so you can check the original.
- Independence analysis only sees links a page actually published. Uncredited reuse is
  invisible to it, so it reports what sources "appear to share" rather than asserting lineage.
- A run takes 60-90 seconds because it reads a dozen pages and makes three LLM passes.
