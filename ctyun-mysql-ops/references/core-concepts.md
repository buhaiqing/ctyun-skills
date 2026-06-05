# MySQL Core Concepts

## Overview

MySQL is the world's most popular open-source relational database. This
skill covers MySQL data-level operations on CTyun RDS MySQL instances.

## Key Concepts

### SQL Operations

| Type | Operations | Examples |
|---|---|---|
| DDL | Data Definition Language | CREATE TABLE, ALTER TABLE, DROP TABLE, TRUNCATE |
| DML | Data Manipulation Language | SELECT, INSERT, UPDATE, DELETE |
| DCL | Data Control Language | GRANT, REVOKE, CREATE USER |
| TCL | Transaction Control | BEGIN, COMMIT, ROLLBACK |

### Common Data Types

| Type | Description |
|---|---|
| `INT` / `BIGINT` | Integer values |
| `VARCHAR(n)` | Variable-length string |
| `TEXT` | Long text |
| `DECIMAL(p,s)` | Exact decimal (money) |
| `DATETIME` / `TIMESTAMP` | Date and time |
| `JSON` | JSON data (MySQL 5.7+) |
| `BOOLEAN` | TINYINT(1) alias |

### Index Types

| Type | Description |
|---|---|
| `BTREE` | Default, balanced tree |
| `HASH` | Hash index (MEMORY engine only) |
| `FULLTEXT` | Full-text search |
| `SPATIAL` | Geographic data |

### Storage Engines

| Engine | Description | Use Case |
|---|---|---|
| InnoDB | Default, ACID compliant, row-level locking | General purpose |
| MyISAM | Table-level locking, no transactions | Read-only, legacy |
| MEMORY | In-memory tables | Temporary data |

## Performance Considerations

- Use **EXPLAIN** to analyze query execution plans
- Avoid `SELECT *` in production queries
- Use **LIMIT** to restrict result sets
- Create indexes for columns used in WHERE and JOIN conditions
- Monitor slow queries via `slow_query_log`
- Use connection pooling for application connections

## Security Best Practices

- **Least privilege**: Grant minimum required privileges
- **Strong passwords**: Use complex passwords for all MySQL users
- **SQL injection**: Use parameterized queries in applications
- **SSL/TLS**: Enable SSL for client connections
- **Regular backups**: Use mysqldump for logical backups
