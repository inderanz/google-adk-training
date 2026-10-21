"""Apply an explicit release gate to a native ADK EvalSetResult JSON file."""
import argparse
import math
from pathlib import Path
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.eval_result import EvalSetResult
from google.adk.evaluation.eval_set import EvalSet


def require_passed(result: EvalSetResult, dataset: EvalSet, config: EvalConfig) -> None:
    # A release gate needs complete case coverage and every required metric, not merely a zero process exit.
    expected_cases = {case.eval_id for case in dataset.eval_cases}
    # A set removes duplicates. Check the original length so two scenarios with
    # the same ID cannot silently become one required result.
    if len(expected_cases) != len(dataset.eval_cases):
        raise ValueError("Duplicate case IDs in the dataset")
    if not config.criteria:
        raise ValueError("No evaluation criteria configured")
    thresholds = {}
    for name, criterion in config.criteria.items():
        threshold = criterion if isinstance(criterion, (float, int)) else criterion.threshold
        # NaN makes ordinary comparisons false, which could accidentally pass
        # a bad score. This teaching gate uses finite, higher-is-better metrics.
        if isinstance(threshold, bool) or not math.isfinite(threshold):
            raise ValueError(f"Invalid threshold: {name}")
        thresholds[name] = threshold
    if result.eval_set_id != dataset.eval_set_id:
        raise ValueError("Result belongs to another dataset")
    if not expected_cases or {case.eval_id for case in result.eval_case_results} != expected_cases:
        raise ValueError("Missing or unexpected evaluation cases")
    if len(result.eval_case_results) != len(expected_cases):
        raise ValueError("Duplicate evaluation cases; select one complete run")
    for case in result.eval_case_results:
        if case.final_eval_status.name != "PASSED":
            raise ValueError(f"Case did not pass: {case.eval_id}")
        metrics = {metric.metric_name: metric for metric in case.overall_eval_metric_results}
        # A dictionary would otherwise keep only the last duplicate metric,
        # possibly hiding a failure behind a later passing row.
        if len(metrics) != len(case.overall_eval_metric_results):
            raise ValueError(f"Duplicate metric results: {case.eval_id}")
        for name, threshold in thresholds.items():
            metric = metrics.get(name)
            if (metric is None or metric.eval_status.name != "PASSED" or metric.score is None
                    or not math.isfinite(metric.score) or metric.score < threshold):
                raise ValueError(f"Missing or failing metric: {case.eval_id}/{name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", help="Native ADK EvalSetResult JSON, not console text or CSV")
    args = parser.parse_args()
    result = EvalSetResult.model_validate_json(Path(args.result).read_text())
    dataset = EvalSet.model_validate_json(Path("eval/cases.evalset.json").read_text())
    config = EvalConfig.model_validate_json(Path("eval/eval_config.json").read_text())
    require_passed(result, dataset, config)
    print("All required cases and metrics passed the teaching release gate.")
