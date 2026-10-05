# Week 3 Data Quality Report

Keep this to one page. A supervisor should be able to read it in two minutes
and know what they may do with the file.


## 1. What I examined

- File name: data/raw/shift_log_i-aroojfatimah.csv
- SHA-256 fingerprint: 05525440ad4db1ff572ebd2218851e57569fcde4957c43e353e223881d8f036a
- Rows / columns: 73 / 8
- One row represents: One line-hour observation
- The business key is: timestamp + line_id
- Reviewed by / date: Arooj Fatima / 2026-10-05

## 2. What I found before running the validator

Fill this in **during Step 3 of the notebook**, before you compare against the
checks. Do not go back and improve it afterwards; the gap is the point.

|| # | Record (line and hour) | What I noticed |
|---|---|---|
| 1 | Line_B, 2026-01-12T06:00 | `downtime_min` is missing (NaN). |
| 2 | Line_C, 2026-01-12T12:00 | `energy_kwh` is negative (-14.9), which is impossible under the data contract. |
| 3 | Line_A, 2026-01-12T08:00 | `motor_temp_c` is unusually high at 118.3°C; it is surprising but not proven impossible without an approved engineering limit. |

## 3. What the checks found

| Check | CSV line(s) | Observation (no speculation) | Impossible or surprising? | What should happen next | Who owns it |
|---|---:|---|---|---|---|
| timestamp_parse | 68 | The timestamp value on CSV line 68 could not be parsed as a valid timestamp. | Impossible / invalid | Verify the original timestamp against the source record before use. | Data owner |
| required_values_complete | 3 | `downtime_min` is missing on CSV line 3. | Invalid | Verify the missing value from the source record; do not fill it without evidence. | Data owner |
| exact_row_uniqueness / business_key_uniqueness | 29, 74 | The same line-hour appears more than once, triggering both duplicate checks. | Invalid | Identify the authoritative record and document the duplicate before any correction. | Data owner |
| positive_energy | 22 | `energy_kwh` is -14.9 on CSV line 22. | Impossible | Verify the energy reading against the source record and approved data-entry process. | Data owner / engineering |
| motor_temperature_review_range | 8 | `motor_temp_c` is 118.3°C on CSV line 8. | Surprising | Compare with the approved engineering limit and the original sensor/inspection record. | Engineering |
| shift_matches_hour | 45 | The shift value does not match the hour recorded on CSV line 45. | Invalid | Verify the timestamp and shift assignment against the shift schedule. | Operations / data owner |


## 4. The gap

* Found by the checks, missed by me: The timestamp parsing problem on CSV line 68 and the shift-hour mismatch on CSV line 45.
* Found by me, covered by no check: None of the issues I identified manually were left without a written check.
* The check I added or would add as a result: The `timestamp_parse` and `shift_matches_hour` checks ensure these consistency problems are detected.


## 5. The judgement call


The high motor temperature reading is unusual, not impossible.

* Three explanations, one of which is not a fault: The temperature could be a genuine high reading from the motor; it could be a sensor or recording error; or it could be a valid reading caused by an unusual operating condition.
* The single piece of evidence that would separate them: The original sensor/inspection record together with the approved engineering temperature limit.
* Who holds it: Engineering or the equipment/data owner.




## 6. What this file can and cannot support

This file can support basic data-quality checks and descriptive calculations, such as calculating the total units produced from valid records. It cannot support automatic shutdown, automatic maintenance scheduling, or safety action because the file does not contain verified failure outcomes or approved engineering limits. This connects to the Week 2 project boundary, where the data is intended to support a shift-handover prioritisation decision rather than an automatic operational decision.

* One calculation still safe: A descriptive total or average of `units_produced` after clearly identifying and excluding invalid records.
* One calculation not safe: Using the motor temperature value to trigger an automatic maintenance or safety decision.
