# KMS Core Concepts

## Overview

CTyun **KMS (密钥管理服务)** — Key Management Service — manages cryptographic
keys for data encryption. KMS provides centralized key lifecycle management
with hardware security module (HSM) protection.

## Key Lifecycle

```
Create → Enabled → Disabled → Enabled
                 → PendingDeletion → (wait pending window) → Deleted
                 → PendingDeletion → CancelDeletion → Enabled
```

### Key States

| State | Description |
|---|---|
| **Enabled** | Key is active and usable for cryptographic operations |
| **Disabled** | Key exists but cannot be used |
| **PendingDeletion** | Key scheduled for deletion; not usable |
| **Deleted** | Key permanently removed (irreversible) |

## Key Types

| Type | Description |
|---|---|
| **Symmetric** | Same key used for encryption and decryption (AES) |
| **Asymmetric** | Public/private key pair (RSA, EC) |

## Key Usage

| Use Case | Key Type | Description |
|---|---|---|
| Data at rest | Symmetric | Encrypt EBS volumes, RDS instances |
| Data in transit | Asymmetric | TLS/SSL certificates |
| Application-level | Symmetric | Customer-managed encryption keys |
| Digital signatures | Asymmetric | Code signing, document signing |

## Key Rotation

KMS supports automatic and manual key rotation:
- **Automatic**: KMS rotates keys annually by default
- **Manual**: Create new key and update application references

## Related Services

- **IAM** — Key access policies and permissions
- **EVS** — Volume encryption uses KMS keys
- **RDS** — Database encryption uses KMS keys
- **OSS** — Object storage server-side encryption
