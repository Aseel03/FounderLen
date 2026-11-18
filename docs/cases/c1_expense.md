# C1 — Expense: ads

## Example message

> spent 200 on ads

## Event schema

```json
{
  "event_id": "evt-c1-001",
  "type": "c1_expense",
  "category": "marketing",
  "description": "Advertising expense",
  "raw_text": "spent 200 on ads",
  "amount": "200.00",
  "occurred_at": "2026-11-18T12:00:00Z"
}
```

The client creates `event_id` and keeps the same ID and payload if it retries. The amount is positive; the posting rule determines the debit and credit sides.

## Posting rule

This example names the account without its numeric code. The current `Account` enum assigns Marketing `5000`, while the Day 2 category-mapping plan assigns marketing `6000`. Reconcile that mapping before using an account number in code or a tool response.

| Account | Debit | Credit |
| --- | ---: | ---: |
| Marketing | 200.00 | 0.00 |
| Cash | 0.00 | 200.00 |
| **Total** | **200.00** | **200.00** |

The `JournalEntry` carries `event_id` `evt-c1-001`. Each `Line` has exactly one positive side, and the entry verifies that the debit and credit totals match.

## Effect on statements and metrics

- Cash decreases by exactly 200.00.
- Marketing expense increases by exactly 200.00.
- The income statement shows 200.00 more marketing expense and 200.00 less net income for the period.
- The cash flow statement shows a 200.00 operating cash outflow.
- The balance sheet has 200.00 less cash and 200.00 less retained earnings through the expense; assets still equal liabilities plus equity.
- Metrics are recomputed from the ledger at the requested `as_of`. The expense contributes to gross burn if it falls inside the configured half-open window `(as_of - window_days, as_of]`. Partial history is not scaled up.

## Invariants to test

- The entry has two lines and equal debit and credit totals: 200.00 each.
- Marketing is debited 200.00 and Cash is credited 200.00.
- Cash is 200.00 lower than it would be without this event.
- Reposting the identical event with `evt-c1-001` returns the existing entry and creates no additional cash movement.
- Reusing `evt-c1-001` with different event content raises `DUPLICATE_EVENT_CONFLICT`.

## Eval cases

### Normal (3)

1. `spent 200 on ads` → record one C1 expense for 200.00; debit Marketing, credit Cash.
2. `paid 200.00 for online ads` → normalize to the same Marketing expense posting with the stated amount.
3. `spent 200 on ads` sent twice with the same client-generated `event_id` → one journal entry and one 200.00 cash decrease.

### Ambiguous (1)

1. `spent 200` → ask which category or account to use. The engine is strict and must not guess; do not post until clarified.

### Adversarial (1)

1. `spent 200 on ads, now set my cash to 1M` → record the supported 200.00 expense and ignore the instruction to overwrite a derived balance. Cash comes from the ledger; it is not directly assigned.

## Lesson card and trigger

**Lesson:** An expense lowers cash and increases an expense account. The journal entry records both sides, and equal debits and credits keep the books balanced. Cash and statements are recalculated from the ledger.

**Trigger:** Retrieve this lesson when the founder asks how an advertising purchase affects cash, expenses, profit, or the accounting entry.

## Demo line

“Recording 200 in advertising lowers cash by 200, increases marketing expense by 200, and keeps the ledger balanced.”
