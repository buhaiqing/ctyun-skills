# API & SDK Usage — Alert Intelligence

## SDK Client

```python
from ctyun_sdk.services.cloudmonitor.client import CloudMonitorClient
from ctyun_sdk.core.credential import Credential
import os

credential = Credential(os.environ["CTYUN_ACCESS_KEY"], os.environ["CTYUN_SECRET_KEY"])
client = CloudMonitorClient(credential, os.environ.get("CTYUN_REGION", "cn-gz"))

# Query alarm history
history = client.list_alarm_history(
    start_time="2026-01-01T00:00:00Z",
    end_time="2026-06-01T00:00:00Z",
    namespace="ECS",
)
```

## Key Endpoints

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List Alarm History | `/v2/cloudmonitor/alarm-history` | GET |
| Query Alarm Statistics | `/v2/cloudmonitor/alarm-statistics` | GET |

All operations are read-only GET requests.
