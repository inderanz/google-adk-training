"""
openapi/normalizer.py
Enterprise FDE Utility: Normalizes legacy or non-standard OpenAPI/Swagger specs for Google ADK 2.0.

Key Capabilities:
1. Auto-populates missing `operationId`s from HTTP method + path.
2. Subsets/whitelists allowed business endpoints, stripping admin/internal routes.
3. Validates required ADK parameters (descriptions, path parameters).
"""

import json
import re
from typing import Any


def sanitize_path_to_operation_id(method: str, path: str) -> str:
    """Transform an HTTP method and route path into a clean snake_case operationId.

    Example:
        GET /v1/borrowers/{tax_id}/exposure -> get_borrower_exposure
        GET /api/v2/accounts/{id}/balance -> get_account_balance
    """
    # Remove URL parameter braces: {tax_id} -> tax_id
    clean = re.sub(r"\{([^}]+)\}", "", path)
    # Remove version prefixes like /v1/, /api/v2/, /api/
    clean = re.sub(r"^/?(api/)?v\d+/?", "", clean)
    # Replace non-alphanumeric characters with underscores
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", clean).strip("_")
    # Singularize common plural prefixes if clean
    clean = re.sub(r"^borrowers_", "borrower_", clean)
    clean = re.sub(r"^accounts_", "account_", clean)

    return f"{method.lower()}_{clean}"


def normalize_legacy_spec(
    raw_spec: dict[str, Any], allowed_path_patterns: list[str] | None = None
) -> dict[str, Any]:
    """Normalize a legacy OpenAPI 3.0 specification dictionary for Google ADK 2.0.

    Args:
        raw_spec: The raw OpenAPI dictionary (possibly missing operationIds).
        allowed_path_patterns: Optional list of regex patterns or prefix strings
                               to whitelist. Endpoints not matching are stripped.

    Returns:
        A sanitized, ADK-compliant OpenAPI specification dictionary.
    """
    normalized = {
        "openapi": raw_spec.get("openapi", "3.0.0"),
        "info": raw_spec.get("info", {"title": "Normalized API", "version": "1.0.0"}),
        "servers": raw_spec.get("servers", [{"url": "/"}]),
        "paths": {},
    }

    raw_paths = raw_spec.get("paths", {})

    for path, path_item in raw_paths.items():
        # Step 1: Endpoint Whitelisting / Subsetting
        if allowed_path_patterns is not None:
            matches_whitelist = any(
                re.search(pattern, path) for pattern in allowed_path_patterns
            )
            if not matches_whitelist:
                continue  # Skip unapproved endpoints (admin, internal, telemetry)

        normalized_path_item = {}

        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue

            op_copy = dict(operation)

            # Step 2: Auto-inject missing operationId
            if "operationId" not in op_copy or not op_copy["operationId"]:
                generated_op_id = sanitize_path_to_operation_id(method, path)
                op_copy["operationId"] = generated_op_id

            # Step 3: Ensure description exists (vital for Gemini tool routing)
            if not op_copy.get("description") and op_copy.get("summary"):
                op_copy["description"] = op_copy["summary"]
            elif not op_copy.get("description"):
                op_copy["description"] = f"Executes {method.upper()} on {path}"

            # Step 4: Ensure path parameters have required: True
            if "parameters" in op_copy:
                for param in op_copy["parameters"]:
                    if param.get("in") == "path":
                        param["required"] = True

            normalized_path_item[method] = op_copy

        if normalized_path_item:
            normalized["paths"][path] = normalized_path_item

    return normalized


def load_and_normalize_spec(
    file_path: str, allowed_path_patterns: list[str] | None = None
) -> str:
    """Load a raw JSON/YAML spec file, normalize it, and return a JSON string for OpenAPIToolset."""
    with open(file_path, "r", encoding="utf-8") as f:
        raw_spec = json.load(f)

    clean_spec = normalize_legacy_spec(
        raw_spec, allowed_path_patterns=allowed_path_patterns
    )
    return json.dumps(clean_spec, indent=2)
