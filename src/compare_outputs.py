from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from utils import ND, normalize_nd, read_table


def normalize_frame(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in result.columns:
        result[column] = result[column].map(normalize_nd)
    return result


def compare(generated_path: Path, reference_path: Path, sample_size: int = 10) -> dict[str, Any]:
    generated = normalize_frame(read_table(generated_path))
    reference = normalize_frame(read_table(reference_path))

    generated_columns = list(generated.columns)
    reference_columns = list(reference.columns)
    common_columns = [column for column in reference_columns if column in generated.columns]
    max_rows = max(len(generated), len(reference))
    comparable_rows = min(len(generated), len(reference))

    missing_columns = [column for column in reference_columns if column not in generated.columns]
    extra_columns = [column for column in generated_columns if column not in reference.columns]
    order_differences = [
        {"position": index + 1, "generated": generated_columns[index] if index < len(generated_columns) else None, "reference": reference_columns[index] if index < len(reference_columns) else None}
        for index in range(max(len(generated_columns), len(reference_columns)))
        if (generated_columns[index] if index < len(generated_columns) else None) != (reference_columns[index] if index < len(reference_columns) else None)
    ]

    mismatch_counts: dict[str, int] = {}
    sample_mismatches: list[dict[str, Any]] = []
    compared_cells = comparable_rows * len(common_columns)
    matching_cells = 0

    for column in common_columns:
        gen_values = generated[column].iloc[:comparable_rows].reset_index(drop=True)
        ref_values = reference[column].iloc[:comparable_rows].reset_index(drop=True)
        equal_mask = gen_values.eq(ref_values)
        matches = int(equal_mask.sum())
        matching_cells += matches
        mismatches = int((~equal_mask).sum())
        mismatch_counts[column] = mismatches
        if mismatches and len(sample_mismatches) < sample_size:
            mismatch_indexes = equal_mask[~equal_mask].index.tolist()
            for row_index in mismatch_indexes:
                sample_mismatches.append(
                    {
                        "row": row_index + 2,
                        "column": column,
                        "generated": gen_values.iloc[row_index],
                        "reference": ref_values.iloc[row_index],
                    }
                )
                if len(sample_mismatches) == sample_size:
                    break

    exact_match_percentage = (matching_cells / compared_cells * 100) if compared_cells else 100.0

    return {
        "generated_shape": generated.shape,
        "reference_shape": reference.shape,
        "row_count_difference": len(generated) - len(reference),
        "column_count_difference": len(generated_columns) - len(reference_columns),
        "missing_columns": missing_columns,
        "extra_columns": extra_columns,
        "column_order_differences": order_differences,
        "per_column_mismatch_counts": mismatch_counts,
        "sample_mismatching_cells": sample_mismatches,
        "exact_match_percentage": exact_match_percentage,
        "compared_cells": compared_cells,
        "matching_cells": matching_cells,
        "unmatched_generated_rows": max(0, len(generated) - len(reference)),
        "unmatched_reference_rows": max(0, len(reference) - len(generated)),
    }


def print_report(report: dict[str, Any]) -> None:
    print(f"Generated shape: {report['generated_shape'][0]} rows x {report['generated_shape'][1]} columns")
    print(f"Reference shape: {report['reference_shape'][0]} rows x {report['reference_shape'][1]} columns")
    print(f"Row count difference: {report['row_count_difference']}")
    print(f"Column count difference: {report['column_count_difference']}")
    print(f"Missing columns: {report['missing_columns'] or 'None'}")
    print(f"Extra columns: {report['extra_columns'] or 'None'}")
    print(f"Column order differences: {len(report['column_order_differences'])}")
    for diff in report["column_order_differences"][:10]:
        print(f"  Position {diff['position']}: generated={diff['generated']!r} reference={diff['reference']!r}")

    print("Per-column mismatch counts:")
    for column, count in report["per_column_mismatch_counts"].items():
        if count:
            print(f"  {column}: {count}")

    print("Sample mismatching cells:")
    if not report["sample_mismatching_cells"]:
        print("  None")
    for mismatch in report["sample_mismatching_cells"]:
        print(
            f"  Row {mismatch['row']}, {mismatch['column']}: "
            f"generated={mismatch['generated']!r} reference={mismatch['reference']!r}"
        )
    print(f"Exact match percentage: {report['exact_match_percentage']:.2f}% ({report['matching_cells']}/{report['compared_cells']} compared cells)")
    if report["unmatched_generated_rows"] or report["unmatched_reference_rows"]:
        print(f"Unmatched generated rows: {report['unmatched_generated_rows']}")
        print(f"Unmatched reference rows: {report['unmatched_reference_rows']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare a generated V3 output against a reference V3 CSV/XLSX.")
    parser.add_argument("--generated", required=True, type=Path, help="Generated V3 CSV/XLSX.")
    parser.add_argument("--reference", required=True, type=Path, help="Reference V3 CSV/XLSX.")
    parser.add_argument("--sample-size", default=10, type=int, help="Number of sample mismatching cells to print.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print_report(compare(args.generated, args.reference, args.sample_size))


if __name__ == "__main__":
    main()
