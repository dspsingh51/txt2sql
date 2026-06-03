from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="Enterprise AI Text-to-SQL",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .main .block-container { padding-top: 1.25rem; max-width: 1480px; }
        div[data-testid="stMetricValue"] { font-size: 1.45rem; }
        .status-approved { color: #176b45; font-weight: 700; }
        .status-blocked { color: #a73535; font-weight: 700; }
        .status-review { color: #8a5a00; font-weight: 700; }
        code { white-space: pre-wrap !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def call_api(path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{API_BASE_URL}{path}"
    if method == "POST":
        response = requests.post(url, json=payload, timeout=30)
    else:
        response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def render_chart(results: list[dict[str, Any]], spec: dict[str, Any]) -> None:
    if not results:
        st.info("No result rows available for visualization.")
        return
    dataframe = pd.DataFrame(results)
    chart_type = spec.get("type")
    x_axis = spec.get("x")
    y_axis = spec.get("y")
    if chart_type == "line" and x_axis and y_axis:
        figure = px.line(dataframe, x=x_axis, y=y_axis, markers=True, title=spec.get("title"))
        st.plotly_chart(figure, use_container_width=True)
    elif chart_type == "bar" and x_axis and y_axis:
        figure = px.bar(dataframe, x=x_axis, y=y_axis, title=spec.get("title"))
        st.plotly_chart(figure, use_container_width=True)
    else:
        st.dataframe(dataframe, use_container_width=True, hide_index=True)


def render_status(validation: dict[str, Any], governance: dict[str, Any]) -> None:
    status = governance.get("status", validation.get("status"))
    css_class = "status-approved" if status == "approved" else "status-review" if "approval" in status else "status-blocked"
    st.markdown(f"<span class='{css_class}'>{status.replace('_', ' ').title()}</span>", unsafe_allow_html=True)
    st.caption(governance.get("reason", ""))
    reasons = validation.get("reasons") or []
    if reasons:
        for reason in reasons:
            st.warning(reason)


def render_schema_viewer() -> None:
    try:
        schema = call_api("/schema")
    except Exception as exc:
        st.error(f"Unable to load schema: {exc}")
        return
    for table_name, metadata in schema.items():
        with st.expander(f"{table_name} - {metadata['business_domain']}", expanded=False):
            st.write(metadata["description"])
            st.dataframe(pd.DataFrame(metadata["columns"]), use_container_width=True, hide_index=True)


def render_history(session_id: str) -> None:
    try:
        history = call_api(f"/history/{session_id}").get("history", [])
    except Exception:
        history = []
    if not history:
        st.caption("No conversation history for this session yet.")
        return
    for item in reversed(history[-8:]):
        with st.expander(item.get("question", "Previous query"), expanded=False):
            st.code(item.get("sql", ""), language="sql")
            st.caption(item.get("summary", ""))


with st.sidebar:
    st.title("Enterprise AI SQL")
    role = st.selectbox("Role", ["analyst", "executive", "finance", "support", "sales"], index=0)
    session_id = st.text_input("Session", value="portfolio-demo")
    require_approval = st.toggle("Simulate approval workflow", value=False)
    st.divider()
    st.subheader("Schema")
    render_schema_viewer()
    st.divider()
    st.subheader("History")
    render_history(session_id)

st.title("Natural Language Analytics Workbench")
st.caption("Governed text-to-SQL with schema-aware agents, validation, execution tracing, and business insight generation.")

examples = [
    "Show top 5 revenue generating regions",
    "Why did sales decline in Q2?",
    "Compare monthly operational costs",
    "Find customer churn trends",
    "Show product-wise growth analysis",
    "Generate executive KPI summary",
    "Find anomalies in operational expenses",
]

selected_example = st.selectbox("Example business questions", examples)
question = st.text_area("Business question", value=selected_example, height=92)

run = st.button("Run governed analytics query", type="primary", use_container_width=False)

if run and question.strip():
    with st.spinner("Running agent workflow"):
        try:
            response = call_api(
                "/query",
                method="POST",
                payload={
                    "question": question,
                    "role": role,
                    "session_id": session_id,
                    "require_approval": require_approval,
                },
            )
        except Exception as exc:
            st.error(f"Query failed: {exc}")
            st.stop()

    metrics = response["metrics"]
    execution = metrics.get("execution", {})
    metric_cols = st.columns(4)
    metric_cols[0].metric("Workflow ms", metrics.get("workflow_elapsed_ms", 0))
    metric_cols[1].metric("Execution ms", execution.get("elapsed_ms", 0))
    metric_cols[2].metric("Rows", execution.get("row_count", 0))
    metric_cols[3].metric("Tokens est.", metrics.get("token_usage", {}).get("total_tokens_estimate", 0))

    left, right = st.columns([1.05, 1])
    with left:
        st.subheader("Generated SQL")
        st.code(response["sql"], language="sql")
        st.subheader("Validation And Governance")
        render_status(response["validation"], response["governance"])
        st.subheader("Business Insight")
        st.write(response["summary"])
        st.write(response["explanation"])
        st.subheader("Recommendations")
        for recommendation in response["recommendations"]:
            st.write(f"- {recommendation}")

    with right:
        st.subheader("Results")
        results = response["results"]
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
        else:
            st.info("No rows executed or returned. Check validation and governance status.")
        st.subheader("Visualization")
        render_chart(results, response["visualization"])

    trace_tab, schema_tab, raw_tab = st.tabs(["Workflow Trace", "Schema Context", "Raw Response"])
    with trace_tab:
        trace_df = pd.DataFrame(response["trace"])
        st.dataframe(trace_df, use_container_width=True, hide_index=True)
    with schema_tab:
        st.json(response["schema_context"])
    with raw_tab:
        st.json(response)
else:
    st.info("Choose an example or enter a business question, then run the governed analytics workflow.")
