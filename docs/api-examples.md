# API Examples

## Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Show top 5 revenue generating regions\",\"role\":\"analyst\",\"session_id\":\"demo\"}"
```

## Schema

```bash
curl http://localhost:8000/api/v1/schema
```

## History

```bash
curl http://localhost:8000/api/v1/history/demo
```

## Connection

```bash
curl http://localhost:8000/api/v1/connection
```
