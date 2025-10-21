"""
Prometheus metrics for MemVid RAG API
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Request counters
http_requests_total = Counter(
    'memvid_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Indexing metrics
indexing_operations_total = Counter(
    'memvid_indexing_operations_total',
    'Total indexing operations',
    ['project_id', 'operation_type', 'status']
)

indexing_chunks_total = Counter(
    'memvid_indexing_chunks_total',
    'Total chunks indexed',
    ['project_id']
)

indexing_duration_seconds = Histogram(
    'memvid_indexing_duration_seconds',
    'Indexing operation duration',
    ['operation_type'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

# Search metrics
search_operations_total = Counter(
    'memvid_search_operations_total',
    'Total search operations',
    ['project_id']
)

search_duration_seconds = Histogram(
    'memvid_search_duration_seconds',
    'Search operation duration',
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Chat/RAG metrics
chat_operations_total = Counter(
    'memvid_chat_operations_total',
    'Total chat/RAG operations',
    ['project_id', 'model', 'status']
)

chat_duration_seconds = Histogram(
    'memvid_chat_duration_seconds',
    'Chat/RAG operation duration',
    ['model'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0]
)

chat_context_chunks = Histogram(
    'memvid_chat_context_chunks',
    'Number of chunks used in chat context',
    buckets=[1, 2, 3, 5, 10, 20, 50]
)

# Project metrics
projects_total = Gauge(
    'memvid_projects_total',
    'Total number of projects'
)

project_chunks_total = Gauge(
    'memvid_project_chunks_total',
    'Total chunks per project',
    ['project_id', 'project_name']
)

project_video_size_mb = Gauge(
    'memvid_project_video_size_mb',
    'Project video size in MB',
    ['project_id', 'project_name']
)

# Error metrics
errors_total = Counter(
    'memvid_errors_total',
    'Total errors',
    ['endpoint', 'error_type']
)


def get_metrics():
    """Get Prometheus metrics"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


class MetricsMiddleware:
    """Middleware to track HTTP metrics"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Track request
                http_requests_total.labels(
                    method=scope["method"],
                    endpoint=scope["path"],
                    status=message["status"]
                ).inc()

            await send(message)

        await self.app(scope, receive, send_wrapper)
