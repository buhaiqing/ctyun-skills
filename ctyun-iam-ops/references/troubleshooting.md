# IAM Troubleshooting Guide

## CLI-Level Errors

### `ctyun: command not found`

**Cause:** CLI not installed or not in PATH.

**Fix:**
```bash
pip install ctyun-cli>=1.20.0
ctyun --version
```

### `not authenticated` / status 401

**Cause:** Credentials not configured.

**Fix:**
```bash
# Check env vars
test -n "$CTYUN_ACCESS_KEY" && echo "AK set" || echo "AK missing"
test -n "$CTYUN_SECRET_KEY" && echo "SK set" || echo "SK missing"

# Check config file
cat ~/.ctyun/config

# Rewrite if needed
cat > ~/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = cn-gz
endpoint = iam.ctyun.cn
scheme = https
timeout = 20
CONFIGEOF
printf "%s" "default" > ~/.ctyun/current
```

> **CRITICAL:** Unlike SDK, the `ctyun` CLI reads credentials ONLY from
> `~/.ctyun/config`, NOT from environment variables.

### `subcommand not found` / no such option

**Cause:** CLI version too old; IAM command or flag doesn't exist.

**Fix:**
```bash
# Check version
ctyun --version

# Upgrade to latest (IAM requires >= 1.20.0 for full support)
pip install --upgrade ctyun-cli
```

### Non-JSON output

**Cause:** API gateway returned HTML error page or CLI crash.

**Fix:** Add `--output json` flag BEFORE the subcommand, not after.

---

## API-Level Errors

| Error Code / Message | Likely Cause | Resolution |
|---|---|---|
| `statusCode != 800` | API returned error | Surface `$.message` to user |
| `CTIAM_0113: 请求头账号ID与请求参数账号ID不同` | accountId mismatch | Ensure `--account-id` matches your account ID (not Access Key) |
| `CTIAM_0113: 请求头账号ID不能为空` | Missing accountId header | Add `--account-id` parameter |
| `CTIAM_0201: 用户不存在` | User does not exist | Verify user name and try `iam list-users` |
| `CTIAM_0202: 用户已存在` | User name already taken | Choose a different user name |
| `CTIAM_0301: 用户组不存在` | Group does not exist | Verify group name and try `iam list-groups` |
| `CTIAM_0302: 用户组已存在` | Group name already taken | Choose a different group name |
| `CTIAM_0401: 策略不存在` | Policy does not exist | Verify policy name and scope |
| `CTIAM_0501: 访问密钥不存在` | Access key not found | Verify AccessKeyId and user name |
| `CTIAM_0601: 角色不存在` | Role does not exist | Verify role name |
| `HTTP_403: 权限不足` | Insufficient permissions | Use main account or request elevated privileges |
| `HTTP_500` | Server-side error | Retry with exponential backoff; if persistent, contact CTyun support |

---

## IAM-Specific Issues

### Access Key Secret Lost

**Symptom:** Secret key was not saved after `iam create-access-key`.

**Fix:** The secret key is only shown once in the API response. It cannot be
retrieved later. Create a new access key and deactivate/delete the old one.

### Policy JSON Validation Failure

**Symptom:** Policy creation fails with syntax error.

**Fix:**
1. Validate JSON syntax locally:
   ```bash
   python -c "import json; json.loads(open('policy.json').read()); print('Valid JSON')"
   ```
2. Check that the policy follows the CTyun IAM schema:
   ```json
   {
     "Version": "1.0",
     "Statement": [
       {
         "Effect": "Allow|Deny",
         "Action": ["service:Operation"],
         "Resource": ["*"]
       }
     ]
   }
   ```
3. Ensure `Action` values use correct format: `service:Operation` (e.g., `ecs:Start`)

### Cannot Delete User

**Symptom:** User deletion fails.

**Possible causes:**
- User has access keys still active → deactivate or delete keys first
- User is member of a group → remove from all groups first
- User has MFA enabled → deactivate MFA first

**Resolution:**
```bash
# 1. Deactivate/delete access keys
ctyun iam list-access-keys --user-name <user_name>
ctyun iam update-access-key --user-name <user_name> --access-key-id <id> --status Inactive
ctyun iam delete-access-key --user-name <user_name> --access-key-id <id>

# 2. Remove user from all groups (list then remove)
ctyun iam list-groups --user-name <user_name>
# For each group:
ctyun iam remove-user-from-group --user-name <user_name> --group-name <group_name>

# 3. Now delete the user
ctyun iam delete-user --user-name <user_name>
```

### Cannot Delete Group

**Symptom:** Group deletion fails.

**Possible causes:**
- Group still has users attached → remove all users first
- Group still has policies attached → detach all policies first

**Resolution:**
```bash
# 1. Detach all policies
ctyun iam list-attached-group-policies --group-name <group_name>
# For each policy:
ctyun iam detach-group-policy --policy-name <policy_name> --group-name <group_name>

# 2. Remove all users
ctyun iam get-group --group-name <group_name>  # shows users
# For each user:
ctyun iam remove-user-from-group --user-name <user_name> --group-name <group_name>

# 3. Now delete the group
ctyun iam delete-group --group-name <group_name>
```

---

## SDK Fallback Triggers

| Condition | Action |
|---|---|
| CLI returns `5xx` for same operation twice | Fall back to SDK for that operation |
| CLI command not found | Fall back to SDK for that operation |
| CLI output is non-JSON after retry | Fall back to SDK for that operation |
| Operation has no CLI equivalent (MFA operations) | Use SDK directly |
| SDK also fails | Surface the API error to user |

Refer to [`cli-decision-matrix.md`](../../ctyun-skill-generator/references/cli-decision-matrix.md)
for the full fallback decision tree.
