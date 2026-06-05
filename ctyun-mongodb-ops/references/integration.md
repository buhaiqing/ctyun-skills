# MongoDB Integration Guide

## CTyun Service Integration

### MongoDB Instance + Application

Applications running on CTyun ECS can connect to MongoDB instances within
the same VPC for low-latency data access.

**Setup:**
1. Deploy MongoDB instance in VPC `{{user.vpc_id}}`
2. Configure security group to allow ECS subnet traffic on port 27017
3. Connect from ECS using the MongoDB connection string

### Application Integration

**Common drivers:**
- **Python** — pymongo / motor (async) / MongoEngine (ODM)
- **Java** — MongoDB Java Driver / Spring Data MongoDB
- **Node.js** — mongodb (native) / mongoose (ODM)
- **Go** — go.mongodb.org/mongo-driver
- **Rust** — mongodb crate

## Cross-Skill Integration

| Skill | Integration Point |
|---|---|
| `ctyun-rds-ops` | Similar instance lifecycle pattern |
| `ctyun-ecs-ops` | Application servers connecting to MongoDB |
| `ctyun-cloudmonitor-ops` | MongoDB instance monitoring and alarm rules |
| `ctyun-vpc-ops` (planned) | Network configuration for MongoDB access |
