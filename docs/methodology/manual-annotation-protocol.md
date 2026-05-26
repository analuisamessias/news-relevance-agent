# Manual Annotation Protocol

## Purpose
This step creates a small, diverse, and practical reference set for:

- initial manual labeling;
- example retrieval in the knowledge base;
- final sanity check of agent outputs on a separate sample.

## Source
- File: `data/MINDsmall_train/news.tsv`
- Selected fields for annotation: `news_id`, `category`, `subcategory`, `title`, `abstract`

## Applied Filters
- Remove malformed rows (<8 columns).
- Keep only rows with non-empty `news_id`, `category`, `subcategory`, `title`, and `abstract`.
- Remove exact duplicates by normalized `(title + abstract)`.

## Sampling Logic
- Select items across categories.
- Inside each category, spread selection across subcategories.
- Use fixed random seed for reproducibility.

## Sample Sizes
- Pilot: `10`
- Main: `40`
- Validation holdout: `10`

## Execution

```bash
python3 scripts/generate_manual_annotation_samples.py
```

## Generated Files
- `annotations/manual/mindsmall_train_annotation_pilot_10.csv`
- `annotations/manual/mindsmall_train_annotation_main_40.csv`
- `annotations/manual/mindsmall_train_annotation_validation_10.csv`
- `annotations/manual/sampling_report.md`

## Annotation Template Columns
- `news_id`
- `category`
- `subcategory`
- `title`
- `abstract`
- `classification`
- `justification`
- `confidence`
- `notes`

The last four columns are intentionally empty for manual filling.
