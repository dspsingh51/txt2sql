# Example Business Queries

- Show top 5 revenue generating regions
- Why did sales decline in Q2?
- Compare monthly operational costs
- Find customer churn trends
- Show product-wise growth analysis
- Generate executive KPI summary
- Find anomalies in operational expenses
- Which departments exceeded budget?
- Compare incidents by region and service line
- What is the relationship between churn and NPS?

## Expected SQL Example

```sql
SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC
LIMIT 5;
```
