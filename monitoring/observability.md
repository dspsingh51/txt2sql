# Observability

The platform includes production-inspired observability hooks for AI workflows and SQL execution.

## Signals

- Structured JSON application logs
- Agent execution trace with elapsed time
- Query execution timing
- Result row and column counts
- Token usage estimates
- Audit event log
- Governance status
- Validation status and block reasons

## Audit Log

Audit records are written to `monitoring/audit.log` as JSON lines.

Example:

```json
{"event_type":"text_to_sql_query","session_id":"demo","role":"analyst","validation_status":"approved","governance_status":"approved"}
```

## Production Monitoring

Recommended production integrations:

- OpenTelemetry traces for each agent step
- Prometheus metrics for latency, blocked queries, approvals, and failures
- Centralized log export to CloudWatch, Datadog, OpenSearch, or Loki
- Alerting on unsafe query attempts and execution failures
- Dashboards for model usage, token cost, and query quality
