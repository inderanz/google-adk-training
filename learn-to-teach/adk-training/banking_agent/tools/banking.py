from google.adk.tools import ToolContext
from pydantic import BaseModel, Field


class PreferenceResponse(BaseModel):
    """Response payload for customer preference updates."""

    status: str = Field(description="Execution status: 'success' or 'error'")
    message: str | None = Field(default=None, description="Explanatory result message")


class CustomerProfileResponse(BaseModel):
    """Response payload for customer profile updates."""

    status: str = Field(default="success")
    user_id: str = Field(description="Authenticated user identity from ToolContext")
    preferred_language: str = Field(
        default="English",
        description="User's preferred language for banking communications",
    )
    preferred_branch: str = Field(
        default="Not Set",
        description="User's preferred bank branch for in-person visits",
    )

class LoanDraftResponse(BaseModel):
    """Response model for multi-turn loan application accumulation."""

    status: str = Field(
        description="Draft state: 'in_progress', 'ready_for_submission', or 'error'."
    )
    captured_fields: list[str] = Field(
        description="List of loan parameters collected in session state so far."
    )
    missing_fields: list[str] = Field(
        description="List of required loan parameters still needed before submission."
    )

class LoanSubmissionResponse(BaseModel):
    """Final loan application confirmation payload."""

    status: str = Field(description="Execution status: 'submitted' or 'error'")
    application_id: str = Field(default=None, description="Generated application ID")
    total_loan: float | None = Field(
        default=None, description="Sanctioned loan principal amount"
    )
    tenure_months: int | None = Field(
        default=None, description="Repayment duration in months"
    )
    monthly_emi: float | None = Field(
        default=None, description="Calculated Equated Monthly Installment (EMI)"
    )
    message: str | None = Field(
        default=None, description="Error message if submission failed"
    )


def set_customer_preference(
    preferred_language: str, preferred_branch: str, tool_context: ToolContext
) -> PreferenceResponse:
    """Updates the customer's preferred language and branch in their profile.

    Args:
        preferred_language: Requested language (e.g., 'Hindi', 'English',
          'Tamil').
        preferred_branch: City or branch code (e.g., 'Connaught Place Delhi',
          'MG Road Bengaluru').
    """
    tool_context.state["preferred_language"] = preferred_language
    tool_context.state["preferred_branch"] = preferred_branch

    return PreferenceResponse(
        status="success",
        message=f"Language set to {preferred_language}, branch set to {preferred_branch}.",
    )


def get_customer_profile(tool_context: ToolContext) -> CustomerProfileResponse:
    """Retrieves the customer's profile information from the tool context."""
     # Zero-Trust Security: Read user_id from runtime, not prompt arguments!
    authenticated_user = tool_context.user_id or "guest_user"
    lang = tool_context.state.get("preferred_language", "English")
    branch = tool_context.state.get("preferred_branch", "Not Set")

    return CustomerProfileResponse(
        user_id=authenticated_user,
        preferred_language=lang,
        preferred_branch=branch,
    )

def update_loan_draft(
        field_name: str, field_value: str, tool_context: ToolContext
) -> LoanDraftResponse:
    """Updates a specific field in the customer's active loan application draft.

    Args:
        field_name: The draft field to update ('applicant_name',
          'annual_income', 'loan_amount', 'tenure_months').
        field_value: The value provided by the customer for the field.
    """
    draft = tool_context.state.get("loan_draft", {})
    draft[field_name] = field_value
    tool_context.state["loan_draft"] = draft

    required = ["applicant_name", "annual_income", "loan_amount", "tenure_months"]
    missing = [f for f in required if f not in draft]

    return LoanDraftResponse(
        status="ready_for_submission" if not missing else "in_progress",
        captured_fields=list(draft.keys()),
        missing_fields=missing,
    )

def submit_loan_application(
    tool_context: ToolContext,
) -> LoanSubmissionResponse:
    """Submits the accumulated loan application draft for processing and calculates EMI."""
    draft = tool_context.state.get("loan_draft", {})
    required = ["applicant_name", "annual_income", "loan_amount", "tenure_months"]
    missing = [f for f in required if f not in draft]

    if missing:
        return LoanSubmissionResponse(
            status="error",
            message=f"Cannot submit. Missing required fields: {', '.join(missing)}",
        )

    try:
        principal = float(draft["loan_amount"])
        months = int(draft["tenure_months"])
        annual_rate = 10.5  # 10.5% annual interest
        monthly_rate = annual_rate / 12 / 100

        # Standard EMI Formula: P * r * (1 + r)^n / ((1 + r)^n - 1)
        emi = (
            principal
            * monthly_rate
            * ((1 + monthly_rate) ** months)
            / (((1 + monthly_rate) ** months) - 1)
        )

        app_id = f"LN-INR-{hash(tool_context.user_id + str(principal)) % 100000:05d}"

        return LoanSubmissionResponse(
            status="submitted",
            application_id=app_id,
            total_loan=round(principal, 2),
            tenure_months=months,
            monthly_emi=round(emi, 2),
        )
    except (ValueError, ZeroDivisionError) as e:
        return LoanSubmissionResponse(
            status="error", message=f"Calculation error: {str(e)}"
        )
