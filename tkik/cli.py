"""Demonstrate mechanics only; no genuine multi-model review is performed."""
from .core import Case, Review, Challenge

def main():
    case = Case("demo-001", "The changed procedure lowers error rate on held-out tasks.",
                "Held-out error rate is unchanged or higher.", "demonstrator")
    for lens in ("purist_logic", "pragmatism", "bridge"):
        case.add_review(Review(lens, f"SCRIPTED_{lens}_NOT_AN_INDEPENDENT_MODEL",
                               "Illustrative only", "Need actual held-out evidence"))
    case.ask(Challenge("c1", "purist_logic", "held-out error rate",
                       "Was the evaluation data separated before tuning?"))
    case.resolve("c1", "WAIVED")
    case.determine("REFINE", "Demonstration proves gating behavior only; hypothesis remains untested.")
    print(f"{case.case_id}: {case.verdict} — {case.rationale}")

if __name__ == "__main__":
    main()
