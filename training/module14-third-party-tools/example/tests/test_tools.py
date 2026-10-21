"""Exercise boundaries and SDK contracts without network access."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta
import json
import os
import unittest
from unittest.mock import patch

from google.adk import Agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models.llm_request import LlmRequest
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool, ToolContext
from google.api_core.exceptions import Forbidden
from google.auth.exceptions import DefaultCredentialsError

from corporate_research import repository, tools


def sample_record() -> dict[str, str]:
    return {
        "company_id": "ACME-001",
        "company_name": "Acme Robotics (fictional)",
        "summary": "Fictional training company founded in 2012.",
        "source_uri": "training-fixture:ACME-001",
        "reviewed_on": datetime.now(UTC).date().isoformat(),
    }


class ToolTests(unittest.TestCase):
    def run_with_record(self, record):
        with patch.object(tools, "fetch_profile", return_value=record):
            return tools.get_company_profile("ACME-001")

    def test_invalid_inputs_never_query(self):
        for value in ("", "acme-001", " ACME-001 ", "X" * 33, "A;DROP TABLE x", None, 12):
            with self.subTest(value=value):
                with patch.object(tools, "fetch_profile") as fetch:
                    result = tools.get_company_profile(value)
                    self.assertEqual(result["status"], "invalid_input")
                    fetch.assert_not_called()

    def test_valid_boundaries(self):
        for value in ("ABC", "A" * 32):
            with patch.object(tools, "fetch_profile", return_value=None) as fetch:
                self.assertEqual(tools.get_company_profile(value)["status"], "not_found")
                fetch.assert_called_once_with(value)

    def test_not_found(self):
        self.assertEqual(self.run_with_record(None)["status"], "not_found")

    def test_success_preserves_provenance(self):
        record = sample_record()
        result = self.run_with_record(record)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["source_uri"], record["source_uri"])
        self.assertEqual(result["reviewed_on"], record["reviewed_on"])

    def test_truncation_marks_output_and_does_not_mutate_record(self):
        record = sample_record()
        record["summary"] = "a" * 2001
        original = deepcopy(record)
        result = self.run_with_record(record)
        self.assertEqual(len(result["summary"]), 2000)
        self.assertTrue(result["truncated"])
        self.assertEqual(record, original)

    def test_exact_summary_boundary(self):
        record = sample_record()
        record["summary"] = "a" * 2000
        self.assertFalse(self.run_with_record(record)["truncated"])

    def test_unapproved_extra_columns_are_not_exposed(self):
        record = sample_record()
        record["internal_note"] = "private fixture text"
        self.assertNotIn("internal_note", self.run_with_record(record))

    def test_missing_or_nontext_fields_fail_closed(self):
        for field in tools.REQUIRED_FIELDS:
            for value in (None, "", "   ", 123):
                record = sample_record()
                record[field] = value
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.run_with_record(record)["status"], "invalid_record")

    def test_mismatched_id(self):
        record = sample_record()
        record["company_id"] = "OTHER-001"
        self.assertEqual(self.run_with_record(record)["status"], "invalid_record")

    def test_metadata_size_limits(self):
        for field, size in (("company_name", 201), ("source_uri", 1001)):
            record = sample_record()
            record[field] = "a" * size
            self.assertEqual(self.run_with_record(record)["status"], "invalid_record")

    def test_invalid_date(self):
        record = sample_record()
        record["reviewed_on"] = "not-a-date"
        self.assertEqual(self.run_with_record(record)["status"], "invalid_record")

    def test_freshness_boundaries(self):
        today = datetime.now(UTC).date()
        for age, status in ((90, "ok"), (91, "stale"), (-1, "invalid_record")):
            record = sample_record()
            record["reviewed_on"] = (today - timedelta(days=age)).isoformat()
            result = self.run_with_record(record)
            self.assertEqual(result["status"], status)
            if status == "stale":
                self.assertNotIn("summary", result)

    def test_output_byte_budget(self):
        record = sample_record()
        record["summary"] = "\x00" * 2000
        record["source_uri"] = "\x00" * 1000
        self.assertEqual(self.run_with_record(record)["status"], "invalid_record")

    def test_unicode_is_json_serializable(self):
        record = sample_record()
        record["summary"] = "研究" * 1000
        result = self.run_with_record(record)
        self.assertEqual(result["status"], "ok")
        self.assertLessEqual(len(json.dumps(result, ensure_ascii=False).encode()), 16000)

    def test_errors_do_not_leak_exception_text(self):
        for error in (Forbidden("SECRET"), TimeoutError("SECRET"), DefaultCredentialsError("SECRET")):
            with patch.object(tools, "fetch_profile", side_effect=error):
                with self.assertLogs(tools.logger) as logs:
                    result = tools.get_company_profile("ACME-001")
                self.assertEqual(result["status"], "unavailable")
                self.assertNotIn("SECRET", json.dumps(result))
                self.assertNotIn("SECRET", str(logs.output))


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "GOOGLE_CLOUD_PROJECT": "demo-project",
            "BIGQUERY_LOCATION": "US",
            "CORPORATE_PROFILES_TABLE": "demo-project.sentinel.company_profiles",
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_parameterized_query_and_resource_limits(self):
        with patch.object(repository.bigquery, "Client", autospec=True) as client_type:
            client = client_type.return_value.__enter__.return_value
            client.query_and_wait.return_value = [sample_record()]
            # Even if called below the tool validator, values stay parameters.
            hostile_value = "ACME-001' OR TRUE --"
            result = repository.fetch_profile(hostile_value)
            args, kwargs = client.query_and_wait.call_args
            self.assertNotIn(hostile_value, args[0])
            self.assertIn("approved = TRUE", args[0])
            self.assertIn("LIMIT 1", args[0])
            config = kwargs["job_config"]
            self.assertEqual(config.query_parameters[0].value, hostile_value)
            self.assertEqual(config.maximum_bytes_billed, 10_485_760)
            self.assertEqual(kwargs["api_timeout"], 5)
            self.assertEqual(kwargs["wait_timeout"], 15)
            self.assertIsNone(kwargs["retry"])
            self.assertIsNone(kwargs["job_retry"])
            self.assertEqual(kwargs["max_results"], 1)
            self.assertEqual(result["company_id"], "ACME-001")

    def test_empty_results(self):
        with patch.object(repository.bigquery, "Client", autospec=True) as client_type:
            client_type.return_value.__enter__.return_value.query_and_wait.return_value = []
            self.assertIsNone(repository.fetch_profile("ACME-001"))

    def test_table_configuration_cannot_inject_sql(self):
        with patch.dict(os.environ, {"CORPORATE_PROFILES_TABLE": "x.y.z`; DROP TABLE x; --"}):
            with patch.object(repository.bigquery, "Client") as client_type:
                with self.assertRaises(ValueError):
                    repository.fetch_profile("ACME-001")
                client_type.assert_not_called()


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.service = InMemorySessionService()
        session = await self.service.create_session(app_name="test", user_id="learner")
        invocation = InvocationContext(
            invocation_id="test",
            agent=Agent(name="test", model="unused-no-model-call"),
            session=session,
            session_service=self.service,
        )
        self.context = ToolContext(invocation_context=invocation)

    async def test_native_function_tool(self):
        tool = FunctionTool(func=tools.get_company_profile)
        with patch.object(tools, "fetch_profile", return_value=sample_record()):
            result = await tool.run_async(
                args={"company_id": "ACME-001"}, tool_context=self.context
            )
        self.assertEqual(result["status"], "ok")

    async def test_native_schema_exposes_only_company_id(self):
        request = LlmRequest()
        tool = FunctionTool(func=tools.get_company_profile)
        await tool.process_llm_request(tool_context=self.context, llm_request=request)
        declaration = request.config.tools[0].function_declarations[0]
        schema = declaration.parameters_json_schema
        properties = schema["properties"] if schema else declaration.parameters.properties
        self.assertEqual(set(properties), {"company_id"})

    async def test_adapter_matches_native(self):
        from corporate_research.adapter import adapted_tool
        native = FunctionTool(func=tools.get_company_profile)
        args = {"company_id": "ACME-001"}
        with patch.object(tools, "fetch_profile", return_value=sample_record()):
            expected = await native.run_async(args=args, tool_context=self.context)
            actual = await adapted_tool.run_async(args=args, tool_context=self.context)
        self.assertEqual(actual, expected)
        self.assertFalse(self.context.actions.skip_summarization)
        request = LlmRequest()
        await adapted_tool.process_llm_request(tool_context=self.context, llm_request=request)
        declaration = request.config.tools[0].function_declarations[0]
        schema = declaration.parameters_json_schema
        properties = schema["properties"] if schema else declaration.parameters.properties
        self.assertEqual(set(properties), {"company_id"})


if __name__ == "__main__":
    unittest.main()
