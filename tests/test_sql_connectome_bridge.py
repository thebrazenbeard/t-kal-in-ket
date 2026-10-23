"""Bounded read-only SQL Connectome V2 qualification evidence adapter tests.

These caller-built payloads are *not* independently attested provider results.
"""
import copy
import hashlib
import json
import unittest

from tkik.core import Case
from tkik.sql_connectome_bridge import SQLQualificationError, assess_translation_qualification


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    ensure_ascii=False, separators=(",", ":"),
                                    default=str).encode()).hexdigest()


def signed_body(kind, subject, timestamp="2026-10-23T00:00:00+00:00"):
    body = {"schema": "SQL_CONNECTOME_RECEIPT_V1",
            "kind": kind, "issued_at": timestamp, "subject": subject}
    return {**body, "receipt_digest": digest(body)}


def sample(status="PASS"):
    translation = {
        "catalog_digest": "catalog-immutable-snapshot",
        "source": {"ir": {"nodes": [{"kind": "projection"}]}},
        "target_parse": {"ir": {"nodes": [{"kind": "projection"}]}},
        "target_sql": "SELECT 1",
        "plan": {"rewrites": []},
        "expression_semantics": {"risk_count": 0},
        "type_semantics": {"risk_count": 0},
        "combined_fidelity": "EXACT",
        "fidelity_components": {
            "capability": "EXACT", "expression_semantics": "EXACT", "types": "EXACT"
        },
    }
    engine = {
        "validation": {"status": status},
        "runtime": {"identity_digest": "runtime-tested-not-attested"},
        "receipt": signed_body("ENGINE_VALIDATION", {"sql": "SELECT 1"}),
    }
    semantic_digest = digest({
        "plan": translation["plan"],
        "expression_semantics": translation["expression_semantics"],
        "type_semantics": translation["type_semantics"],
        "combined_fidelity": translation["combined_fidelity"],
    })
    qualification = {
        "status": status,
        "source_dialect": "mysql", "target_dialect": "postgresql",
        "capability_fidelity": "EXACT", "expression_semantic_fidelity": "EXACT",
        "type_fidelity": "EXACT", "translation_fidelity": "EXACT",
        "translation_fidelity_scope": "CAPABILITY_EXPRESSION_AND_TYPE_SEMANTICS",
        "expression_semantic_risk_count": 0, "type_semantic_risk_count": 0,
        "source_ir_digest": digest(translation["source"]["ir"]),
        "target_ir_digest": digest(translation["target_parse"]["ir"]),
        "semantic_evidence_digest": semantic_digest,
        "engine_validation_receipt_digest": engine["receipt"]["receipt_digest"],
        "behavioral_equivalence": "NOT_ESTABLISHED",
        "query_executed": False, "authority": "VALIDATION_ONLY",
    }
    subject = {
        "catalog_digest": translation["catalog_digest"],
        "source_dialect": "mysql", "target_dialect": "postgresql",
        "source_sql_digest": digest("SELECT 1"),  # original SQL unavailable from export
        "target_sql_digest": digest(translation["target_sql"]),
        "source_ir_digest": qualification["source_ir_digest"],
        "target_ir_digest": qualification["target_ir_digest"],
        "semantic_evidence_digest": semantic_digest,
        "capability_fidelity": qualification["capability_fidelity"],
        "expression_semantic_fidelity": qualification["expression_semantic_fidelity"],
        "type_fidelity": qualification["type_fidelity"],
        "translation_fidelity": qualification["translation_fidelity"],
        "translation_fidelity_scope": qualification["translation_fidelity_scope"],
        "expression_semantic_risk_count": 0, "type_semantic_risk_count": 0,
        "target_runtime_identity_digest": engine["runtime"]["identity_digest"],
        "engine_validation_status": status,
        "engine_validation_receipt_digest": engine["receipt"]["receipt_digest"],
    }
    return {
        "schema": "SQL_CONNECTOME_TRANSLATION_QUALIFICATION_V2",
        "qualification": qualification, "translation": translation,
        "engine_validation": engine,
        "receipt": signed_body("TRANSLATION_QUALIFICATION", subject),
    }


class SQLQualificationBridgeTests(unittest.TestCase):
    def test_attaches_limited_evidence_not_a_verified_sql_oracle(self):
        payload = sample()
        assessment = assess_translation_qualification(payload)
        self.assertEqual(assessment.status, "PASS")
        self.assertFalse(assessment.origin_verified)
        self.assertFalse(assessment.behavioral_equivalence_established)
        self.assertFalse(assessment.execution_authorized)
        evidence = assessment.as_evidence()
        self.assertEqual(evidence.identifier, "sql-connectome:" + payload["receipt"]["receipt_digest"])
        self.assertIn("UNVERIFIED_ORIGIN", evidence.reliability)
        self.assertNotIn("SELECT 1", evidence.claim)
        self.assertIn("NOT_ESTABLISHED", evidence.uncertainty)
        case = Case("case-sql", "SQL dialects are interchangeable", "A mismatch", "challenger")
        case.add_evidence(evidence)
        self.assertEqual(len(case.evidence), 1)
        with self.assertRaises(Exception):
            case.determine("SUSTAIN", "Receipt looked official")

    def test_mutated_receipt_digest_is_rejected(self):
        payload = sample()
        payload["receipt"]["subject"]["translation_fidelity"] = "LOSSY"
        with self.assertRaises(SQLQualificationError):
            assess_translation_qualification(payload)

    def test_recomputed_outer_receipt_cannot_launder_changed_semantics(self):
        payload = sample()
        payload["translation"]["expression_semantics"]["risk_count"] = 9
        payload["receipt"] = signed_body(
            "TRANSLATION_QUALIFICATION", payload["receipt"]["subject"]
        )
        with self.assertRaises(SQLQualificationError):
            assess_translation_qualification(payload)

    def test_fake_nested_engine_receipt_rejected(self):
        payload = sample()
        payload["engine_validation"]["receipt"]["subject"]["sql"] = "DROP TABLE data"
        with self.assertRaises(SQLQualificationError):
            assess_translation_qualification(payload)

    def test_laundered_pass_and_source_ir_rejected(self):
        payload = sample("FAIL")
        payload["qualification"]["status"] = "PASS"
        with self.assertRaises(SQLQualificationError):
            assess_translation_qualification(payload)
        payload = sample()
        payload["translation"]["source"]["ir"]["nodes"].append({"kind": "different"})
        with self.assertRaises(SQLQualificationError):
            assess_translation_qualification(payload)

    def test_receipt_must_never_assert_query_execution_or_equivalence(self):
        for key, value in (("query_executed", True),
                           ("behavioral_equivalence", "ESTABLISHED"),
                           ("authority", "EXECUTION_ALLOWED")):
            payload = sample()
            payload["qualification"][key] = value
            with self.subTest(key=key), self.assertRaises(SQLQualificationError):
                assess_translation_qualification(payload)

    def test_failure_remains_failure_and_no_execution_authority(self):
        x = assess_translation_qualification(sample("FAIL"))
        self.assertEqual(x.status, "FAIL")
        self.assertFalse(x.execution_authorized)
        self.assertIn("FAIL", x.as_evidence().claim)

    def test_invalid_shapes_are_rejected_without_promoting_evidence(self):
        for bad in (None, {}, {"schema": "invented"}, ["list"]):
            with self.subTest(bad=bad), self.assertRaises(SQLQualificationError):
                assess_translation_qualification(bad)
