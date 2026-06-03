# Security And Governance

Generated SQL is treated as untrusted input. The platform validates and governs every query before it can reach the execution layer.

## Controls

- Read-only mode by default
- Single SQL statement only
- `SELECT` and `WITH` statements only
- Destructive keyword blocking
- SQL comment rejection
- Role-based table allowlists
- Sensitive column detection
- Approval simulation for broad or sensitive access
- Audit log for every workflow

## Blocked Operations

The validator blocks `DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `INSERT`, `UPDATE`, `CREATE`, `MERGE`, `REPLACE`, `EXEC`, and `VACUUM`.

## Governance Model

The governance layer receives a validation report and returns one of:

- `approved`: query can execute in read-only mode
- `approval_required`: valid query but execution is paused for human review
- `blocked`: query cannot execute

## Production Extensions

- Integrate with enterprise identity providers
- Enforce row and column-level security at the database layer
- Add query cost estimation
- Add approval workflow integration with ServiceNow or Jira
- Attach data classification metadata from a catalog
- Export audit events to SIEM tooling
