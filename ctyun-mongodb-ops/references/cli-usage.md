# CTyun MongoDB CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support MongoDB operations.** Verified against
> `ctyun-cli v1.20.2` module list — **no MongoDB subcommand exists.**

## MongoDB Instance Operations (REST API)

MongoDB instance operations (create, describe, delete, backup) use the
CTyun MongoDB OpenAPI REST API via Python `requests` (see
[`api-sdk-usage.md`](api-sdk-usage.md)).

## MongoDB Data Operations (mongosh)

### Installation

```bash
# macOS
brew install mongosh

# Ubuntu/Debian (MongoDB repo)
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt-get update && apt-get install -y mongodb-mongosh

# Verify
mongosh --version
```

### Connection

```bash
# Using connection string (recommended)
mongosh "mongodb://{{user.username}}:{{user.password}}@{{user.host}}:{{user.port}}/{{user.database}}" --quiet
```

### Common Operations

```bash
# Ping the database
mongosh "{{user.connection_string}}" --quiet --eval 'db.runCommand({ping: 1})'

# List databases
mongosh "{{user.connection_string}}" --quiet --eval 'db.adminCommand({listDatabases: 1})'

# List collections
mongosh "{{user.connection_string}}" --quiet --eval 'db.getCollectionNames()'

# Query documents
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.find({{user.filter}}).limit({{user.limit}}).toArray()
'

# Aggregate
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.aggregate({{user.pipeline}}).toArray()
'

# Count documents
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.countDocuments({{user.filter}})
'

# Insert document
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.insertOne({{user.document}})
'

# Update documents
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.updateMany({{user.filter}}, {{user.update}})
'

# Delete documents (DANGEROUS — confirm first)
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.deleteMany({{user.filter}})
'

# Create index
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.createIndex({{user.index_spec}})
'
```

### Backup & Restore

```bash
# mongodump
mongodump --uri="{{user.connection_string}}" --out="{{user.backup_dir}}"

# mongorestore
mongorestore --uri="{{user.connection_string}}" "{{user.backup_dir}}"
```

## Evidence for `sdk-only` Tag

```
$ ctyun --help
# ... modules: ecs, monitor, redis, audit, ims, billing,
#     security, iam, ebs, cda, vpc, cce, elb, kafka, css,
#     emr, sfs, oceanfs, aone, lts ...
# No "mongodb" or "document" module present.
```
