"""Read an approved profile using the official Google BigQuery client."""

import os
import re

from google.cloud import bigquery

# 10 MiB: do not set a limit below BigQuery's minimum query billing unit.
MAX_BYTES_BILLED = 10_485_760
API_TIMEOUT_SECONDS = 5
WAIT_TIMEOUT_SECONDS = 15

# A table identifier is configuration, not an argument the model may choose.
TABLE_ID_PATTERN = r"[a-z][a-z0-9-]*\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*"


def fetch_profile(company_id: str) -> dict[str, str] | None:
    """Fetch the most recently reviewed, approved row for one company."""
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.environ["BIGQUERY_LOCATION"]
    table_id = os.environ["CORPORATE_PROFILES_TABLE"]
    if re.fullmatch(TABLE_ID_PATTERN, table_id) is None:
        raise ValueError("Invalid configured table identifier.")

    # Values use parameters; BigQuery parameters cannot replace table identifiers.
    query = f"""
        SELECT company_id, company_name, summary, source_uri,
               CAST(reviewed_on AS STRING) AS reviewed_on
        FROM `{table_id}`
        WHERE company_id = @company_id AND approved = TRUE
        ORDER BY reviewed_on DESC
        LIMIT 1
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_id", "STRING", company_id)
        ],
        maximum_bytes_billed=MAX_BYTES_BILLED,
        labels={"component": "corporate-profile"},
    )
    # ADC supplies credentials; the application does not load a key file.
    with bigquery.Client(project=project, location=location) as client:
        rows = client.query_and_wait(
            query,
            job_config=config,
            api_timeout=API_TIMEOUT_SECONDS,
            wait_timeout=WAIT_TIMEOUT_SECONDS,
            retry=None,
            job_retry=None,
            max_results=1,
        )
        for row in rows:
            return dict(row)
    return None
