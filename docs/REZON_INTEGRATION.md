# Four-source Rezon integration proposal (not yet live)

The desired execution graph is **ChatGPT Chair + Lappy + VN1 + VN2**, communicating on a shared proposition but submitting individually attributable challenge findings. Rezon, if available, should transport messages and receipts, not secretly decide truth. The bridge adapter must be developed against fresh Rezon schemas rather than guessed endpoint names.

## Proposed minimal message contract

```json
{
  "schema": "TKIK_REVIEW_REQUEST_V1",
  "case_id": "case-123",
  "claim_version": 1,
  "input_sha256": "<64 hex characters>",
  "lens": "purist_logic",
  "reviewer_host": "vn1",
  "reviewer_runtime": "<observed runtime identifier>",
  "attempt_id": "<unique durable ID>",
  "question": "<single precise adversarial question>",
  "evidence_refs": []
}
```

Treat REQUESTED/RESERVED, DISPATCHED, COMPLETED and OUTCOME_UNKNOWN as **distinct states**; a timeout after dispatch does not prove the model did not run. The receiving host should append a receipt with observed model/runtime, timestamps, immutable challenge digest, response digest and actual provider/host metadata. Reused context is recorded as contamination risk.

## Admission gate

A review is independent only when actual distinct runtime invocations can be checked and relevant shared inputs or dependency coupling are disclosed. Missing receipts remain MISSING. A scripted example cannot count. The Chair may synthesize disagreements but must show each review unchanged and distinguish external output from Chair inference.

## Return protocol

Each reviewer returns: `case_id`, frozen claim/version/hash, target, strongest falsifier, strongest competing explanation, evidence cited, risks of confirmation bias, suggested decisive test, confidence/limitations, receipt state, and explicit dissent. No merge/deploy/training action follows automatically. Model-to-model dialogue can iterate, but any changed claim must be versioned and recirculated, not silently moved mid-round.

## Next engineering boundary

Inspect actual Rezon interfaces and existing four-node transport authorization, then implement an adapter with end-to-end receipts and fault-injection tests (duplicate dispatch, timeouts, substituted model, inconsistent input hashes and unreachable host). Until that is done, **no live four-host Socratic dialogue is claimed**.
