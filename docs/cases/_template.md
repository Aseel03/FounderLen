# Case template

## Example message

Describe the user message that starts this case.

## Event schema

Record the normalized event fields: `event_id`, `type`, `category`, `description`, `raw_text`, `amount`, and `occurred_at`. The client generates `event_id` and reuses it on retries.

## Posting rule

State the exact debit and credit lines. They must balance.

## Effect on statements and metrics

Describe the expected change to the relevant statements and metrics. Derived reports come from the append-only journal; they are not stored as separate ledger entries.

## Invariants to test

List the properties that must always hold, including balance and idempotency where relevant.

## Eval cases

### Normal (3)

1. 
2. 
3. 

### Ambiguous (1)

1. 

### Adversarial (1)

1. 

## Lesson card and trigger

Write the lesson and the phrase, question, or condition that should retrieve it.

## Demo line

Write one concise line suitable for demonstrating the case.