import logging
import os
import time

# =========================
# LOGGER SETUP (FIXED)
# =========================
def setup_logger():
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("weather_pipeline")

    logger.propagate = False

    if logger.hasHandlers():
         logger.handlers.clear()

    # Duplicate log problem FIX
    if not logger.handlers:
        handler = logging.FileHandler(
            "logs/pipeline.log",
            encoding="utf-8"
        )

        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


# =========================
# PIPELINE TIMER
# =========================
class PipelineTimer:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def end(self):
        if not self.start_time:
            return 0
        return time.time() - self.start_time


# =========================
# PIPELINE LOGGING EVENTS
# =========================
def log_start(logger, mode):
    logger.info("-" * 40)
    logger.info(f"PIPELINE START | mode={mode}")


def log_end(logger, duration, mode=None):
    if mode:
        logger.info(f"PIPELINE END | mode={mode} | duration={duration:.2f}s")
    else:
        logger.info(f"PIPELINE END | duration={duration:.2f}s")
    logger.info("-" * 40)


# =========================
# ROW COUNTS PER STAGE
# =========================
def log_row_counts(logger, stage, counts_dict):
    """
    counts_dict example:
    {"Baku": 1827, "Ganja": 1800}
    """
    logger.info(f"--- ROW COUNTS | STAGE: {stage} ---")

    for city, count in counts_dict.items():
        logger.info(f"{stage} | city={city} | rows={count}")


# =========================
# QUALITY CHECK LOGGING
# =========================
def log_quality_checks(logger, results_df):
    logger.info(">>> QUALITY CHECK RESULTS START")

    for _, row in results_df.iterrows():
        status = str(row["status"]).upper()
        msg = (
            f"CHECK: {row['check_name']} | "
            f"STATUS: {status} | "
            f"DETAILS: {row['details']}"
        )

        if status == "FAIL":
            logger.error(msg)
        elif status in ["WARN", "WARNING"]:
            logger.warning(msg)
        else:
            logger.info(msg)

    logger.info(">>> QUALITY CHECK RESULTS END")


# =========================
# ERROR & WARNING HANDLERS
# =========================
def log_error(logger, error):
    logger.error(f"FATAL ERROR | {str(error)}", exc_info=True)


def log_warning(logger, message):
    logger.warning(f"WARNING | {message}")