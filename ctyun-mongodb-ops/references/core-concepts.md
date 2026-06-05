# MongoDB Core Concepts

## Overview

CTyun **MongoDB (文档数据库服务)** — Document Database Service — provides
managed MongoDB instances. This skill covers both instance lifecycle and
data-level operations.

## Architecture

```
CTyun MongoDB (文档数据库服务)
  └── MongoDB Instance (replica set)
        ├── Primary node
        ├── Secondary node(s) (data redundancy)
        └── Engine version: 6.0, 7.0
```

## MongoDB Data Model

```
MongoDB Instance
  └── Database (logical container)
        └── Collection (analogous to table)
              └── Document (BSON JSON, analogous to row)
                    └── Fields (key-value pairs)
```

### Document Example

```json
{
  "_id": ObjectId("..."),
  "name": "example",
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "tags": ["production", "critical"],
  "metadata": { "version": 1 }
}
```

## CRUD Operations

| Operation | mongosh Function | Description |
|---|---|---|
| Create | `insertOne()` / `insertMany()` | Insert documents |
| Read | `find()` / `findOne()` | Query documents |
| Update | `updateOne()` / `updateMany()` / `replaceOne()` | Update documents |
| Delete | `deleteOne()` / `deleteMany()` | Remove documents |

## Index Types

| Type | Description |
|---|---|
| `_id` (default) | Unique index on `_id` field |
| Single field | Index on one field |
| Compound | Index on multiple fields |
| Text | Full-text search index |
| Geospatial | 2dsphere / 2d indexes |
| TTL | Time-to-live auto-expiry |
| Unique | Ensures unique values |
| Hashed | For hashed sharding |

## Aggregation Pipeline

The aggregation pipeline processes documents through stages:

```
db.collection.aggregate([
  { $match: { status: "active" } },
  { $group: { _id: "$category", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

Common stages: `$match`, `$group`, `$sort`, `$project`, `$lookup`, `$unwind`, `$limit`

## Replication & High Availability

MongoDB instances in CTyun use **Replica Sets**:

- **Primary**: Handles all write operations
- **Secondaries**: Replicate data from primary (readable, optionally)
- **Arbiter** (optional): Votes in elections, holds no data (rare in CTyun)

## Backup

| Backup Type | Method | Scope |
|---|---|---|
| Instance backup | CTyun API | Full instance snapshot |
| mongodump | CLI tool | Logical backup (db/collection level) |
| mongorestore | CLI tool | Restore from mongodump |

## Safety

- **deleteOne/deleteMany**: Can cause data loss — confirm before executing
- **drop()**: Irreversibly removes a collection
- **dropDatabase()**: Irreversibly removes entire database
- **Instance delete**: Irreversibly removes the entire instance
- Always verify collection/database name before destructive operations
