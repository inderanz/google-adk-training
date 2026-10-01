import logging

# Set up standard logging, which can be easily adapted to Cloud Logging
# import google.cloud.logging
# client = google.cloud.logging.Client()
# client.setup_logging()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("CloudLogging")

def log_query_to_model(prompt_text: str):
    """Callback to log the query to Cloud Logging."""
    logger.info(f"Query to model: {prompt_text}")

def log_model_response(response_text: str):
    """Callback to log the model's response to Cloud Logging."""
    logger.info(f"Model response: {response_text}")
