"""Optional local NLI advocate: advisory evidence, never a verdict."""
from __future__ import annotations

import argparse
import hashlib
from itertools import islice
import json
import math
from pathlib import Path
import socket
import sys

MODEL_ID = "cross-encoder/nli-deberta-v3-small"
MODEL_REVISION = "fa2804872c3b4bd748f38c0185cc85775361e735"
WEIGHTS_SHA256 = "ebc79588dd73ccfb6a3f6078519cfbf512c5305384c5ea1845bc71cd32216e86"
LABELS = ("contradiction", "entailment", "neutral")


def advisory(premise, claim, scorer):
    """Score a supplied pair; keep evidence identity and uncertainty explicit."""
    if any(not isinstance(s, str) or not s.strip() or len(s) > 4000
           for s in (premise, claim)):
        raise ValueError("nonempty premise and claim, each at most 4000 characters")
    logits = tuple(islice(scorer(premise, claim), 4))
    if len(logits) != 3 or any(type(x) not in (int, float) or not math.isfinite(x) for x in logits):
        raise ValueError("expected three finite NLI logits")
    high = max(logits)
    exp = [math.exp(x - high) for x in logits]
    scores = [x / sum(exp) for x in exp]
    order = sorted(range(3), key=lambda i: scores[i], reverse=True)
    i, j = order[:2]
    label = LABELS[i]
    action = "ABSTAIN"
    if scores[i] >= 0.80 and scores[i] - scores[j] >= 0.20:
        action = {"contradiction": "REVIEW_POSSIBLE_CONTRADICTION",
                  "entailment": "TEXTUAL_SUPPORT_ONLY",
                  "neutral": "INSUFFICIENT_TEXTUAL_SUPPORT"}[label]
    digest = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
    return {"configured_model": MODEL_ID, "configured_revision": MODEL_REVISION,
            "execution_attested": False,
            "premise_sha256": digest(premise), "claim_sha256": digest(claim),
            "label": None if action == "ABSTAIN" else label, "uncalibrated_scores": dict(zip(LABELS, scores)),
            "advice": action, "authority": "NONE", "effect": False}


def require_worker(expected_hostname):
    if not expected_hostname or socket.gethostname().casefold() != expected_hostname.casefold():
        raise RuntimeError("explicit designated worker hostname does not match")


def verify_weights(model_dir):
    path = Path(model_dir) / "model.safetensors"
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != WEIGHTS_SHA256:
        raise ValueError("model weights SHA256 does not match pinned artifact")


def local_scorer(model_dir, worker_hostname):
    """No download, remote code, pickle weights, or model load at import time."""
    require_worker(worker_hostname)
    verify_weights(model_dir)
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    tokenizer = AutoTokenizer.from_pretrained(
        str(model_dir), local_files_only=True, trust_remote_code=False)
    model = AutoModelForSequenceClassification.from_pretrained(
        str(model_dir), local_files_only=True, trust_remote_code=False,
        use_safetensors=True).to("cpu").eval()
    actual = tuple(str(model.config.id2label.get(i, "")).lower() for i in range(3))
    if model.config.num_labels != 3 or actual != LABELS:
        raise ValueError("unexpected model label mapping")
    torch.set_num_threads(1)

    def score(premise, claim):
        features = tokenizer(premise, claim, return_tensors="pt", truncation=False)
        if features["input_ids"].shape[-1] > 512:
            raise ValueError("pair exceeds 512 tokens; select narrower evidence")
        with torch.inference_mode():
            return model(**features).logits[0].tolist()
    return score


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate input key")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--worker-hostname", required=True)
    args = parser.parse_args()
    try:
        frame = sys.stdin.read(32769)
        if len(frame) > 32768:
            raise ValueError("input frame exceeds limit")
        payload = json.loads(frame, object_pairs_hook=_unique_pairs)
        if not isinstance(payload, dict) or set(payload) != {"premise", "claim"}:
            raise ValueError("expected premise and claim")
        for key in ("premise", "claim"):
            if not isinstance(payload[key], str) or not payload[key].strip() or len(payload[key]) > 4000:
                raise ValueError("invalid or oversized evidence")
        result = advisory(payload["premise"], payload["claim"],
                          local_scorer(args.model_dir, args.worker_hostname))
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        print("Advocate unavailable: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps(result, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
