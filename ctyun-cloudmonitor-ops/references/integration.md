# Integration — Cloud Monitor

## Environment Setup (uv)

`ctyun` CLI and CTyun Python SDK require a Python runtime. Use **`uv`** for local, isolated, and **idempotent** environment management.

### Quick Start (Command-based)

**Bootstrap (idempotent — safe to re-run):**
```bash
uv venv --python 3.10

# Activate: macOS/Linux
source .venv/bin/activate
# Activate: Windows
# .venv\Scripts\activate

uv pip install ctyun-cli ctyun-sdk
```

**Pin versions for reproducibility:**
```bash
uv pip install ctyun-cli==1.0.0 ctyun-sdk==1.0.0
```
> Replace version numbers with the latest stable releases.

### Advanced: Project-based Setup (Recommended for Teams)

For reproducible, version-locked environments, use `pyproject.toml` with `uv sync`:

**1. Create `pyproject.toml`:**
```toml
[project]
name = "ctyun-cloudmonitor-ops"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "ctyun-cli>=1.0.0",
    "ctyun-sdk>=1.0.0",
]

[tool.uv]
python-version = "3.10"
```

**2. Sync environment (idempotent):**
```bash
uv sync
source .venv/bin/activate  # macOS/Linux
```

## Python SDK Bootstrap

### Basic Client Setup

```python
import os
from ctyun_sdk.core.credential import Credential
from ctyun_sdk.services.cloudmonitor.client import CloudMonitorClient

# Load credentials from environment
credential = Credential(
    os.environ["CTYUN_ACCESS_KEY"],
    os.environ["CTYUN_SECRET_KEY"],
)

# Initialize client
client = CloudMonitorClient(
    credential,
    os.environ.get("CTYUN_REGION", "cn-gz")
)
```

### Environment Variable Template (.env)

```ini
# CTyun Cloud Monitor credentials
CTYUN_ACCESS_KEY=your_access_key_here
CTYUN_SECRET_KEY=your_secret_key_here
CTYUN_REGION=cn-gz
```

> **SECURITY:** Never commit `.env` to version control. Add to `.gitignore`.

### Loading .env in Python

```python
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env file
env_file = Path.cwd() / '.env'
load_dotenv(env_file, override=False)  # Shell env takes priority

# Verify credentials
assert os.environ.get("CTYUN_ACCESS_KEY"), "CTYUN_ACCESS_KEY not set"
assert os.environ.get("CTYUN_SECRET_KEY"), "CTYUN_SECRET_KEY not set"
```

## CLI Configuration

### Interactive Configuration

```bash
ctyun config init
# Follow prompts to enter credentials
```

### Manual Configuration

For manual CLI configuration, see [CLI Usage / Sandbox Environment Setup](cli-usage.md#sandbox-environment-setup).

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Cloud Monitor CI

on: [push]

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Setup environment
        run: |
          uv venv --python 3.10
          uv pip install ctyun-cli ctyun-sdk
      
      - name: Configure credentials
        env:
          CTYUN_ACCESS_KEY: ${{ secrets.CTYUN_ACCESS_KEY }}
          CTYUN_SECRET_KEY: ${{ secrets.CTYUN_SECRET_KEY }}
        run: |
          mkdir -p ~/.ctyun
          cat > ~/.ctyun/config << EOF
          [default]
          access_key = ${CTYUN_ACCESS_KEY}
          secret_key = ${CTYUN_SECRET_KEY}
          region_id = cn-gz
          EOF
      
      - name: Verify Cloud Monitor access
        run: |
          source .venv/bin/activate
          ctyun --output json cloudmonitor describe-alarm-rules --region-id cn-gz
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    environment {
        CTYUN_ACCESS_KEY = credentials('ctyun-access-key')
        CTYUN_SECRET_KEY = credentials('ctyun-secret-key')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    uv venv --python 3.10
                    source .venv/bin/activate
                    uv pip install ctyun-cli ctyun-sdk
                '''
            }
        }
        
        stage('Configure') {
            steps {
                sh '''
                    mkdir -p ~/.ctyun
                    cat > ~/.ctyun/config << EOF
[default]
access_key = ${CTYUN_ACCESS_KEY}
secret_key = ${CTYUN_SECRET_KEY}
region_id = cn-gz
EOF
                '''
            }
        }
        
        stage('Run Monitoring') {
            steps {
                sh '''
                    source .venv/bin/activate
                    python scripts/monitor_check.py
                '''
            }
        }
    }
}
```

## Terraform Integration

While Cloud Monitor doesn't have an official Terraform provider, you can use local-exec provisioners with the CLI:

```hcl
resource "null_resource" "cloudmonitor_alarm" {
  triggers = {
    alarm_name = "high-cpu-alert"
    threshold  = "80"
  }
  
  provisioner "local-exec" {
    command = <<-EOT
      ctyun --output json cloudmonitor create-alarm-rule \
        --region-id ${var.region} \
        --alarm-name ${self.triggers.alarm_name} \
        --namespace ECS \
        --metric-name CPUUtilization \
        --resource-id ${aws_instance.example.id} \
        --threshold ${self.triggers.threshold}
    EOT
  }
}
```

## Monitoring Integration

### Prometheus Exporter (Conceptual)

```python
from prometheus_client import start_http_server, Gauge
import time
from ctyun_sdk.services.cloudmonitor.client import CloudMonitorClient

# Create metrics
cpu_gauge = Gauge('ctyun_ecs_cpu_percent', 'CPU usage', ['instance_id'])

def collect_metrics():
    # Query Cloud Monitor API
    resp = client.query_metric_data(
        namespace="ECS",
        metricName="CPUUtilization",
        resourceId="i-xxxxxxxx",
        # ... other params
    )
    
    # Export to Prometheus
    for dp in resp.result.datapoints:
        cpu_gauge.labels(instance_id="i-xxxxxxxx").set(dp.value)

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        collect_metrics()
        time.sleep(60)
```

### Datadog Integration

Forward Cloud Monitor alarms to Datadog via webhook:

```python
import requests
import json

def forward_to_datadog(alarm_event):
    """Forward Cloud Monitor alarm to Datadog"""
    payload = {
        "title": f"CTyun Alert: {alarm_event['alarmName']}",
        "text": f"Alarm {alarm_event['status']} for {alarm_event['resourceId']}",
        "priority": "normal" if alarm_event['status'] == 'OK' else "high",
        "tags": [
            f"namespace:{alarm_event['namespace']}",
            f"region:{alarm_event['region']}",
            f"alarm:{alarm_event['alarmId']}"
        ]
    }
    
    requests.post(
        "https://api.datadoghq.com/api/v1/events",
        headers={"DD-API-KEY": os.environ["DD_API_KEY"]},
        json=payload
    )
```

## Webhook Integration

### Receiving Cloud Monitor Webhooks

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/webhook/cloudmonitor', methods=['POST'])
def handle_cloudmonitor_webhook():
    event = request.json
    
    # Verify signature (if supported)
    # signature = request.headers.get('X-CTyun-Signature')
    
    # Process alarm event
    if event['status'] == 'ALARM':
        # Trigger PagerDuty, Slack, etc.
        send_pagerduty_alert(event)
    
    return {'status': 'ok'}

def send_pagerduty_alert(event):
    """Forward to PagerDuty"""
    import pdpyras
    session = pdpyras.EventsAPISession(os.environ['PAGERDUTY_KEY'])
    session.trigger(
        event['alarmName'],
        dedup_key=event['alarmId'],
        severity='critical' if event['metricValue'] > 95 else 'warning'
    )

if __name__ == '__main__':
    app.run(port=5000)
```

## SDK Version Locking

Pin SDK versions for reproducibility:

```toml
# pyproject.toml
[project]
dependencies = [
    "ctyun-cli==1.0.0",
    "ctyun-sdk==1.0.0",
]

[tool.uv.pip]
# Generate lock file
# uv pip compile pyproject.toml -o requirements.lock
```

## Multi-Region Setup

```python
# Initialize clients for multiple regions
regions = ['cn-gz', 'cn-bj', 'cn-sh']
clients = {}

for region in regions:
    clients[region] = CloudMonitorClient(
        credential,
        region
    )

# Query alarms across all regions
for region, client in clients.items():
    resp = client.describe_alarm_rules()
    print(f"{region}: {resp.result.totalCount} alarms")
```
