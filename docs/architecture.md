# Architecture

The Enterprise AI Text-to-SQL Platform is organized around governed agent orchestration. Each agent has a narrow responsibility, emits trace metadata, and passes structured state to the next step.

## System Architecture

```mermaid
flowchart LR
    User["Business User"] --> Streamlit["Streamlit Analytics Workbench"]
    Streamlit --> FastAPI["FastAPI API Layer"]
    FastAPI --> Workflow["TextToSQLWorkflow"]
    Workflow --> Agents["AI Agent Modules"]
    Agents --> Validation["SQL Validation And Governance"]
    Validation --> Executor["Read-Only Query Executor"]
    Executor --> SQLite["SQLite Demo Database"]
    Executor -. production .-> Warehouse["PostgreSQL / Warehouse Read Replica"]
    Workflow --> Memory["Redis / Local Memory"]
    Workflow --> Audit["Audit Log"]
    Workflow --> Logs["Structured JSON Logs"]
```

## Agent Orchestration Workflow

```mermaid
flowchart TD
    Start["User Question"] --> Memory["Memory Agent"]
    Memory --> Intent["Intent Understanding Agent"]
    Intent --> Schema["Schema Context Agent"]
    Schema --> SQLGen["SQL Generation Agent"]
    SQLGen --> Validation["SQL Validation Agent"]
    Validation --> Governance{"Governance Decision"}
    Governance -->|Approved| Execute["Query Execution Agent"]
    Governance -->|Approval Required| BlockExecution["Hold For Approval"]
    Governance -->|Blocked| Blocked["Return Safe Failure"]
    Execute --> Insights["Analytics Insight Agent"]
    BlockExecution --> Insights
    Blocked --> Insights
    Insights --> Viz["Visualization Agent"]
    Viz --> Remember["Persist Memory And Audit"]
    Remember --> Response["Structured Response"]
```

## Query Lifecycle

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit
    participant API as FastAPI
    participant WF as Workflow
    participant DB as Read-Only DB
    participant OBS as Observability

    U->>UI: Ask business question
    UI->>API: POST /api/v1/query
    API->>WF: Run agent workflow
    WF->>WF: Infer intent and retrieve schema
    WF->>WF: Generate SQL
    WF->>WF: Validate SQL and enforce role policies
    alt approved
        WF->>DB: Execute SELECT query
        DB-->>WF: Result rows
    else blocked or approval required
        WF-->>WF: Skip execution
    end
    WF->>OBS: Write trace and audit event
    WF-->>API: SQL, results, insights, chart spec
    API-->>UI: Structured response
    UI-->>U: Results, summary, trace, visualization
```

## Secure SQL Validation Flow

```mermaid
flowchart TD
    SQL["Generated SQL"] --> Normalize["Normalize Statement"]
    Normalize --> Single{"Single Statement?"}
    Single -->|No| Block["Block Query"]
    Single -->|Yes| ReadOnly{"SELECT Or WITH?"}
    ReadOnly -->|No| Block
    ReadOnly -->|Yes| Keywords{"Unsafe Keywords?"}
    Keywords -->|Yes| Block
    Keywords -->|No| Role{"Role Can Access Tables?"}
    Role -->|No| Block
    Role -->|Yes| Sensitive{"Sensitive Columns Or Broad Scan?"}
    Sensitive -->|Yes| Approval["Approval Required"]
    Sensitive -->|No| Approved["Approved For Read-Only Execution"]
```

## Deployment Architecture

```mermaid
flowchart TB
    Internet["Enterprise Users"] --> ALB["Load Balancer / Ingress"]
    ALB --> UI["Streamlit Container"]
    ALB --> API["FastAPI Container"]
    API --> Redis["Redis Memory"]
    API --> DB["PostgreSQL Read Replica / Warehouse"]
    API --> Secrets["Secrets Manager"]
    API --> Logs["Centralized Logs"]
    API --> Metrics["Metrics And Traces"]
    Logs --> SIEM["Security Monitoring"]
    Metrics --> Dashboards["Operations Dashboards"]
```

## Design Principles

- Keep AI reasoning modular and observable.
- Validate before execution, every time.
- Default to read-only execution.
- Make role and approval decisions explicit.
- Treat generated SQL as untrusted until validated.
- Preserve workflow traces for debugging and governance.
