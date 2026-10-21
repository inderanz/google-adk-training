"""Read an actual deployed pack back from GCS using its exact saved scope/versions."""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
from google.adk.artifacts import GcsArtifactService


async def verify(report_path: str) -> dict:
    # Read the exact referenced objects using a fresh provider, then compare bytes and scope.
    report = json.loads(Path(report_path).read_text())
    case = next(case for case in report["cases"] if case["id"] == "pack")
    outputs = []
    for event in case["events"]:
        for part in (event.get("content") or {}).get("parts", []):
            response = part.get("function_response") or part.get("functionResponse")
            if response and response["name"] == "create_review_pack":
                outputs.append(response["response"])
    outcome = next(value for value in outputs if value.get("status") == "prepared_for_human_review")
    # A new client/process reads the data; nothing relies on the earlier Runner.
    service = GcsArtifactService(bucket_name=os.environ["ARTIFACT_BUCKET"])
    scope = {"app_name": "bank_review", "user_id": case["user_id"], "session_id": case["session_id"]}
    manifest_part = await service.load_artifact(
        **scope, filename="CASE-001-manifest.json", version=outcome["manifest_version"])
    if not manifest_part or not manifest_part.inline_data:
        raise AssertionError("Saved manifest could not be read back")
    manifest = json.loads(manifest_part.inline_data.data)
    source = await service.load_artifact(**scope, **{
        key: manifest["source"][key] for key in ("filename", "version")})
    saved_report = await service.load_artifact(**scope, **manifest["report"])
    if not source or not source.inline_data or not saved_report or not saved_report.inline_data:
        raise AssertionError("An exact referenced artifact version is missing")
    digest = hashlib.sha256(source.inline_data.data).hexdigest()
    if digest != manifest["source"]["sha256"]:
        raise AssertionError("Source digest does not match the manifest")
    if manifest["report"] != outcome["report"]:
        raise AssertionError("Returned report and saved manifest disagree")
    if b"ownership_register" not in saved_report.inline_data.data:
        raise AssertionError("Fixture report does not contain the expected missing item")
    return {"status": "verified_from_gcs", "source": manifest["source"], "report": manifest["report"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", nargs="?", default="deployment-results.json")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(verify(args.report)), indent=2))
