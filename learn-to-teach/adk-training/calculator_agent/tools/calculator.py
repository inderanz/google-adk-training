from pydantic import BaseModel, Field

class MathResult(BaseModel):
    """Structured response for basic arithmetic operations."""

    status: str = Field(description="Execution status: 'success' or 'error'")
    result: float | None = Field( default=None, description="The computed mathematical value")
    message: str | None = Field(default=None, description="Error message if any issues occurred during computation")


class GstInvoiceReport(BaseModel):
    """Structured financial report for Indian Goods and services tax (GST) invoices."""

    status: str = Field(default="success", description="Execution status of calculation")
    base_amount: float = Field(description="Original pre-tax amount in currency")
    tax_rate_percent: float = Field(description="Applicable GST slab percentage")
    cgst: float = Field(description="Central GST (equal to half of total GST)")
    sgst: float = Field(description="State GST (equal to half of total GST)")
    total_gst: float = Field(description="Total GST amount (sum of CGST and SGST)")
    total_payable: float = Field(description="Final invoice total payable by customer (base amount + total GST)")


def add(a: float, b: float) -> MathResult:
    """Perform addition of two numbers.

    Use this tool when the user asks to find the sum of two numbers.

    Args:
        a (float): First number.
        b (float): Second number.
    """
    return MathResult(status="success", result=a + b)

def subtract(a: float, b: float) -> MathResult:
       """Subtracts the second number from the first number.

       Use this tool when the user asks to find the difference between two
       numbers.

       Args:
           a: The first number.
           b: The second number to subtract.
       """
       return MathResult(status="success", result=a - b)


def multiply(a: float, b: float) -> MathResult:
       """Multiplies two numbers together.

       Use this tool when the user asks to find the product of two numbers.

       Args:
           a: The first number.
           b: The second number to multiply.
       """
       return MathResult(status="success", result=a * b)


def divide(a: float, b: float) -> MathResult:
       """Divides the first number by the second number.

       Use this tool when the user asks to divide one number by another.

       Args:
           a: The numerator.
           b: The denominator.
       """
       if b == 0:
           return MathResult(
               status="error",
               message="Cannot divide by zero. Denominator must be non-zero.",
           )
       return MathResult(status="success", result=a / b)


def calculate_gst_invoice(
       amount: float, tax_rate_percent: float = 18.0
) -> GstInvoiceReport:
       """Calculates an itemized GST invoice including CGST, SGST, and the total payable amount.

       Use this tool whenever a user asks to calculate GST, tax, or an invoice total for a purchase.

       Args:
           amount: The base pre-tax amount in rupees (INR) or currency.
           tax_rate_percent: The GST tax slab percentage (defaults to 18.0%).
       """
       total_tax = round(amount * (tax_rate_percent / 100.0), 2)
       half_tax = round(total_tax / 2.0, 2)
       total_due = round(amount + total_tax, 2)

       return GstInvoiceReport(
           base_amount=amount,
           tax_rate_percent=tax_rate_percent,
           cgst=half_tax,
           sgst=half_tax,
           total_gst=total_tax,
           total_payable=total_due,
       )
