#!/usr/bin/env python3
"""Generate fixed manual annotation samples from MINDsmall_train/news.tsv.

This script intentionally uses a fixed configuration for the project's real workflow.
Run: python3 scripts/generate_manual_annotation_samples.py
"""

from __future__ import annotations

import csv
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

# Fixed project configuration
SOURCE = Path("data/MINDsmall_train/news.tsv")
OUTPUT_DIR = Path("annotations/manual")
PILOT_SIZE = 10
MAIN_SIZE = 40
VALIDATION_SIZE = 10
MIN_CATEGORY_COUNT = 20
SEED = 42

FIELDNAMES = [
    "news_id",
    "category",
    "subcategory",
    "title",
    "abstract",
    "classification",
    "justification",
    "confidence",
    "notes",
]


@dataclass(frozen=True)
class NewsItem:
    news_id: str
    category: str
    subcategory: str
    title: str
    abstract: str


@dataclass(frozen=True)
class LoadStats:
    total_rows: int
    malformed_rows: int
    missing_required_rows: int
    eligible_rows: int


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def load_items(path: Path) -> tuple[List[NewsItem], LoadStats]:
    items: List[NewsItem] = []
    total_rows = 0
    malformed_rows = 0
    missing_required_rows = 0

    with path.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            total_rows += 1
            if len(row) < 8:
                malformed_rows += 1
                continue

            news_id, category, subcategory, title, abstract = row[:5]
            news_id = news_id.strip()
            category = category.strip()
            subcategory = subcategory.strip()
            title = title.strip()
            abstract = abstract.strip()

            if not (news_id and category and subcategory and title and abstract):
                missing_required_rows += 1
                continue

            items.append(
                NewsItem(
                    news_id=news_id,
                    category=category,
                    subcategory=subcategory,
                    title=title,
                    abstract=abstract,
                )
            )

    stats = LoadStats(
        total_rows=total_rows,
        malformed_rows=malformed_rows,
        missing_required_rows=missing_required_rows,
        eligible_rows=len(items),
    )
    return items, stats


def deduplicate_items(items: Iterable[NewsItem]) -> List[NewsItem]:
    seen = set()
    result = []
    for item in items:
        key = normalize_text(item.title) + " || " + normalize_text(item.abstract)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def allocate_quota(counts: Dict[str, int], sample_size: int) -> Dict[str, int]:
    if sample_size <= 0 or not counts:
        return {k: 0 for k in counts}

    keys = sorted(counts)
    quotas = {k: 0 for k in keys}
    eligible = [k for k in keys if counts[k] > 0]

    if sample_size <= len(eligible):
        eligible_sorted = sorted(eligible, key=lambda k: counts[k], reverse=True)
        for k in eligible_sorted[:sample_size]:
            quotas[k] = 1
        return quotas

    for k in eligible:
        quotas[k] = 1
    remaining = sample_size - len(eligible)

    total = sum(counts.values())
    fractional = []
    for k in eligible:
        exact = remaining * (counts[k] / total)
        base = int(exact)
        quotas[k] += base
        fractional.append((exact - base, k))

    still = sample_size - sum(quotas.values())
    for _, k in sorted(fractional, reverse=True):
        if still <= 0:
            break
        quotas[k] += 1
        still -= 1

    return quotas


def sample_from_category_pool(pool: List[NewsItem], need: int, rng: random.Random) -> List[NewsItem]:
    if need <= 0 or not pool:
        return []

    subcat_map: Dict[str, List[NewsItem]] = defaultdict(list)
    for item in pool:
        subcat_map[item.subcategory].append(item)

    for sub_items in subcat_map.values():
        rng.shuffle(sub_items)

    chosen: List[NewsItem] = []
    subcats = sorted(subcat_map, key=lambda s: len(subcat_map[s]), reverse=True)

    while len(chosen) < need and subcats:
        next_subcats = []
        for sub in subcats:
            if len(chosen) >= need:
                break
            items = subcat_map[sub]
            if not items:
                continue
            chosen.append(items.pop())
            if items:
                next_subcats.append(sub)
        subcats = next_subcats

    if len(chosen) < need:
        leftovers = [item for items in subcat_map.values() for item in items]
        rng.shuffle(leftovers)
        chosen.extend(leftovers[: need - len(chosen)])

    return chosen[:need]


def sample_items(
    items: List[NewsItem],
    sample_size: int,
    min_category_count: int,
    rng: random.Random,
    banned_ids: set[str] | None = None,
) -> List[NewsItem]:
    banned_ids = banned_ids or set()
    filtered = [i for i in items if i.news_id not in banned_ids]

    category_counts = Counter(i.category for i in filtered)
    categories = {c: n for c, n in category_counts.items() if n >= min_category_count}
    if not categories:
        categories = dict(category_counts)

    category_pool: Dict[str, List[NewsItem]] = defaultdict(list)
    for item in filtered:
        if item.category in categories:
            category_pool[item.category].append(item)

    for cat_items in category_pool.values():
        rng.shuffle(cat_items)

    quotas = allocate_quota({k: len(v) for k, v in category_pool.items()}, sample_size)

    selected: List[NewsItem] = []
    for category, need in sorted(quotas.items()):
        selected.extend(sample_from_category_pool(category_pool[category], need, rng))

    if len(selected) < sample_size:
        chosen_ids = {i.news_id for i in selected}
        leftovers = [
            i for i in filtered if i.category in category_pool and i.news_id not in chosen_ids
        ]
        rng.shuffle(leftovers)
        selected.extend(leftovers[: sample_size - len(selected)])

    if len(selected) > sample_size:
        rng.shuffle(selected)
        selected = selected[:sample_size]

    return selected


def write_annotation_csv(path: Path, items: List[NewsItem]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "news_id": item.news_id,
                    "category": item.category,
                    "subcategory": item.subcategory,
                    "title": item.title,
                    "abstract": item.abstract,
                    "classification": "",
                    "justification": "",
                    "confidence": "",
                    "notes": "",
                }
            )


def write_report(
    path: Path,
    stats: LoadStats,
    total_dedup: int,
    pilot: List[NewsItem],
    main: List[NewsItem],
    validation: List[NewsItem],
) -> None:
    def fmt_counts(name: str, items: List[NewsItem]) -> str:
        counts = Counter(i.category for i in items)
        lines = [f"### {name}"]
        lines.append("By category:")
        for category, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"- {category}: {count}")
        return "\n".join(lines)

    content = [
        "# Manual Annotation Sampling Report",
        "",
        "## Dataset Counts",
        f"- Raw rows read from source: {stats.total_rows}",
        f"- Malformed rows (<8 columns): {stats.malformed_rows}",
        f"- Rows removed for missing required fields: {stats.missing_required_rows}",
        f"- Eligible rows after completeness filter: {stats.eligible_rows}",
        f"- Rows after deduplication: {total_dedup}",
        "",
        fmt_counts("Pilot Sample", pilot),
        "",
        fmt_counts("Main Sample", main),
        "",
        fmt_counts("Validation Sample", validation),
        "",
    ]
    path.write_text("\n".join(content), encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    eligible_items, stats = load_items(SOURCE)
    dedup_items = deduplicate_items(eligible_items)

    pilot = sample_items(dedup_items, PILOT_SIZE, MIN_CATEGORY_COUNT, rng)

    banned = {item.news_id for item in pilot}
    main_sample = sample_items(dedup_items, MAIN_SIZE, MIN_CATEGORY_COUNT, rng, banned)

    banned.update(i.news_id for i in main_sample)
    validation_sample = sample_items(
        dedup_items, VALIDATION_SIZE, MIN_CATEGORY_COUNT, rng, banned
    )

    pilot_path = OUTPUT_DIR / f"mindsmall_train_annotation_pilot_{PILOT_SIZE}.csv"
    main_path = OUTPUT_DIR / f"mindsmall_train_annotation_main_{MAIN_SIZE}.csv"
    validation_path = OUTPUT_DIR / f"mindsmall_train_annotation_validation_{VALIDATION_SIZE}.csv"
    report_path = OUTPUT_DIR / "sampling_report.md"

    write_annotation_csv(pilot_path, pilot)
    write_annotation_csv(main_path, main_sample)
    write_annotation_csv(validation_path, validation_sample)
    write_report(report_path, stats, len(dedup_items), pilot, main_sample, validation_sample)

    print(f"Generated: {pilot_path}")
    print(f"Generated: {main_path}")
    print(f"Generated: {validation_path}")
    print(f"Generated: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
