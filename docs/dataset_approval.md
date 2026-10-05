# Week 3 Dataset Approval

## The decision, in one sentence

> This file **may** be used to support descriptive data-quality analysis and shift-handover prioritisation,
> but **may not** be used to make automatic shutdown, automatic maintenance, or safety decisions,
> on condition that the known data-quality issues are clearly documented and invalid records are not used without review,
> and the decision is revisited when verified failure outcomes, approved engineering limits, or a more representative dataset become available.

Decision: **Approve with conditions**

## Why this decision and not the one next to it

The file does not pass all validation checks, but the identified problems can be documented and the permitted use is limited to descriptive analysis and shift-handover prioritisation. It is therefore not appropriate to reject the file completely, but it is also not safe to approve it for automatic operational, maintenance, or safety decisions.

## Conditions

| Condition                                                                           | Owner                     | Evidence that closes it                  | Review trigger                      |
| ----------------------------------------------------------------------------------- | ------------------------- | ---------------------------------------- | ----------------------------------- |
| Known data-quality issues must be documented before use                             | Data owner                | Updated data-quality record              | New data release                    |
| Invalid or questionable records must be reviewed before calculations                | Data analyst / data owner | Reviewed records and documented decision | Before operational use              |
| Approved engineering limits are required for safety-related interpretation          | Engineering               | Approved engineering limits              | Engineering limits become available |
| Verified failure or inspection outcomes are required for predictive operational use | Data owner / operations   | Historical failure or inspection rec     |                                     |
