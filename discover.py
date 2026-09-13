"""
Source discovery across multiple search engines.

Verity deliberately does not trust a single engine's ranking. If it only asked Google, it
would inherit Google's idea of which sources matter; instead it asks several engines and
unions the results, tracking which engines surfaced each source. That overlap is itself a
signal worth showing: a source only one engine ranked is a different thing from one they
all agree on.
"""

import base64
import re
import time
import urllib.parse

ENGINES = {
    "DuckDuckGo": "https://html.duckduckgo.com/html/?q={q}",
    "Bing": "https://www.bing.com/search?q={q}",
}

# Aggregators, social sites and search-engine plumbing — not primary sources on a question.
SKIP_DOMAINS = {
    "duckduckgo.com", "bing.com", "google.com", "youtube.com", "facebook.com",
    "twitter.com", "x.com", "reddit.com", "pinterest.com", "instagram.com",
    "tiktok.com", "linkedin.com", "microsofttranslator.com",
}

EXTRACT_JS = """
() => {
    const out = [];
    // DuckDuckGo HTML layout
    document.querySelectorAll('.result').forEach(r => {
        const a = r.querySelector('.result__a');
        if (!a) return;
        out.push({
            title: (a.innerText || '').trim(),
            href: a.getAttribute('href') || '',
            snippet: (r.querySelector('.result__snippet')?.innerText || '').trim(),
        });
    });
    // Bing layout
    document.querySelectorAll('li.b_algo').forEach(r => {
        const a = r.querySelector('h2 a');
        if (!a) return;
        out.push({
            title: (a.innerText || '').trim(),
            href: a.getAttribute('href') || '',
            snippet: (r.querySelector('.b_caption p, .b_algoSlug')?.innerText || '').trim(),
        });
    });
    return out;
}
"""


def unwrap_url(href):
    """Search engines wrap result links in their own click-tracking redirects. DuckDuckGo
    hides the real URL in a `uddg` query param; Bing base64-encodes it into `u`. Neither
    redirect is worth following at request time, so decode them up front."""
    if not href:
        return None

    if href.startswith("//"):
        href = "https:" + href

    parsed = urllib.parse.urlparse(href)
    params = urllib.parse.parse_qs(parsed.query)

    if "uddg" in params:  # DuckDuckGo
        return params["uddg"][0]

    if "u" in params:  # Bing — value looks like "a1<base64url>"
        raw = params["u"][0]
        if raw.startswith("a1"):
            raw = raw[2:]
        padded = raw + "=" * (-len(raw) % 4)
        try:
            return base64.urlsafe_b64decode(padded).decode("utf-8", "replace")
        except Exception:
            return None

    return href if href.startswith("http") else None


def domain_of(url):
    netloc = urllib.parse.urlparse(url).netloc.lower()
    return re.sub(r"^www\.", "", netloc)


def discover_sources(page, query, per_engine=10, on_event=None):
    """Returns deduped candidate sources, each annotated with which engines surfaced it."""
    by_url = {}
    notify = on_event or (lambda msg: None)

    for engine, url_template in ENGINES.items():
        target = url_template.format(q=urllib.parse.quote_plus(query))
        notify(f"Querying {engine}...")
        try:
            page.goto(target, timeout=25000, wait_until="domcontentloaded")
            page.wait_for_timeout(1200)
            raw_results = page.evaluate(EXTRACT_JS)
        except Exception as e:
            print(f"  ({engine} failed: {e})")
            notify(f"{engine} did not respond — continuing with other engines")
            continue

        kept = 0
        for r in raw_results:
            if kept >= per_engine:
                break
            url = unwrap_url(r["href"])
            if not url:
                continue
            domain = domain_of(url)
            if not domain or domain in SKIP_DOMAINS:
                continue

            existing = by_url.get(url)
            if existing:
                if engine not in existing["engines"]:
                    existing["engines"].append(engine)
                continue

            by_url[url] = {
                "title": r["title"] or domain,
                "url": url,
                "domain": domain,
                "snippet": r["snippet"],
                "engines": [engine],
            }
            kept += 1

        print(f"  {engine}: {kept} usable results")
        notify(f"{engine} returned {kept} usable results")
        time.sleep(1)

    # One source per domain — ten pages from the same outlet is one perspective, not ten.
    by_domain = {}
    for source in by_url.values():
        current = by_domain.get(source["domain"])
        if current is None or len(source["engines"]) > len(current["engines"]):
            by_domain[source["domain"]] = source

    sources = sorted(by_domain.values(), key=lambda s: -len(s["engines"]))
    return sources


def _discover_one_query(args):
    """Runs a single query in its own browser. Safe in a worker thread because the whole
    Playwright context is created and destroyed inside steel_page."""
    from browser import steel_page

    query, per_engine = args
    try:
        with steel_page(f"search:{query[:20]}", quiet=True) as page:
            return query, discover_sources(page, query, per_engine=per_engine)
    except Exception as e:
        print(f"  (search for {query!r} failed: {e})")
        return query, []


def discover_for_queries(queries, per_engine=6, workers=3, on_event=None):
    """Searches several queries at once, each in its own browser, and merges the results.

    Every source keeps a record of which queries and engines surfaced it — useful signal,
    since a source that only one narrow query found is a different kind of result from one
    every query returns."""
    from concurrent.futures import ThreadPoolExecutor

    notify = on_event or (lambda msg: None)
    queries = [q for q in queries if q and q.strip()]
    if not queries:
        return []

    merged = {}
    with ThreadPoolExecutor(max_workers=min(workers, len(queries))) as pool:
        for query, sources in pool.map(
            _discover_one_query, [(q, per_engine) for q in queries]
        ):
            notify(f'"{query[:52]}" → {len(sources)} sources')
            for s in sources:
                existing = merged.get(s["domain"])
                if existing:
                    for engine in s["engines"]:
                        if engine not in existing["engines"]:
                            existing["engines"].append(engine)
                    if query not in existing["queries"]:
                        existing["queries"].append(query)
                else:
                    merged[s["domain"]] = {**s, "queries": [query]}

    # Sources multiple queries agree on come first — they're most likely central to the topic.
    return sorted(
        merged.values(), key=lambda s: (-len(s["queries"]), -len(s["engines"]))
    )


if __name__ == "__main__":
    import sys
    from browser import steel_page

    query = " ".join(sys.argv[1:]) or "is nuclear energy safe"
    print(f"Discovering sources for: {query!r}\n")
    with steel_page("discovery") as page:
        found = discover_sources(page, query)

    print(f"\n{len(found)} unique sources (one per domain):\n")
    for s in found:
        print(f"  [{'+'.join(s['engines'])}] {s['domain']}")
        print(f"      {s['title'][:80]}")
