"""Unit tests for bot.market_clusters.classify_clusters."""

from __future__ import annotations

import pytest

from bot.market_clusters import classify_clusters, effective_cluster_limit


# ---------------------------------------------------------------------------
# Individual cluster keyword matches
# ---------------------------------------------------------------------------

def test_iran_question_matches_iran_cluster() -> None:
    result = classify_clusters("Will Iran attack Israel?", "will-iran-attack-israel")
    assert "iran" in result


def test_iranian_keyword_matches_iran_cluster() -> None:
    result = classify_clusters("Will the Iranian government collapse?", "iranian-gov-collapse")
    assert "iran" in result


def test_tehran_keyword_matches_iran_cluster() -> None:
    result = classify_clusters("Will Tehran host peace talks?", "tehran-peace-talks")
    assert "iran" in result


def test_israel_keyword_matches_israel_cluster() -> None:
    result = classify_clusters("Will Israel invade Lebanon?", "will-israel-invade-lebanon")
    assert "israel" in result


def test_gaza_keyword_matches_israel_cluster() -> None:
    result = classify_clusters("Will the Gaza ceasefire hold?", "gaza-ceasefire-hold")
    assert "israel" in result


def test_hamas_keyword_matches_israel_cluster() -> None:
    result = classify_clusters("Will Hamas release hostages?", "hamas-release-hostages")
    assert "israel" in result


def test_hezbollah_keyword_matches_israel_cluster() -> None:
    result = classify_clusters("Will Hezbollah fire rockets in 2025?", "hezbollah-rockets-2025")
    assert "israel" in result


def test_netanyahu_keyword_matches_israel_cluster() -> None:
    result = classify_clusters("Will Netanyahu resign?", "netanyahu-resign")
    assert "israel" in result


def test_ukraine_keyword_matches_russia_ukraine_cluster() -> None:
    result = classify_clusters("Will Ukraine retake Kherson?", "ukraine-retake-kherson")
    assert "russia-ukraine" in result


def test_russia_keyword_matches_russia_ukraine_cluster() -> None:
    result = classify_clusters("Will Russia default on debt?", "russia-default-debt")
    assert "russia-ukraine" in result


def test_putin_keyword_matches_russia_ukraine_cluster() -> None:
    result = classify_clusters("Will Putin remain in power?", "putin-remain-power")
    assert "russia-ukraine" in result


def test_zelensky_keyword_matches_russia_ukraine_cluster() -> None:
    result = classify_clusters("Will Zelensky visit Washington?", "zelensky-visit-washington")
    assert "russia-ukraine" in result


def test_kyiv_keyword_matches_russia_ukraine_cluster() -> None:
    result = classify_clusters("Will Kyiv fall?", "will-kyiv-fall")
    assert "russia-ukraine" in result


def test_kremlin_keyword_matches_russia_ukraine_cluster() -> None:
    result = classify_clusters("Will the Kremlin change policy?", "kremlin-policy-change")
    assert "russia-ukraine" in result


def test_china_keyword_matches_china_taiwan_cluster() -> None:
    result = classify_clusters("Will China invade Taiwan?", "china-invade-taiwan")
    assert "china-taiwan" in result


def test_taiwan_keyword_matches_china_taiwan_cluster() -> None:
    result = classify_clusters("Will Taiwan hold elections?", "taiwan-elections")
    assert "china-taiwan" in result


def test_trump_keyword_matches_trump_cluster() -> None:
    result = classify_clusters("Will Trump win the election?", "trump-win-election")
    assert "trump" in result


# ---------------------------------------------------------------------------
# Multi-cluster matching
# ---------------------------------------------------------------------------

def test_iran_and_israel_question_matches_both_clusters() -> None:
    result = classify_clusters("Will Iran attack Israel?", "iran-attack-israel")
    assert "iran" in result
    assert "israel" in result


def test_russia_ukraine_question_matches_single_cluster() -> None:
    result = classify_clusters("Will Russia and Ukraine sign a peace deal?", "russia-ukraine-peace-deal")
    assert "russia-ukraine" in result
    assert len(result) == 1


# ---------------------------------------------------------------------------
# Unclustered markets return empty frozenset
# ---------------------------------------------------------------------------

def test_bitcoin_question_returns_empty_frozenset() -> None:
    result = classify_clusters("Will Bitcoin exceed $100k by end of 2025?", "bitcoin-100k-2025")
    assert result == frozenset()


def test_generic_company_question_returns_empty_frozenset() -> None:
    result = classify_clusters("Will X company go bankrupt by Q2?", "x-company-bankrupt-q2")
    assert result == frozenset()


def test_sports_question_returns_empty_frozenset() -> None:
    result = classify_clusters("Will the Lakers win the NBA championship?", "lakers-nba-championship")
    assert result == frozenset()


# ---------------------------------------------------------------------------
# Case insensitivity
# ---------------------------------------------------------------------------

def test_all_caps_iran_question_matches() -> None:
    result = classify_clusters("WILL IRAN WIN?", "will-iran-win")
    assert "iran" in result


def test_mixed_case_russia_question_matches() -> None:
    result = classify_clusters("Will RUSSIA invade Finland?", "russia-invade-finland")
    assert "russia-ukraine" in result


def test_mixed_case_trump_question_matches() -> None:
    result = classify_clusters("Trump wins again", "trump-wins-again")
    assert "trump" in result


# ---------------------------------------------------------------------------
# Word-boundary correctness (no false positives)
# ---------------------------------------------------------------------------

def test_trump_does_not_match_trumpet() -> None:
    result = classify_clusters("Will the trumpet player win?", "trumpet-player-win")
    assert "trump" not in result


def test_trump_does_not_match_stumbling() -> None:
    result = classify_clusters("Is the economy stumbling?", "economy-stumbling")
    assert "trump" not in result


def test_russia_does_not_match_prussian() -> None:
    result = classify_clusters("Will the Prussian guard reform?", "prussian-guard-reform")
    assert "russia-ukraine" not in result


def test_iran_does_not_match_irana() -> None:
    # "irana" is not a token equal to "iran"
    result = classify_clusters("The Irana river overflowed", "irana-river")
    assert "iran" not in result


def test_china_does_not_match_china_town_as_single_word() -> None:
    # "chinatown" normalizes to one token, not "china"
    result = classify_clusters("Will Chinatown be renovated?", "chinatown-renovation")
    assert "china-taiwan" not in result


# ---------------------------------------------------------------------------
# Multi-word keyword matching (xi jinping)
# ---------------------------------------------------------------------------

def test_xi_jinping_multi_word_matches_china_taiwan_cluster() -> None:
    result = classify_clusters("Will Xi Jinping visit Taiwan?", "xi-jinping-visit-taiwan")
    assert "china-taiwan" in result


def test_xi_jinping_in_slug_matches_china_taiwan_cluster() -> None:
    result = classify_clusters("Will the leader visit?", "xi-jinping-visit-2025")
    assert "china-taiwan" in result


# ---------------------------------------------------------------------------
# Slug-based matching
# ---------------------------------------------------------------------------

def test_slug_only_iran_matches_when_question_is_generic() -> None:
    result = classify_clusters("Will this happen?", "iran-strike-may")
    assert "iran" in result


def test_slug_only_ukraine_matches_when_question_is_generic() -> None:
    result = classify_clusters("Will this happen?", "ukraine-ceasefire-2025")
    assert "russia-ukraine" in result


# ---------------------------------------------------------------------------
# Hyphens and punctuation in slug are normalized correctly
# ---------------------------------------------------------------------------

def test_hyphenated_slug_iran_normalized_to_token() -> None:
    result = classify_clusters("Generic question", "will-iran-do-something-2025")
    assert "iran" in result


def test_slug_with_numbers_does_not_break_matching() -> None:
    result = classify_clusters("Generic question", "trump-2024-election")
    assert "trump" in result


def test_slug_with_dots_normalized_correctly() -> None:
    # dots should be treated as separators
    result = classify_clusters("Generic question", "russia.ceasefire.2025")
    assert "russia-ukraine" in result


# ---------------------------------------------------------------------------
# Return type is always frozenset
# ---------------------------------------------------------------------------

def test_return_type_is_frozenset_for_match() -> None:
    result = classify_clusters("Will Iran attack?", "iran-attack")
    assert isinstance(result, frozenset)


def test_return_type_is_frozenset_for_no_match() -> None:
    result = classify_clusters("Will Bitcoin hit 200k?", "bitcoin-200k")
    assert isinstance(result, frozenset)


# ---------------------------------------------------------------------------
# Extended clusters: north-korea, musk, venezuela, syria, middle-east-other
# ---------------------------------------------------------------------------

def test_north_korea_multi_word_match() -> None:
    result = classify_clusters("Will North Korea test a missile?", "north-korea-missile")
    assert "north-korea" in result


def test_kim_jong_multi_word_match() -> None:
    result = classify_clusters("Will Kim Jong Un visit China?", "kim-jong-un-visit-china")
    assert "north-korea" in result
    assert "china-taiwan" in result


def test_pyongyang_keyword_match() -> None:
    result = classify_clusters("Will Pyongyang host talks?", "pyongyang-talks")
    assert "north-korea" in result


def test_musk_keyword_matches_musk_cluster() -> None:
    result = classify_clusters("Will Musk tweet before noon?", "musk-tweet")
    assert "musk" in result


def test_tesla_keyword_matches_musk_cluster() -> None:
    result = classify_clusters("Will Tesla ship 2M cars in 2025?", "tesla-2m-cars-2025")
    assert "musk" in result


def test_spacex_keyword_matches_musk_cluster() -> None:
    result = classify_clusters("Will SpaceX launch Starship?", "spacex-starship-launch")
    assert "musk" in result


def test_venezuela_keyword_match() -> None:
    result = classify_clusters("Will Venezuela hold fair elections?", "venezuela-fair-elections")
    assert "venezuela" in result


def test_maduro_keyword_match() -> None:
    result = classify_clusters("Will Maduro leave power?", "maduro-leave-power")
    assert "venezuela" in result


def test_syria_keyword_match() -> None:
    result = classify_clusters("Will Syria reunify?", "syria-reunify")
    assert "syria" in result


def test_assad_keyword_match() -> None:
    result = classify_clusters("Will Assad return to power?", "assad-return-power")
    assert "syria" in result


def test_saudi_keyword_matches_middle_east_other() -> None:
    result = classify_clusters("Will Saudi Arabia normalize with Israel?", "saudi-normalize-israel")
    assert "middle-east-other" in result
    assert "israel" in result


def test_yemen_keyword_matches_middle_east_other() -> None:
    result = classify_clusters("Will Yemen ceasefire hold?", "yemen-ceasefire")
    assert "middle-east-other" in result


def test_houthi_keyword_matches_middle_east_other() -> None:
    result = classify_clusters("Will Houthi attacks stop?", "houthi-attacks-stop")
    assert "middle-east-other" in result


def test_lebanon_keyword_matches_middle_east_other() -> None:
    result = classify_clusters("Will Lebanon elect a president?", "lebanon-elect-president")
    assert "middle-east-other" in result


# ---------------------------------------------------------------------------
# Per-cluster limit overrides
# ---------------------------------------------------------------------------

def test_russia_ukraine_override_limit_is_four() -> None:
    assert effective_cluster_limit("russia-ukraine", 2) == 4


def test_iran_uses_default_limit() -> None:
    assert effective_cluster_limit("iran", 2) == 2


def test_unknown_cluster_uses_default_limit() -> None:
    assert effective_cluster_limit("nonexistent-cluster", 3) == 3
