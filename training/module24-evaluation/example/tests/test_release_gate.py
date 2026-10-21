"""Malformed evidence must not satisfy a release gate; no model calls are made."""
from pathlib import Path
import unittest
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.eval_result import EvalSetResult
from google.adk.evaluation.eval_metrics import EvalStatus
from google.adk.evaluation.eval_set import EvalSet
from check_eval import require_passed


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.dataset = EvalSet.model_validate_json(Path("eval/cases.evalset.json").read_text())
        self.config = EvalConfig.model_validate_json(Path("eval/eval_config.json").read_text())
        # Deliberately fabricated passing scores isolate the gate's logic.
        # They are not Gemini results and must never be reported as live quality.
        self.result = EvalSetResult.model_validate({
            "eval_set_id": self.dataset.eval_set_id, "eval_set_result_id": "gate-fixture",
            "eval_case_results": [{
                "eval_id": case.eval_id, "final_eval_status": EvalStatus.PASSED, "session_id": "fixture",
                "eval_metric_result_per_invocation": [],
                "overall_eval_metric_results": [{
                    "metric_name": name, "score": 1.0, "eval_status": EvalStatus.PASSED
                } for name in self.config.criteria],
            } for case in self.dataset.eval_cases],
        })

    def test_complete_unambiguous_result_passes(self):
        require_passed(self.result, self.dataset, self.config)

    def test_empty_criteria_cannot_prove_quality(self):
        self.config.criteria = {}
        with self.assertRaisesRegex(ValueError, "criteria"):
            require_passed(self.result, self.dataset, self.config)

    def test_duplicate_dataset_ids_cannot_hide_a_missing_scenario(self):
        self.dataset.eval_cases.append(self.dataset.eval_cases[0].model_copy(deep=True))
        with self.assertRaisesRegex(ValueError, "dataset"):
            require_passed(self.result, self.dataset, self.config)

    def test_duplicate_metrics_cannot_hide_failure_in_either_order(self):
        for failed_first in (True, False):
            with self.subTest(failed_first=failed_first):
                candidate = self.result.model_copy(deep=True)
                metrics = candidate.eval_case_results[0].overall_eval_metric_results
                failed = metrics[0].model_copy(update={"score": 0.0})
                metrics.insert(0 if failed_first else len(metrics), failed)
                with self.assertRaisesRegex(ValueError, "Duplicate metric"):
                    require_passed(candidate, self.dataset, self.config)

    def test_nonfinite_threshold_cannot_disable_comparison(self):
        name = next(iter(self.config.criteria))
        self.config.criteria[name] = float("nan")
        with self.assertRaisesRegex(ValueError, "threshold"):
            require_passed(self.result, self.dataset, self.config)
