"""Semantic clustering of markets for correlation risk control."""

from __future__ import annotations

import re

CLUSTER_KEYWORDS: dict[str, frozenset[str]] = {
    "iran":             frozenset({"iran", "iranian", "tehran"}),
    "israel":           frozenset({"israel", "israeli", "gaza", "hamas", "hezbollah", "netanyahu"}),
    "russia-ukraine":   frozenset({"ukraine", "ukrainian", "russia", "russian", "putin", "zelensky", "kyiv", "kremlin"}),
    "china-taiwan":     frozenset({"china", "chinese", "taiwan", "taiwanese", "xi jinping"}),
    "trump":            frozenset({"trump"}),
    "north-korea":      frozenset({"north korea", "kim jong", "pyongyang"}),
    "musk":             frozenset({"musk", "tesla", "spacex"}),
    "venezuela":        frozenset({"venezuela", "maduro"}),
    "syria":            frozenset({"syria", "syrian", "assad"}),
    "middle-east-other":frozenset({"saudi", "yemen", "houthi", "lebanon"}),
}

CLUSTER_LIMIT_OVERRIDES: dict[str, int] = {
    "russia-ukraine": 4,
}


def effective_cluster_limit(cluster: str, default: int) -> int:
    return CLUSTER_LIMIT_OVERRIDES.get(cluster, default)


_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def classify_clusters(question: str, slug: str) -> frozenset[str]:
    """Return the frozenset of cluster names that match the given market.

    Matching rules:
    - Case-insensitive
    - Single-word keywords match as whole tokens (so "trump" does NOT match "stumbling")
    - Multi-word keywords (e.g. "xi jinping") match as substrings in the normalized text
    - A market may belong to zero, one, or multiple clusters
    """
    text = _NON_ALNUM.sub(" ", f"{question} {slug}".lower()).strip()
    tokens = set(text.split())
    result: set[str] = set()
    for cluster, keywords in CLUSTER_KEYWORDS.items():
        for kw in keywords:
            if " " in kw:
                if kw in text:
                    result.add(cluster)
                    break
            elif kw in tokens:
                result.add(cluster)
                break
    return frozenset(result)
