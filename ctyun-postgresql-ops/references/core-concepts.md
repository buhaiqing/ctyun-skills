# PostgreSQL Core Concepts

## Overview

PostgreSQL is a powerful, open-source object-relational database system
with strong SQL standards compliance. This skill covers PostgreSQL data-level
operations on CTyun RDS PostgreSQL instances.

## Key Concepts

### SQL Operations

| Type | Operations | Examples |
|---|---|---|
| DDL | Data Definition Language | CREATE TABLE, ALTER TABLE, DROP TABLE, TRUNCATE |
| DML | Data Manipulation Language | SELECT, INSERT, UPDATE, DELETE |
| DCL | Data Control Language | GRANT, REVOKE, CREATE ROLE |
| TCL | Transaction Control | BEGIN, COMMIT, ROLLBACK, SAVEPOINT |

### Common Data Types

| Type | Description |
|---|---|
| `INTEGER` / `BIGINT` | Integer values |
| `VARCHAR(n)` / `TEXT` | Variable-length strings |
| `NUMERIC(p,s)` | Exact decimal |
| `TIMESTAMP` / `TIMESTAMPTZ` | Date/time with/without timezone |
| `JSON` / `JSONB` | JSON data (JSONB is indexed) |
| `BOOLEAN` | True/false |
| `UUID` | Universally unique identifier |
| `ARRAY` | Array of any data type |

### Index Types

| Type | Description |
|---|---|
| `BTREE` | Default, balanced tree |
| `HASH` | Hash index |
| `GIN` | Generalized Inverted Index (JSONB, full-text) |
| `GiST` | Generalized Search Tree (geometric, full-text) |
| `BRIN` | Block Range Index (large tables) |

### Schema Concept

PostgreSQL uses a **schema** hierarchy: `database → schema → table`.
The default schema is `public`. Schemas provide namespace isolation
within a single database.

## Performance Considerations

- Use **EXPLAIN ANALYZE** for query plan analysis
- Use `VACUUM` and `ANALYZE` regularly for query optimizer statistics
- **BRIN indexes** are efficient for large, append-only tables
- Use **partitioning** for very large tables (declarative in PG 10+)
- Monitor slow queries via `pg_stat_statements`
- Connection pooling recommended (e.g., PgBouncer)

## Security Best Practices

- **Least privilege**: Grant only required privileges per role
- **Strong passwords**: Use SCRAM-SHA-256 password authentication
- **SSL/TLS**: Enable SSL for client connections
- **pg_hba.conf**: Restrict client authentication by IP
- **Row-level security**: Implement fine-grained access control
- **Regular backups**: Use pg_dump or physical backup tools
