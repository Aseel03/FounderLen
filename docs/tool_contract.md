# FounderLens tool contract

```yaml
contract_version: 1
```

Tools marked `write` may append to the ledger. Tools marked `read` return information without changing it. Every tool uses one of the shared response envelopes below.

## Shared response envelopes

Success:

```json
{"ok": true, "data": {}}
```

Error:

```json
{"ok": false, "error": {"code": "INVALID_INPUT", "message": "The amount must be greater than zero."}}
```

Use `ok` to distinguish success from failure. On success, `data` contains the tool’s result. On failure, `error.code` is a stable value for program logic and `error.message` explains the problem.

## Shared error codes

| Code | Meaning |
| --- | --- |
| `UNSUPPORTED_EVENT_TYPE` | The event type has no registered posting rule. |
| `INVALID_INPUT` | Input is malformed or violates a model or tool rule, such as a non-positive amount, naive timestamp, invalid debit/credit line, or invalid date range. |
| `UNKNOWN_CATEGORY` | An expense category is not in the category-to-account configuration, so the engine cannot choose its expense account. |
| `DUPLICATE_EVENT_CONFLICT` | An `event_id` already belongs to different event content. Reposting the identical event returns its existing entry; reusing the ID for different content is an error. |

## How the contract connects to the engine

`Event` describes what happened. A posting rule converts it into accounting `Line`s. `JournalEntry` groups those lines under the `event_id` and checks that total debits equal total credits. `MetricsSnapshot` holds calculated cash, burn, runway, confidence, stage, and data coverage.

The engine treats the journal as append-only: entries are not edited or deleted. Statements and metrics are calculated from that history rather than stored as separate ledger entries. Model tests cover the data rules; tool tests should check that failures use this contract’s error envelope.

## `record_event`

- **Scope:** `write`
- **Input:** `event_id`, `type`, `category`, `description`, `raw_text`, positive `amount`, and timezone-aware `occurred_at`. These match the current `Event` model.
- **Output:** The normalized event and the resulting journal entry.
- **Possible errors:** `INVALID_INPUT`, `UNSUPPORTED_EVENT_TYPE`, `UNKNOWN_CATEGORY`, `DUPLICATE_EVENT_CONFLICT`.
- **ID and retries:** The client generates `event_id` once and reuses it with the same payload when retrying. An identical repost returns the existing entry, so recording twice creates one entry. The same ID with different content returns `DUPLICATE_EVENT_CONFLICT`.
- **Account mapping note:** The example uses the account name `Marketing`, not an account number. The current `Account` enum assigns Marketing `5000`, while the Day 2 category-mapping plan assigns marketing `6000`. Reconcile that mapping before exposing account numbers in the tool response.
- **Example call:**

```json
{"event_id":"evt-001","type":"c1_expense","category":"marketing","description":"Ads","raw_text":"spent 200 on ads","amount":"200.00","occurred_at":"2026-11-18T12:00:00Z"}
```

- **Example response:**

```json
{"ok":true,"data":{"event":{"event_id":"evt-001","type":"c1_expense","category":"marketing","description":"Ads","raw_text":"spent 200 on ads","amount":"200.00","occurred_at":"2026-11-18T12:00:00Z"},"journal_entry":{"event_id":"evt-001","lines":[{"account":"Marketing","debit":"200.00","credit":"0.00"},{"account":"Cash","debit":"0.00","credit":"200.00"}]}}}
```

## `get_statements`

- **Scope:** `read`
- **Input:** `as_of` for balance reports, and `start` and `end` for period reports. All timestamps are timezone-aware UTC instants.
- **Output:** `trial_balance`, `balance_sheet`, `income_statement`, and `cash_flow`.
- **Possible errors:** `INVALID_INPUT`.
- **Example context:** Assume the ledger is empty, so all statement totals are zero.
- **Example call:**

```json
{"as_of":"2026-10-20T00:00:00Z","start":"2026-10-01T00:00:00Z","end":"2026-10-20T00:00:00Z"}
```

- **Example response:**

```json
{"ok":true,"data":{"trial_balance":[],"balance_sheet":{"assets":"0.00","liabilities":"0.00","equity":"0.00"},"income_statement":{"revenue":"0.00","expenses":"0.00","net_income":"0.00"},"cash_flow":{"operating":"0.00","investing":"0.00","financing":"0.00","ending_cash":"0.00"}}}
```

## `get_metrics`

- **Scope:** `read`
- **Input:** `as_of`, a timezone-aware timestamp. The engine receives this value and does not read the clock.
- **Output:** A metrics snapshot containing `as_of`, `cash`, `net_burn_monthly`, `runway_months`, `confidence`, `stage`, and `data_days`. The Day 2 plan renames the current Day 1 model field `net_burn_30d` to `net_burn_monthly`. Runway is undefined (`null`) when net burn is zero or negative. Partial history is reported raw and lowers confidence; it is never scaled up.
- **Possible errors:** `INVALID_INPUT`.
- **Example context:** This shows the Day 2 golden scenario at Oct 20: setup capital on Oct 1, then the planned expenses, revenue, and COGS events through Oct 18.
- **Example call:**

```json
{"as_of":"2026-10-20T00:00:00Z"}
```

- **Example response:**

```json
{"ok":true,"data":{"as_of":"2026-10-20T00:00:00Z","cash":"4900.00","net_burn_monthly":"100.00","runway_months":"49.0","confidence":"HIGH","stage":"EARLY_REVENUE","data_days":19}}
```

## `list_events`

- **Scope:** `read`
- **Input:** No required fields; `{}` lists all recorded events.
- **Output:** `events`, a collection of normalized events with their `event_id`s.
- **Possible errors:** `INVALID_INPUT` if optional filters are added and invalid; the example call uses no filters.
- **Example call:**

```json
{}
```

- **Example response:**

```json
{"ok":true,"data":{"events":[{"event_id":"evt-001","type":"c1_expense","category":"marketing","description":"Ads","raw_text":"spent 200 on ads","amount":"200.00","occurred_at":"2026-10-03T00:00:00Z"}]}}
```

## `simulate`

- **Scope:** `read`
- **Input:** A `kind` and the parameters needed for that scenario. For example, `recurring_monthly_cost` takes an `amount`. New scenarios can be added as new `kind` values without changing the shared tool envelope.
- **Output:** The selected `kind`, the parameters used, and the hypothetical result. Simulation does not append to or change the ledger.
- **Possible errors:** `INVALID_INPUT` for malformed parameters or an unsupported `kind`.
- **Example call:**

```json
{"kind":"recurring_monthly_cost","amount":"800.00"}
```

- **Example response:**

```json
{"ok":true,"data":{"kind":"recurring_monthly_cost","parameters":{"amount":"800.00"},"result":{"net_burn_monthly_delta":"800.00"}}}
```

## `retrieve_lessons`

- **Scope:** `read`
- **Input:** Exactly one of `concept` or `trigger`. Providing neither or both is `INVALID_INPUT`.
- **Output:** `lessons`, a collection of matching lesson cards. Each card has a `lesson_id`, `concept`, `trigger`, and `lesson`.
- **Possible errors:** `INVALID_INPUT`.
- **Example call:**

```json
{"trigger":"cash_runway_question"}
```

- **Example response:**

```json
{"ok":true,"data":{"lessons":[{"lesson_id":"expense-cash-flow","concept":"expense_posting","trigger":"cash_runway_question","lesson":"An expense lowers cash and increases an expense account; its journal entry must balance."}]}}
```

## `get_knowledge_state`

- **Scope:** `read`
- **Input:** No required fields; `{}` requests the current known state.
- **Output:** `as_of` and a `state` summary of financial and business facts derived from the ledger. This is a view of current knowledge, not a stored snapshot.
- **Possible errors:** `INVALID_INPUT` if optional filters are added and invalid; the example call uses no filters.
- **Example call:**

```json
{}
```

- **Example response:**

```json
{"ok":true,"data":{"as_of":"2026-10-20T00:00:00Z","state":{"cash":"4900.00","net_burn_monthly":"100.00","runway_months":"49.0","confidence":"HIGH","stage":"EARLY_REVENUE"}}}
```
