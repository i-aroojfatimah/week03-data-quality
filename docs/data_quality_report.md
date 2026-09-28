# Week 3 Data Quality Report

Keep this to one page. A supervisor should be able to read it in two minutes
and know what they may do with the file.

## 1. What I examined

- File name:
- SHA-256 fingerprint:
- Rows / columns:
- One row represents:
- The business key is:
- Reviewed by / date:

## 2. What I found before running the validator

Fill this in **during Step 3 of the notebook**, before you compare against the
checks. Do not go back and improve it afterwards; the gap is the point.

| # | Record (line and hour) | What I noticed |
|---|---|---|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |

## 3. What the checks found

One row per distinct problem. If one fault trips two checks, say so rather than
counting it twice.

| Check | CSV line(s) | Observation (no speculation) | Impossible or surprising? | What should happen next | Who owns it |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 4. The gap

- Found by the checks, missed by me:
- Found by me, covered by no check:
- The check I added or would add as a result:

## 5. The judgement call

The high motor temperature reading is unusual, not impossible.

- Three explanations, one of which is not a fault:
- The single piece of evidence that would separate them:
- Who holds it:

## 6. What this file can and cannot support

Connect this back to the Week 2 decision boundary in two or three sentences.
Name one calculation that is still safe and one that is not, and say why the
difference follows from the specific faults you found.
