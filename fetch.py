"""
Reads what each source actually says, and who it points at.

Two jobs here. The obvious one is pulling each page's real text — Verity attributes claims to
specific sources, so it can't work from search snippets, which are written to be clicked
rather than to be accurate.

The second job is collecting each page's outbound links. That's the raw material for source
independence analysis: if eight articles all link to the same government report, they are not
eight independent pieces of evidence, and links are the one checkable trace of that (as
opposed to asking a model to guess at lineage, which would just be invention).

Pages are read in parallel, each in its own Steel browser, because a serial read of a dozen
sources takes minutes and the demo has seconds.
"""

import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from browser import steel_page

MAX_CHARS = 6000
MAX_LINKS = 60
DEFAULT_WORKERS = 4

# Pages that are really just a bot check. Cheaper to detect and skip than to fight, and
# fighting a bot wall is not something Verity should be doing in the first place.
CHALLENGE_MARKERS = (
    "just a moment", "enable javascript and cookies", "checking your browser",
    "verify you are human", "attention required", "ddos protection by",
)

# Domains observed to serve bot walls rather than content more often than not. Not banned,
# just tried last — see prioritize().
HARD_TO_READ_DOMAINS = {
    "sciencedirect.com", "researchgate.net", "academic.oup.com", "doaj.org",
    "jstor.org", "tandfonline.com", "onlinelibrary.wiley.com", "ssrn.com",
    "papers.ssrn.com", "ieeexplore.ieee.org", "dl.acm.org", "cambridge.org",
    "journals.sagepub.com", "iopscience.iop.org", "pubs.acs.org", "bloomberg.com",
    "wsj.com", "ft.com", "economist.com", "nytimes.com", "washingtonpost.com",
}

# Share widgets and tracking, not citations. Counting a Facebook share button as a cited
# source would quietly wreck the independence analysis, which is built on real outbound links.
NOISE_DOMAINS = {
    "scholar.google.com", "google.com", "books.google.com", "translate.google.com",
    "facebook.com", "twitter.com", "x.com", "linkedin.com", "instagram.com",
    "pinterest.com", "api.whatsapp.com", "whatsapp.com", "t.me", "telegram.me",
    "reddit.com", "tumblr.com", "mailto", "doubleclick.net", "googletagmanager.com",
    "google-analytics.com", "addtoany.com", "sharethis.com", "flipboard.com",
    "threads.net", "bsky.app", "mastodon.social",
}

READ_JS = """
() => {
    const drop = 'script, style, nav, header, footer, aside, form, noscript, iframe, ' +
                 '[role="navigation"], [role="banner"], [role="contentinfo"], ' +
                 '.nav, .navbar, .menu, .sidebar, .footer, .header, .cookie, .ad, .ads';
    const clone = document.body.cloneNode(true);
    clone.querySelectorAll(drop).forEach(el => el.remove());

    const main = clone.querySelector('article, main, [role="main"], .post-content, .article-body');
    const host = (main || clone);
    const text = (host.innerText || '').replace(/\\n{3,}/g, '\\n\\n').trim();

    // Outbound links from the body of the page, in document order. Nav/footer chrome was
    // already stripped above, so what's left skews toward links the article actually makes.
    const links = [];
    host.querySelectorAll('a[href]').forEach(a => {
        const href = a.getAttribute('href') || '';
        if (!href.startsWith('http')) return;
        links.push({ href: href, text: (a.innerText || '').trim().slice(0, 120) });
    });

    return {
        title: (document.title || '').trim(),
        text: text,
        links: links,
        published: document.querySelector('meta[property="article:published_time"]')?.content
               || document.querySelector('meta[name="date"]')?.content
               || document.querySelector('time[datetime]')?.getAttribute('datetime')
               || '',
    };
}
"""


def _domain(url):
    try:
        return re.sub(r"^www\.", "", urllib.parse.urlparse(url).netloc.lower())
    except Exception:
        return ""


def _looks_like_challenge(title, text):
    blob = f"{title} {text[:400]}".lower()
    return any(marker in blob for marker in CHALLENGE_MARKERS)


def _clean_links(links, self_domain):
    """Keeps outbound links to other domains, deduped, capped. Self-links are navigation,
    not citation."""
    seen = set()
    out = []
    for link in links:
        url = link.get("href", "").split("#")[0].rstrip("/")
        domain = _domain(url)
        if not domain or domain == self_domain or url in seen:
            continue
        if domain in NOISE_DOMAINS:
            continue
        seen.add(url)
        out.append({"url": url, "domain": domain, "text": link.get("text", "")})
        if len(out) >= MAX_LINKS:
            break
    return out


def read_page(page, source, max_chars=MAX_CHARS):
    """Reads one already-open browser at one source. Returns an enriched source or None."""
    try:
        page.goto(source["url"], timeout=20000, wait_until="domcontentloaded")
        page.wait_for_timeout(700)
        result = page.evaluate(READ_JS)
    except Exception as e:
        return None, f"unreachable ({type(e).__name__})"

    title = result.get("title") or source.get("title") or source["domain"]
    text = (result.get("text") or "").strip()

    if _looks_like_challenge(title, text):
        return None, "blocked by a bot check"
    if len(text) < 400:
        return None, f"too little readable text ({len(text)} chars)"

    return {
        **source,
        "title": title,
        "text": text[:max_chars],
        "text_chars": len(text),
        "published": (result.get("published") or "")[:10],
        "links": _clean_links(result.get("links", []), source["domain"]),
    }, None


def _read_in_own_browser(source):
    """One source, one dedicated Steel browser — safe to run in a worker thread because the
    Playwright context is created and torn down entirely inside it."""
    try:
        with steel_page(source["domain"], quiet=True) as page:
            return read_page(page, source)
    except Exception as e:
        return None, f"browser failed ({type(e).__name__})"


def read_sources_parallel(sources, workers=DEFAULT_WORKERS, on_event=None):
    """Reads many sources concurrently, keeping whatever succeeds. Failures are normal here
    (paywalls, bot walls, timeouts) and never abort the run."""
    notify = on_event or (lambda msg: None)
    if not sources:
        return []

    results = []
    with ThreadPoolExecutor(max_workers=min(workers, len(sources))) as pool:
        for source, (fetched, problem) in zip(
            sources, pool.map(_read_in_own_browser, sources)
        ):
            if fetched:
                results.append(fetched)
                notify(f"Read {source['domain']} ({fetched['text_chars']:,} chars)")
            else:
                notify(f"Skipped {source['domain']} — {problem}")
    return results


def prioritize(sources):
    """Pushes reliably-hostile domains to the back rather than dropping them.

    Publisher portals and academic aggregators serve bot walls far more often than they serve
    articles. They're still worth trying if nothing better is left — but trying them first is
    how a research run ends up with three sources and no counter-evidence."""
    soft = [s for s in sources if s["domain"] in HARD_TO_READ_DOMAINS]
    easy = [s for s in sources if s["domain"] not in HARD_TO_READ_DOMAINS]
    return easy + soft


def read_until(sources, target, workers=DEFAULT_WORKERS, max_attempts=None, on_event=None):
    """Keeps reading candidates in parallel waves until `target` sources are successfully
    read, or the candidate pool runs out.

    Reading exactly `target` candidates and accepting the survivors sounds equivalent but
    isn't: roughly a third of pages block automated readers, so a fixed slice quietly yields
    two usable sources instead of six. Overfetching is what keeps the counterargument stage
    from coming back empty."""
    notify = on_event or (lambda msg: None)
    pool_sources = prioritize(sources)[: (max_attempts or target * 3)]
    if not pool_sources:
        return []

    collected = []
    wave_size = max(workers, 1)
    for start in range(0, len(pool_sources), wave_size):
        if len(collected) >= target:
            break
        wave = pool_sources[start : start + wave_size]
        collected.extend(read_sources_parallel(wave, workers=workers, on_event=notify))

    return collected[:target]


if __name__ == "__main__":
    import sys
    from discover import discover_sources

    query = " ".join(sys.argv[1:]) or "is nuclear energy safe"
    print(f"Query: {query!r}\n")

    with steel_page("discovery", quiet=True) as page:
        sources = discover_sources(page, query, on_event=lambda m: print(f"  {m}"))

    print(f"\nReading {min(len(sources), 6)} sources in parallel...")
    read = read_sources_parallel(sources[:6], on_event=lambda m: print(f"  {m}"))

    print(f"\n{len(read)} sources read.")
    for r in read:
        print(f"\n  {r['domain']}  ({len(r['links'])} outbound links)")
        for link in r["links"][:4]:
            print(f"     -> {link['domain']}")
