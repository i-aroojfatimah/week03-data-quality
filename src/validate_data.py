"""Validation rules for the Week 3 plant shift log.

Six checks are written for you as worked examples. Six are marked TODO and are
your work in this lab. Run the tests to see which ones are outstanding:

    pytest -q

Every check answers the same four questions:

    name         what do we call this rule?
    expectation  what should be true, in one sentence a supervisor can read?
    mask         which rows break it?
    affected     which line numbers in the CSV should a human open?

A check never repairs data. It produces evidence and lets a person decide.
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

# Course review threshold. This is a teaching value, not an approved plant
# safety limit. A row above it is flagged for a human, never deleted.
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
    """Return one-based CSV line numbers, counting the header as line 1."""
    return [int(index) + 2 for index in mask[mask].index]


def result(name: str, mask: pd.Series, expectation: str) -> CheckResult:
    """Turn a boolean mask of FAILING rows into a check result."""
    affected = csv_line_numbers(mask)
    return CheckResult(name, not affected, len(affected), expectation, affected)


# ---------------------------------------------------------------------------
# WORKED EXAMPLES - read these before writing your own
# ---------------------------------------------------------------------------

def check_required_columns(frame: pd.DataFrame) -> CheckResult:
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    return CheckResult(
        name="required_columns",
        passed=not missing,
        observed=missing,
        expectation="all eight contracted columns are present",
        affected_rows=[],
    )


def check_timestamp_parse(frame: pd.DataFrame) -> CheckResult:
    parsed = pd.to_datetime(frame["timestamp"], format="ISO8601", errors="coerce")
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
    # notna() first: a missing value is the completeness check's business,
    # and reporting it twice hides how many distinct problems the file has.
    outside = frame["downtime_min"].notna() & ~frame["downtime_min"].between(0, 60)
    return result(
        "downtime_range",
        outside,
        "downtime_min is between 0 and 60 minutes within an hourly period",
    )


def check_motor_temperature_review_range(frame: pd.DataFrame) -> CheckResult:
    outside = ~frame["motor_temp_c"].between(MIN_MOTOR_TEMP_C, MAX_MOTOR_TEMP_C)
    return result(
        "motor_temperature_review_range",
        outside,
        f"motor_temp_c sits between {MIN_MOTOR_TEMP_C:g} and {MAX_MOTOR_TEMP_C:g} "
        "under the course review rule, which is not an approved plant limit",
    )


# ---------------------------------------------------------------------------
# YOUR WORK - replace each `raise NotImplementedError` with a real check
# ---------------------------------------------------------------------------

def check_business_key_uniqueness(frame: pd.DataFrame) -> CheckResult:
    """One row should describe one line in one hourly period.

    Fail every row that shares its timestamp and line_id with another row.
    Note that this is not the same question as exact_row_uniqueness: two
    records for the same line-hour may disagree about the units produced,
    and that is the more dangerous case.

    Hint: pandas `DataFrame.duplicated` accepts a subset of columns.
    """
    raise NotImplementedError("Write check_business_key_uniqueness")


def check_known_line_ids(frame: pd.DataFrame) -> CheckResult:
    """line_id should name one of the three production lines in EXPECTED_LINES.

    Fail any row naming something else. Watch for values that look correct to
    a human reader but not to a computer: a different case, or a trailing
    space. The course contract treats those as defects to report rather than
    to tidy away, because the file that produced them will produce more.
    Add a comment saying what a cleaning step would have to record before it
    could be allowed to strip them instead.
    """
    raise NotImplementedError("Write check_known_line_ids")


def check_positive_energy(frame: pd.DataFrame) -> CheckResult:
    """A line that ran for an hour consumed energy, so energy_kwh exceeds zero.

    Fail any row where it does not. Keep the original value in the file: the
    check reports the row, it does not correct the reading.
    """
    raise NotImplementedError("Write check_positive_energy")


def check_rejects_within_output(frame: pd.DataFrame) -> CheckResult:
    """A line cannot reject more units than it produced.

    This rule needs no engineering authority to justify: it follows from what
    the two columns mean. Fail any row where rejected_units exceeds
    units_produced, and also consider whether a negative count is possible.
    """
    raise NotImplementedError("Write check_rejects_within_output")


def check_shift_matches_hour(frame: pd.DataFrame) -> CheckResult:
    """The shift label should agree with the hour of the timestamp.

    The course rule is Day for 06:00 to 17:59 and Night for 18:00 to 05:59.
    Fail any row whose label disagrees. A row whose timestamp does not parse
    cannot be judged here, so leave it to the timestamp_parse check.

    Hint: `pd.to_datetime(...).dt.hour` gives you the hour as a number.
    """
    raise NotImplementedError("Write check_shift_matches_hour")


def check_expected_line_hour_coverage(frame: pd.DataFrame) -> CheckResult:
    """Stretch check. Each expected line should have 24 distinct hourly records.

    This one reports on lines rather than rows, so build the CheckResult by
    hand instead of calling `result`. Put the count per line in `observed`,
    leave `affected_rows` empty, and count distinct business keys so that a
    duplicated line-hour does not disguise a missing one.
    """
    raise NotImplementedError("Write check_expected_line_hour_coverage")


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


def validate(path: Path, skip_unwritten: bool = False) -> dict:
    """Run every check against the file at `path`.

    With skip_unwritten=True an unfinished check is recorded as "not written"
    rather than stopping the run, so you can use the script from the first
    minute of the lab.
    """
    frame = pd.read_csv(path)
    checks: list[CheckResult] = []
    unwritten: list[str] = []

    schema = check_required_columns(frame)
    checks.append(schema)
    if not schema.passed:
        # Nothing below can be trusted if the contracted columns are missing.
        return build_payload(path, frame, checks, unwritten)

    for check in CHECKS[1:]:
        try:
            checks.append(check(frame))
        except NotImplementedError:
            if not skip_unwritten:
                raise
            unwritten.append(check.__name__)

    return build_payload(path, frame, checks, unwritten)


def build_payload(path: Path, frame: pd.DataFrame, checks: list[CheckResult], unwritten: list[str]) -> dict:
    failed = [check.name for check in checks if not check.passed]
    return {
        "dataset": path.as_posix(),
        "sha256": sha256(path),
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "status": "PASS" if not failed else "FAIL",
        "failed_checks": failed,
        "unwritten_checks": unwritten,
        "checks": [asdict(check) for check in checks],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Week 3 plant shift log.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--skip-unwritten",
        action="store_true",
        help="report unfinished checks instead of stopping on them",
    )
    args = parser.parse_args()

    try:
        payload = validate(args.input, skip_unwritten=args.skip_unwritten)
    except NotImplementedError as unwritten:
        # A half-finished validator should say so in one line, not in a traceback.
        print(f"Cannot run yet: {unwritten}")
        print("Finish the TODO checks in src/validate_data.py (pytest -q lists them),")
        print("or add --skip-unwritten to run the checks you have written so far.")
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"Dataset:     {args.input}")
    print(f"Fingerprint: {payload['sha256']}")
    print(f"Rows:        {payload['rows']}")
    print()
    for check in payload["checks"]:
        marker = "PASS" if check["passed"] else "FAIL"
        detail = check["observed"]
        rows = check["affected_rows"]
        location = f"  CSV lines {rows}" if rows else ""
        print(f"{marker:4}  {check['name']}: {detail}{location}")
    for name in payload["unwritten_checks"]:
        print(f"TODO  {name}: not written yet")
    print()
    print(f"Overall status: {payload['status']}")
    print(f"Result written to: {args.output}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
