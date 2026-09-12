"""
Source independence: is this twenty pieces of evidence, or one piece of evidence repeated
twenty times?

Everything in this module is computed from real outbound links that were actually present on
the pages Verity read. Nothing here is inferred by a language model, which is deliberate: the
whole claim being made — "these sources are not independent" — is only worth anything if it's
checkable. Every cluster below can be verified by clicking the links it cites.

Because links are evidence of a relationship but not proof of lineage, the language stays
hedged: sources "appear to share" an upstream, rather than Verity asserting who copied whom.
"""

MIN_CLUSTER = 2

# Resolvers and repositories where a shared *domain* means nothing (two different DOIs are
# two different papers) but a shared *URL* is strong evidence of a common upstream. These are
# therefore allowed to form document clusters but never outlet clusters.
RESOLVER_DOMAINS = {
    "doi.org", "dx.doi.org", "arxiv.org", "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov",
    "jstor.org", "ssrn.com", "papers.ssrn.com", "researchgate.net", "semanticscholar.org",
    "sciencedirect.com", "springer.com", "link.springer.com", "nature.com", "mdpi.com",
    "wikipedia.org", "en.wikipedia.org", "youtube.com", "amazon.com",
}


def _domain_of_url(url):
    import re
    import urllib.parse
    try:
        return re.sub(r"^www\.", "", urllib.parse.urlparse(url).netloc.lower())
    except Exception:
        return ""


def _citation_index(sources):
    """target -> set of source domains citing it, at both URL and domain granularity."""
    by_url = {}
    by_domain = {}
    for s in sources:
        for link in s.get("links", []):
            by_url.setdefault(link["url"], set()).add(s["domain"])
            by_domain.setdefault(link["domain"], set()).add(s["domain"])
    return by_url, by_domain


def analyze_independence(sources):
    """Groups sources that visibly lean on the same upstream material.

    Returns a structure the UI can render directly, including a headline count of distinct
    evidence clusters versus the raw source count."""
    if not sources:
        return None

    source_domains = {s["domain"] for s in sources}
    by_url, by_domain = _citation_index(sources)

    # Candidate upstreams: anything two or more of our sources point at. Specific URLs are
    # stronger evidence of a shared origin than a bare domain, so they rank first.
    candidates = []
    for url, citers in by_url.items():
        if len(citers) >= MIN_CLUSTER:
            candidates.append({"kind": "document", "label": url, "citers": citers, "weight": len(citers) * 2})
    for domain, citers in by_domain.items():
        if len(citers) >= MIN_CLUSTER and domain not in RESOLVER_DOMAINS:
            candidates.append({"kind": "outlet", "label": domain, "citers": citers, "weight": len(citers)})

    candidates.sort(key=lambda c: (-c["weight"], -len(c["citers"])))

    # Greedy assignment so each source appears in exactly one cluster — a source can cite
    # several shared upstreams, but the display needs a single clear home for it.
    assigned = {}
    clusters = []
    cluster_roots = set()
    for cand in candidates:
        members = sorted(d for d in cand["citers"] if d not in assigned)
        if len(members) < MIN_CLUSTER:
            continue

        if cand["kind"] == "document":
            shared_urls = [cand["label"]]
        else:
            shared_urls = sorted(
                url for url in by_url
                if _domain_of_url(url) == cand["label"]
            )[:4]

        for m in members:
            assigned[m] = cand["label"]

        # Sometimes the shared upstream is a source Verity read directly — then the cluster
        # has a real root rather than an unseen document, which is worth saying plainly.
        root_is_read_source = cand["kind"] == "outlet" and cand["label"] in source_domains
        if root_is_read_source:
            cluster_roots.add(cand["label"])

        clusters.append({
            "upstream": cand["label"],
            "upstream_kind": cand["kind"],
            "upstream_was_read": root_is_read_source,
            "members": members,
            "size": len(members),
            "shared_urls": shared_urls,
        })

    # A source that is itself the root of a cluster isn't "unclustered" — it's the origin of
    # one, and listing it as independent alongside its own dependents reads as a bug.
    unclustered = sorted(
        d for d in source_domains if d not in assigned and d not in cluster_roots
    )

    # Direct derivation: one source we read links straight at another source we read.
    derivations = []
    for s in sources:
        for link in s.get("links", []):
            if link["domain"] in source_domains and link["domain"] != s["domain"]:
                pair = {"from": s["domain"], "to": link["domain"]}
                if pair not in derivations:
                    derivations.append(pair)

    # Each cluster collapses to roughly one independent line of evidence; anything with no
    # detected shared upstream counts as its own.
    distinct = len(clusters) + len(unclustered)

    return {
        "total_sources": len(sources),
        "distinct_clusters": distinct,
        "clusters": clusters,
        "independent": unclustered,
        "derivations": derivations,
        "summary": _summarize(len(sources), distinct, clusters),
    }


def _summarize(total, distinct, clusters):
    if not clusters:
        return (
            f"No shared upstream sources were detected among these {total} sources. On the "
            "evidence of their outbound links, they appear to be independent of one another — "
            "though Verity can only see links a page actually published."
        )

    biggest = max(clusters, key=lambda c: c["size"])
    return (
        f"{total} sources were read, but they appear to represent roughly {distinct} distinct "
        f"lines of evidence. The largest overlap: {biggest['size']} sources all point at "
        f"{biggest['upstream']}. Counting those as separate confirmations would overstate how "
        "much independent evidence actually exists."
    )


if __name__ == "__main__":
    import sys
    from browser import steel_page
    from discover import discover_sources
    from fetch import read_sources_parallel

    query = " ".join(sys.argv[1:]) or "is nuclear energy safe"
    with steel_page("discovery", quiet=True) as page:
        sources = discover_sources(page, query)
    read = read_sources_parallel(sources[:8], on_event=lambda m: print(f"  {m}"))

    result = analyze_independence(read)
    print(f"\n{result['summary']}\n")
    for c in result["clusters"]:
        print(f"  Cluster — shared {c['upstream_kind']}: {c['upstream']}")
        for m in c["members"]:
            print(f"     - {m}")
    if result["independent"]:
        print(f"\n  No shared upstream detected: {', '.join(result['independent'])}")
    if result["derivations"]:
        print("\n  Direct links between sources read:")
        for d in result["derivations"]:
            print(f"     {d['from']} -> {d['to']}")
