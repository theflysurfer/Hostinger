#!/usr/bin/env python3
"""
Script to integrate async endpoints and Loki logging into api_v2.py
"""
import re
import sys

def integrate():
    # Read api_v2.py
    with open('app/api_v2.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add imports after existing imports
    imports_to_add = '''
# RQ/Redis and Loki imports
try:
    from .queue import enqueue_indexing, enqueue_chat, get_job_status
    from .jobs import index_text_job, index_folder_job, chat_job
    from .loki_handler import loguru_loki_sink
except ImportError as e:
    logger.warning(f"RQ/Loki imports failed: {e}")
'''

    # Find the import section end
    import_pattern = r'(from \.project_manager import ProjectManager)'
    if re.search(import_pattern, content):
        content = re.sub(import_pattern, r'\1\n' + imports_to_add, content, count=1)
        print("✓ Added imports")
    else:
        print("✗ Could not find import section")

    # 2. Add Loki configuration after logger configuration
    loki_config = '''
# Configure Loki logging
loki_url = os.getenv("LOKI_URL")
if loki_url:
    try:
        logger.add(loguru_loki_sink, serialize=True)
        logger.info(f"Loki logging configured: {loki_url}")
    except Exception as e:
        logger.warning(f"Failed to configure Loki: {e}")
'''

    # Add after logger configuration
    if 'Configure Loki logging' not in content:
        logger_pattern = r'(logger\.add\(\s*"/app/logs/memvid-api\.log"[^)]+\))'
        content = re.sub(logger_pattern, r'\1' + loki_config, content, count=1, flags=re.DOTALL)
        print("✓ Added Loki configuration")
    else:
        print("- Loki already configured")

    # 3. Read async endpoints from file
    with open('app/async_endpoints.py', 'r', encoding='utf-8') as f:
        async_content = f.read()

    # Extract endpoints (skip the comment section)
    endpoints_match = re.search(r'@app\.post.*', async_content, re.DOTALL)
    if endpoints_match:
        async_endpoints = '\n\n# ============================================================================\n# ASYNC JOB ENDPOINTS\n# ============================================================================\n\n' + endpoints_match.group(0)

        # Add endpoints if not already present
        if '/index/text/async' not in content:
            content = content.rstrip() + '\n' + async_endpoints
            print("✓ Added async endpoints")
        else:
            print("- Async endpoints already present")
    else:
        print("✗ Could not extract async endpoints")

    # Write back
    with open('app/api_v2.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✓ Integration complete!")
    return 0

if __name__ == "__main__":
    sys.exit(integrate())
