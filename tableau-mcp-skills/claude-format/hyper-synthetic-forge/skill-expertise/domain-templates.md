# Domain Templates

Domain patterns for description-based generation.

## Domain Template Patterns

Unless a domain below says otherwise, dates use the default weekday weights (Mon-Fri 16% each, Sat-Sun 10% each).

**E-Commerce:** Customers, Products, Orders, Order_Items. Weekend order spikes (weekends 15% each, weekdays 14% each), log-normal amounts (avg ~$50-200), Pareto product popularity (20% of products = 80% of sales), 80/20 repeat customers. Seasonality: Q4 holiday spike +40%, January dip -25%.

**Healthcare:** Patients, Visits, Providers. Age skews older (mean ~55), business-hours visits, chronic condition repeats (20% patients = 60% visits), local geography concentration. Seasonality: flu season Oct-Feb +30%.

**Financial Services:** Accounts, Transactions. Log-normal amounts (avg ~$150), weekday-heavy transactions (Mon-Fri 18% each, Sat-Sun 5% each), realistic balance ranges by account type (checking: $500-15K, savings: $1K-100K). Trend: +5% YoY transaction volume growth.

**SaaS/B2B:** Companies, Users, Usage. Log-normal company size (avg ~200 employees), ARR correlated with size ($50K-$5M), business-hours usage patterns, 30% of users are power users. Trend: +20% YoY user growth.

**Supply Chain:** Suppliers, Products, Shipments, Inventory. Lead times by region (domestic 3-7 days, international 14-45 days), seasonal demand curves, warehouse capacity 70-95% utilization. Seasonality: pre-holiday inventory build Aug-Oct.

**HR/People:** Employees, Departments, Performance Reviews. Tenure log-normal (avg ~4 years), salary bands by level (L1: $50-70K, L2: $70-100K, L3: $100-150K), review scores normal (mean 3.5/5). Trend: +3% annual compensation growth.
