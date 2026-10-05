"""Validation rules for the Week 3 plant shift log.

The validator reports data-quality problems. It never repairs the raw data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "timestamp",
    "line_id",
    "shift",
    "units_produced",
    "downtime_min",
    "energy_kwh",
    "rejected_units",
    "motor_temp_c",
]

EXPECTED_LINES = {"Line_A", "Line_B", "Line_C"}

BUSINESS_KEY = ["timestamp", "line_id"]

EXPECTED_HOURS_PER_LINE = 24

# Teaching review values only.
# These are NOT approved plant safety limits.
MAX_MOTOR_TEMP_C = 100.0
MIN_MOTOR_TEMP_C = 40.0


@dataclass
class CheckResult:
    name: str
    passed: bool
    observed: object
    expectation: str
    affected_rows: list[int]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)

    return digest.hexdigest()


def csv_line_numbers(mask: pd.Series) -> list[int]:
    """Return one-based CSV line numbers, counting header as line 1."""
    return [int(index) + 2 for index in mask[mask].index]


def result(
    name: str,
    mask: pd.Series,
    expectation: str,
) -> CheckResult:
    """Create a CheckResult from a boolean failing-row mask."""
    affected = csv_line_numbers(mask)

    return CheckResult(
        name=name,
        passed=not affected,
        observed=len(affected),
        expectation=expectation,
        affected_rows=affected,
    )


# ---------------------------------------------------------------------------
# WORKED EXAMPLES
# ---------------------------------------------------------------------------

def check_required_columns(frame: pd.DataFrame) -> CheckResult:
    missing = sorted(
        set(REQUIRED_COLUMNS) - set(frame.columns)
    )

    return CheckResult(
        name="required_columns",
        passed=not missing,
        observed=missing,
        expectation="all eight contracted columns are present",
        affected_rows=[],
    )


def check_timestamp_parse(frame: pd.DataFrame) -> CheckResult:
    parsed = pd.to_datetime(
        frame["timestamp"],
        format="ISO8601",
        errors="coerce",
    )

    return result(
        "timestamp_parse",
        parsed.isna(),
        "every timestamp reads as an ISO-8601 date and time",
    )


def check_required_values_complete(frame: pd.DataFrame) -> CheckResult:
    return result(
        "required_values_complete",
        frame[REQUIRED_COLUMNS].isna().any(axis=1),
        "required fields contain no missing values",
    )


def check_exact_row_uniqueness(frame: pd.DataFrame) -> CheckResult:
    return result(
        "exact_row_uniqueness",
        frame.duplicated(keep=False),
        "no row repeats every field of another row",
    )


def check_downtime_range(frame: pd.DataFrame) -> CheckResult:
    outside = (
        frame["downtime_min"].notna()
        & ~frame["downtime_min"].between(0, 60)
    )

    return result(
        "downtime_range",
        outside,
        "downtime_min is between 0 and 60 minutes per hourly period",
    )


def check_motor_temperature_review_range(
    frame: pd.DataFrame,
) -> CheckResult:
    outside = ~frame["motor_temp_c"].between(
        MIN_MOTOR_TEMP_C,
        MAX_MOTOR_TEMP_C,
    )

    return result(
        "motor_temperature_review_range",
        outside,
        (
            f"motor_temp_c sits between {MIN_MOTOR_TEMP_C:g} and "
            f"{MAX_MOTOR_TEMP_C:g} under the course review rule"
        ),
    )


# ---------------------------------------------------------------------------
# YOUR WEEK 3 CHECKS
# ---------------------------------------------------------------------------

def check_business_key_uniqueness(
    frame: pd.DataFrame,
) -> CheckResult:
    """One line should have at most one record per timestamp."""

    duplicate_mask = frame.duplicated(
        subset=BUSINESS_KEY,
        keep=False,
    )

    return result(
        "business_key_uniqueness",
        duplicate_mask,
        "each timestamp and line_id combination appears at most once",
    )


def check_known_line_ids(frame: pd.DataFrame) -> CheckResult:
    """Only the three expected production lines are allowed."""

    invalid = ~frame["line_id"].isin(EXPECTED_LINES)

    return result(
        "known_line_ids",
        invalid,
        "line_id must be one of the three expected production lines",
    )


def check_positive_energy(frame: pd.DataFrame) -> CheckResult:
    """Energy must be greater than zero."""

    invalid = (
        frame["energy_kwh"].notna()
        & (frame["energy_kwh"] <= 0)
    )

    return result(
        "positive_energy",
        invalid,
        "energy_kwh must be greater than zero for each hourly record",
    )


def check_rejects_within_output(
    frame: pd.DataFrame,
) -> CheckResult:
    """Rejected units cannot be negative or exceed production."""

    invalid = (
        frame["rejected_units"].notna()
        & frame["units_produced"].notna()
        & (
            (frame["rejected_units"] < 0)
            | (frame["units_produced"] < 0)
            | (
                frame["rejected_units"]
                > frame["units_produced"]
            )
        )
    )

    return result(
        "rejects_within_output",
        invalid,
        (
            "rejected_units must be non-negative and "
            "cannot exceed units produced"
        ),
    )


def check_shift_matches_hour(
    frame: pd.DataFrame,
) -> CheckResult:
    """Shift must agree with the timestamp hour."""

    parsed = pd.to_datetime(
        frame["timestamp"],
        format="ISO8601",
        errors="coerce",
    )

    hour = parsed.dt.hour

    expected_shift = hour.map(
        lambda h: (
            "Day"
            if 6 <= h <= 17
            else "Night"
        )
    )

    # Invalid timestamps are handled by timestamp_parse.
    # Do not report the same problem twice here.
    invalid = (
        parsed.notna()
        & frame["shift"].ne(expected_shift)
    )

    return result(
        "shift_matches_hour",
        invalid,
        (
            "shift is Day from 06:00 to 17:59 and "
            "Night from 18:00 to 05:59"
        ),
    )


def check_expected_line_hour_coverage(
    frame: pd.DataFrame,
) -> CheckResult:
    """Each expected line should have 24 distinct hourly records."""

    distinct_keys = (
        frame[BUSINESS_KEY]
        .drop_duplicates()
    )

    counts = (
        distinct_keys
        .groupby("line_id")
        .size()
        .reindex(
            sorted(EXPECTED_LINES),
            fill_value=0,
        )
    )

    passed = bool(
        (counts == EXPECTED_HOURS_PER_LINE).all()
    )

    return CheckResult(
        name="expected_line_hour_coverage",
        passed=passed,
        observed={
            line: int(count)
            for line, count in counts.items()
        },
        expectation=(
            "each expected line has 24 distinct hourly records"
        ),
        affected_rows=[],
    )


CHECKS = [
    check_required_columns,
    check_timestamp_parse,
    check_required_values_complete,
    check_exact_row_uniqueness,
    check_business_key_uniqueness,
    check_known_line_ids,
    check_positive_energy,
    check_rejects_within_output,
    check_downtime_range,
    check_motor_temperature_review_range,
    check_shift_matches_hour,
    check_expected_line_hour_coverage,
]


def validate(
    path: Path,
    skip_unwritten: bool = False,
) -> dict:
    """Run every validation check against the CSV."""

    frame = pd.read_csv(path)

    checks: list[CheckResult] = []
    unwritten: list[str] = []

    schema = check_required_columns(frame)
    checks.append(schema)

    if not schema.passed:
        return build_payload(
            path,
            frame,
            checks,
            unwritten,
        )

    for check in CHECKS[1:]:
        try:
            checks.append(check(frame))

        except NotImplementedError:
            if not skip_unwritten:
                raise

            unwritten.append(check.__name__)

    return build_payload(
        path,
        frame,
        checks,
        unwritten,
    )


def build_payload(
    path: Path,
    frame: pd.DataFrame,
    checks: list[CheckResult],
    unwritten: list[str],
) -> dict:

    failed = [
        check.name
        for check in checks
        if not check.passed
    ]

    return {
        "dataset": path.as_posix(),
        "sha256": sha256(path),
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "status": (
            "PASS"
            if not failed
            else "FAIL"
        ),
        "failed_checks": failed,
        "unwritten_checks": unwritten,
        "checks": [
            asdict(check)
            for check in checks
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a Week 3 plant shift log."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--skip-unwritten",
        action="store_true",
        help=(
            "report unfinished checks instead of "
            "stopping on them"
        ),
    )

    args = parser.parse_args()

    try:
        payload = validate(
            args.input,
            skip_unwritten=args.skip_unwritten,
        )

    except NotImplementedError as unwritten:
        print(
            f"Cannot run yet: {unwritten}"
        )
        print(
            "Finish the TODO checks in "
            "src/validate_data.py (pytest -q lists them),"
        )
        print(
            "or add --skip-unwritten to run "
            "the checks written so far."
        )
        return 2

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            payload,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print(
        f"Dataset:     {args.input}"
    )
    print(
        f"Fingerprint: {payload['sha256']}"
    )
    print(
        f"Rows:        {payload['rows']}"
    )
    print()

    for check in payload["checks"]:
        marker = (
            "PASS"
            if check["passed"]
            else "FAIL"
        )

        detail = check["observed"]
        rows = check["affected_rows"]

        location = (
            f"  CSV lines {rows}"
            if rows
            else ""
        )

        print(
            f"{marker:4}  "
            f"{check['name']}: "
            f"{detail}{location}"
        )

    for name in payload["unwritten_checks"]:
        print(
            f"TODO  {name}: not written yet"
        )

    print()
    print(
        f"Overall status: {payload['status']}"
    )
    print(
        f"Result written to: {args.output}"
    )

    return (
        0
        if payload["status"] == "PASS"
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())