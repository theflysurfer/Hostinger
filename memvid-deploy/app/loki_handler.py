"""
Loki logging handler for MemVid RAG API
Sends logs to Loki for centralized logging
"""
import os
import logging
from loguru import logger
import requests
import time
import json
from typing import Dict, Any


class LokiHandler(logging.Handler):
    """
    Custom logging handler that sends logs to Loki
    """

    def __init__(self, loki_url: str, labels: Dict[str, str] = None):
        """
        Initialize Loki handler

        Args:
            loki_url: Loki push API URL (e.g., http://loki:3100/loki/api/v1/push)
            labels: Additional labels to attach to all logs
        """
        super().__init__()
        self.loki_url = loki_url
        self.labels = labels or {}
        self.labels.setdefault("app", "memvid-api")
        self.labels.setdefault("env", os.getenv("ENVIRONMENT", "production"))

    def emit(self, record):
        """
        Emit a log record to Loki
        """
        try:
            # Format log message
            log_entry = self.format(record)

            # Create labels string
            labels_str = ",".join([f'{k}="{v}"' for k, v in self.labels.items()])
            labels_str = "{" + labels_str + f',level="{record.levelname.lower()}"' + "}"

            # Create Loki payload
            payload = {
                "streams": [
                    {
                        "stream": self.labels,
                        "values": [
                            [str(int(time.time() * 1e9)), log_entry]  # Timestamp in nanoseconds
                        ]
                    }
                ]
            }

            # Send to Loki
            response = requests.post(
                self.loki_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if response.status_code not in [200, 204]:
                print(f"Failed to send log to Loki: {response.status_code} {response.text}")

        except Exception as e:
            # Don't fail if logging fails
            print(f"Loki handler error: {e}")


def configure_loki_logging(loki_url: str = None):
    """
    Configure Loki logging for the application

    Args:
        loki_url: Loki push API URL. If not provided, uses LOKI_URL env var
    """
    loki_url = loki_url or os.getenv("LOKI_URL")

    if not loki_url:
        logger.warning("LOKI_URL not configured, skipping Loki logging setup")
        return

    try:
        # Create Loki handler
        loki_handler = LokiHandler(
            loki_url=loki_url,
            labels={
                "app": "memvid-api",
                "service": "rag",
                "env": os.getenv("ENVIRONMENT", "production")
            }
        )

        # Set formatter
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}'
        )
        loki_handler.setFormatter(formatter)

        # Add to root logger
        logging.root.addHandler(loki_handler)
        logging.root.setLevel(logging.INFO)

        logger.info(f"Loki logging configured: {loki_url}")

    except Exception as e:
        logger.error(f"Failed to configure Loki logging: {e}")


# Loguru sink for Loki
def loguru_loki_sink(message):
    """
    Loguru sink function to send logs to Loki
    """
    loki_url = os.getenv("LOKI_URL")
    if not loki_url:
        return

    try:
        record = message.record
        labels = {
            "app": "memvid-api",
            "service": "rag",
            "level": record["level"].name.lower(),
            "env": os.getenv("ENVIRONMENT", "production")
        }

        # Create Loki payload
        payload = {
            "streams": [
                {
                    "stream": labels,
                    "values": [
                        [str(int(time.time() * 1e9)), message]
                    ]
                }
            ]
        }

        # Send to Loki (non-blocking)
        requests.post(
            loki_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=1
        )

    except Exception:
        # Silent fail - don't break application if Loki is down
        pass
