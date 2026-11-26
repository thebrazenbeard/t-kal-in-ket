# Optional local model advocate

This repository owns the experimental advisory interface and model binding. It is
not an independent verdict authority, a replacement for the human/peer advocate,
or evidence of a persistent identity or independent mind.

Upstream: [cross-encoder/nli-deberta-v3-small](https://huggingface.co/cross-encoder/nli-deberta-v3-small)
(141.9M parameters, Apache-2.0), pinned revision
`fa2804872c3b4bd748f38c0185cc85775361e735`.
The upstream `model.safetensors` is about 568 MB and is SHA-256 pinned in
`tkik/advocate.py`. Weights remain an upstream artifact rather than being
duplicated in Git. Preserve upstream license and attribution in any distribution.

On a separately designated inference worker only, provision compatible CPU
PyTorch and Transformers, and retrieve the exact revision's safetensors,
configuration and tokenizer files from the upstream repository. Verify the
snapshot provenance and dependency versions before use. The loader verifies the
exact seven-file snapshot inventory and all seven SHA-256 digests before model
imports (local download metadata directory `.cache` is ignored). This is a
byte-integrity check, not an authenticated worker receipt or protection from
concurrent local modification. Use an isolated, stable read-only model directory. No model downloads or model imports happen at
module import. No automatic network calls, training, serving or startup tasks
are included. No private deliberations are sent to the Hub.

Run from a clean source installation on the designated worker:

```sh
python -m tkik.advocate --model-dir /path/to/pinned/snapshot --worker-hostname WORKER_HOST < pair.json
```

Input: a JSON object with string fields `premise` and `claim`. Select relevant
evidence excerpts; long pairs are rejected, not silently truncated. The
hostname check prevents accidental misrouting, not authenticated placement.
Output is a textual relationship hint, with input digests, uncalibrated scores
and explicit NONE authority. The initial thresholds are exploratory, not
calibrated. Neutral is not falsity; entailment is not truth. A high-confidence
contradiction is a request for closer examination, not a verdict.

Before behavioral activation, compare this with existing deterministic checks
and the ordinary advocate on novel synthetic cases, including false accusations,
missing evidence, scope changes and order/loyalty perturbations. Evaluate
incremental detection, false positives, abstention and resource cost. Keep
existing decision procedures and real defense opportunities. Retain or remove
the experiment according to evidence. Boundary tests use synthetic scores and inert snapshot files; they do not
establish model effectiveness or worker capacity. One observed CPU setup used
Python 3.13.15, torch 2.8.0+cpu, transformers 4.57.1, tokenizers 0.22.2,
safetensors 0.8.0, sentencepiece 0.2.3 and huggingface-hub 0.36.2; this is an
observed configuration, not a complete dependency lock or recommendation to
install outdated packages. Verify the actual worker's dependencies and keep
behavioral qualification separate.
