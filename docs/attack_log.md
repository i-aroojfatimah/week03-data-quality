# Week 3 Attack Log

Validation is never finished. The only way to find out what your checks miss is to have someone try to get past them.

## The round

I completed the attack exercise independently by testing whether operationally unrealistic rows could pass my validator. The raw dataset was not modified; attack rows were treated as test data.

## My attacks on my validator

| # | The row I wrote                                                                    | Why it is nonsense in a real plant                                                                               | Why my checks accepted it                                                               |
| - | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| 1 | A row with an extremely high but non-negative `units_produced` value               | The production amount would be operationally unrealistic for one hour.                                           | There is no approved maximum production limit in the validator.                         |
| 2 | A row with a very large positive `energy_kwh` value compared with `units_produced` | The energy consumption would be operationally suspicious compared with the output.                               | The `positive_energy` check only checks that energy is greater than zero.               |
| 3 | A row with an unusual combination of production, energy and motor temperature      | The combination may be operationally unrealistic even though each individual value is within the written checks. | The validator does not contain a general relationship check between these measurements. |

## Attacks that got past my validator

| # | Their row                                                                   | Why my checks accepted it                                                | The check I would add                                                        |
| - | --------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| 1 | An extremely high but non-negative production value                         | No approved maximum production limit is defined.                         | Add a production-rate range check when an approved limit is available.       |
| 2 | A very large positive energy value                                          | `positive_energy` only checks that energy is greater than zero.          | Add an energy-per-unit plausibility check using an approved reference range. |
| 3 | An unusual but individually valid combination of production and temperature | The current checks do not test relationships between these measurements. | Add an approved operational relationship/plausibility check.                 |

## The check I actually added

No additional operational-limit check was added because the dataset does not provide approved engineering limits for production rate or energy-per-unit. Adding an invented limit would create a false validation rule.

The current validator already contains checks for timestamps, completeness, uniqueness, known lines, positive energy, rejected units, downtime, motor temperature review, shift/hour consistency and line-hour coverage.

## What this round changed about your approval decision

The attack exercise confirmed that passing data-quality checks does not prove that every operational value is realistic. The dataset should therefore remain limited to descriptive analysis and shift-handover prioritisation, and should not be used for automatic safety or maintenance decisions.
