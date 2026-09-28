# Week 3 Attack Log

Validation is never finished. The only way to find out what your checks miss is
to have someone try to get past them.

## The round

1. Swap validators with your partner. You now work against **their**
   `src/validate_data.py`, and they work against yours.
2. Write three rows that are **operationally nonsense** but that their checks
   **accept**. A row that fails a check is not an attack; it is a check working.
3. Append your rows to a copy of their file (`data/processed/attack_<yourname>.csv`,
   never the raw file) and run their validator to confirm it passes.
4. Hand back the rows and the log.

## My attacks on my partner's validator

Partner:

| # | The row I wrote | Why it is nonsense in a real plant | Why their checks accepted it |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

## Attacks that got past my validator

| # | Their row | Why my checks accepted it | The check I would add |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

## The check I actually added

Name it, paste the code, and say which attack it stops. Add a test for it in
`tests/test_validate_data.py` and confirm `pytest -q` is green.

```python

```

## What this round changed about your approval decision

One or two sentences. If it changed nothing, say why you are confident.
