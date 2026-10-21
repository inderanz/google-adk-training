import unittest
from pathlib import Path
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.eval_result import EvalSetResult
from google.adk.evaluation.eval_metrics import EvalStatus
from google.adk.evaluation.eval_set import EvalSet
from bank_review.agent import read_case, build_app
from check_eval import require_passed
from support import ScriptedModel, call, text, invoke, results


class EvaluationTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_runner_returns_fixture(self):
        model = ScriptedModel(replies=[call("read_case", case_id="CASE-001"), text("Fixture answer")])
        events, _, _ = await invoke(build_app(model))
        self.assertEqual(results(events)[0]["missing_documents"], ["ownership_register"])
        self.assertEqual(read_case("CASE-999"), {"status": "not_found"})

    def test_native_dataset_and_config(self):
        dataset = EvalSet.model_validate_json(Path("eval/cases.evalset.json").read_text())
        config = EvalConfig.model_validate_json(Path("eval/eval_config.json").read_text())
        self.assertEqual(len(dataset.eval_cases), 4)
        self.assertTrue(config.criteria)

    def test_release_gate_rejects_missing_results(self):
        dataset = EvalSet.model_validate_json(Path("eval/cases.evalset.json").read_text())
        config = EvalConfig.model_validate_json(Path("eval/eval_config.json").read_text())
        result = EvalSetResult(eval_set_id=dataset.eval_set_id, eval_set_result_id="fixture")
        with self.assertRaisesRegex(ValueError, "Missing"):
            require_passed(result, dataset, config)

    def test_release_gate_rejects_failed_or_unevaluated_metric(self):
        dataset = EvalSet.model_validate_json(Path("eval/cases.evalset.json").read_text())
        config = EvalConfig.model_validate_json(Path("eval/eval_config.json").read_text())
        rows = [{"eval_id": case.eval_id, "final_eval_status": EvalStatus.PASSED, "session_id": "fixture",
                 "eval_metric_result_per_invocation": [],
                 "overall_eval_metric_results": [{"metric_name": name, "score": 1.0,
                     "eval_status": EvalStatus.PASSED} for name in config.criteria]} for case in dataset.eval_cases]
        result = EvalSetResult.model_validate({"eval_set_id": dataset.eval_set_id,
            "eval_set_result_id": "fixture", "eval_case_results": rows})
        require_passed(result, dataset, config)
        for score in [None, 0.0, float("nan")]:
            candidate = result.model_copy(deep=True)
            candidate.eval_case_results[0].overall_eval_metric_results[0].score = score
            with self.assertRaisesRegex(ValueError, "Missing or failing metric"):
                require_passed(candidate, dataset, config)
