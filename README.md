# Week 3 Lab: Data Quality and Validation

A file lands on your desk at 07:50. The shift handover is at 08:00, and a
supervisor is going to decide which production line gets attention today.

Your job in the next two hours is not to clean the file. It is to find out what
the file will not support, write checks that catch it next time, and put your
name to a decision about its use.

## Your file is yours

Generate your own copy before anything else:

```bash
python src/make_variant.py --student-id your-github-username
```

This writes `data/raw/shift_log_<your-username>.csv`. The faults in it are
generated from your username, so they differ from the person next to you. Your
instructor can regenerate your exact file from your username, which is also how
your report is marked. Compare methods with your neighbour; copying findings
will produce a report about someone else's file.

**Never edit a file in `data/raw/`.** A fault you delete is a fault nobody else
can see. Everything you produce goes in `docs/`, `artifacts/`, or `src/`.

## Three rules

1. **Report, do not repair.** A correction needs a source, an approver, and a record.
2. **Impossible is not the same as surprising.** Negative energy contradicts what
   the column means. A high motor temperature might be an error, a real event, or
   a line running differently. Only the first kind can be settled from the file.
3. **Name your evidence.** "CSV line 44" beats "some temperatures look high".

## Sequence (120 minutes)

| Part | Minutes | What you do |
|---|---:|---|
| A. Generate and fingerprint | 10 | Produce your file, record its SHA-256, state the data contract in words |
| B. Hunt | 20 | Find suspect records yourself, in the notebook, before any validator runs |
| C. Commit to your list | 5 | Write your findings into the report **before** you see what the checks say |
| D. Make the tests pass | 40 | Write the six missing checks in `src/validate_data.py` until `pytest -q` is green |
| E. Beat your partner's validator | 20 | Swap, write rows that pass their checks and should not, add a check that stops one |
| F. Decide and push | 25 | Complete the approval sentence, finish the report, commit |

### A. Generate and fingerprint

Open `week03` in VS Code, create the environment, and install:

```bash
python -m venv .venv
source .venv/bin/activate          # macOS or Linux
.venv\Scripts\Activate.ps1         # Windows PowerShell
python -m pip install -r requirements.txt
python src/make_variant.py --student-id your-github-username
```

Record the file name and fingerprint in `docs/data_quality_report.md`. A
fingerprint is what lets someone else confirm they are looking at the same
evidence you were.

### B and C. Hunt, then commit

Open `notebooks/week3_data_quality.ipynb` and work to the end of Step 3. The
notebook asks you to write your own detection code rather than run ours.

Step 3 asks you to write your suspect list into the report **before** running
the validator. Do it honestly. The difference between your list and the
validator's output is the most useful thing you will learn today, and it only
exists if you commit first.

### D. Make the tests pass

```bash
pytest -q
```

Twelve tests fail. Six checks in `src/validate_data.py` are marked TODO, and
six checks above them are worked examples to read first. Write one check,
re-run, repeat. When the tests are green:

```bash
python src/validate_data.py --input data/raw/shift_log_<your-username>.csv \
  --output artifacts/validation_results.json
```

Exit status `1` means validation ran and found failures. It does not mean the
program crashed. Status `2` means a check is still a TODO, and `0` means every
rule passed. Check with `echo $?` on macOS or Linux, `echo $LASTEXITCODE`
on Windows PowerShell. A validator that always exits `0` protects nothing.

### E. Beat your partner's validator

Follow `docs/attack_log.md`. Write three rows that are nonsense in a real plant
and that their checks accept anyway. Think about what a rule does **not** say:
a range check says nothing about a line producing 400 units with 60 minutes of
downtime in the same hour.

Then add one check to your own validator that stops one of the attacks you
received, with a test for it.

### F. Decide and push

Complete the sentence at the top of `docs/dataset_approval.md`, finish the
report, then:

```bash
git status
git add README.md src/ tests/ docs/ notebooks/ artifacts/validation_results.json data/raw/
git commit -m "Complete Week 3 validation checkpoint"
git push
```

Do not commit `.venv`, notebook checkpoints, or caches.

## What you submit

1. `data/raw/shift_log_<your-username>.csv`, unedited;
2. the executed `notebooks/week3_data_quality.ipynb`, including your written answers;
3. `src/validate_data.py` with all twelve checks written, plus the one you added in Part E;
4. `tests/test_validate_data.py` with your new test, `pytest -q` green;
5. `artifacts/validation_results.json`;
6. `docs/data_quality_report.md`, `docs/dataset_approval.md`, `docs/attack_log.md`;
7. the assumptions section below, completed.

## How this is marked

| Weight | What earns it |
|---:|---|
| 30% | The six checks are correct, and the test you added catches a real attack |
| 25% | The report separates observation from interpretation, and names records precisely |
| 20% | The approval sentence is specific enough to be acted on and to be wrong |
| 15% | Part C was answered honestly, including what you missed |
| 10% | The raw file is unchanged and the repository is clean |

You are not marked on finding every fault. You are marked on what you do with
the ones you found and on being straight about the ones you did not.

## Scenario and decision boundary

One row represents one production line in one hourly period, across three lines
and one simulated day. The file contains no verified failures, inspections,
repairs, or intervention outcomes.

The approved question stays narrow:

> Which line deserves descriptive review at the next shift handover, subject to
> data-quality warnings and human confirmation?

This file does not predict machine failure. Nothing you do today changes that.

## Data source, licence, and assumptions

### Source

- File: `data/raw/shift_log_<your-username>.csv`
- Origin: simulated for this course by `src/make_variant.py`, seeded from your username
- Coverage: three production lines, hourly, one simulated day
- Personal or sensitive data: none
- Fingerprint: **paste the SHA-256 from the notebook**

### Licence and reuse boundary

Supplied for teaching use in this course repository. No public or commercial
reuse licence is asserted. Ask the instructor before publishing or redistributing.

### Assumptions to complete

- One row represents: **[complete]**
- The decision window is: **[complete]**
- The expected line identifiers are: **[complete]**
- The expected timestamp cadence is: **[complete]**
- The engineering source for the temperature limit is: **[complete or state Unknown]**
- The permitted analytical use is: **[complete]**
- A prohibited claim is: **[complete]**

## Before you push

- `git diff` shows no change to anything in `data/raw/`;
- `pytest -q` is green, including your added test;
- the notebook has saved outputs and no traceback;
- `artifacts/validation_results.json` exists and records failed checks;
- the approval sentence has no blanks left in it.
