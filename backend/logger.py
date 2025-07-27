import logging
import sys

import structlog


def init_logging() -> None:
    # Clear ALL existing handlers and configuration
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Clear any existing structlog configuration
    structlog._config._CONFIG = structlog._config._Configuration()

    # Configure structlog with clean processors (no duplicates)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="ISO"),  # Only ONE timestamp processor
            structlog.processors.add_log_level,
            structlog.processors.CallsiteParameterAdder(  # Only ONE callsite processor
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            structlog.dev.ConsoleRenderer(colors=True, pad_event=False),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging separately (for FastAPI/uvicorn logs)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"))

    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Suppress noisy external logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
