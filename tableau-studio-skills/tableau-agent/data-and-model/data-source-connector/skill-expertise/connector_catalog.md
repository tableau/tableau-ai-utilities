# Connector Catalog (Locked)

Locked catalog of Tableau Desktop 2026.2 (Beta) connectors grouped by source type. Never fabricate a connector. If a source isn't listed here, report "no matching Desktop connector, try ODBC generic."

## Cloud Data Warehouses

| Source | Primary Connector | Alternate | Driver Required |
|---|---|---|---|
| Snowflake | Snowflake | ODBC generic | Snowflake ODBC/JDBC driver |
| Databricks | Databricks | ODBC generic | Databricks ODBC driver |
| Google BigQuery | Google BigQuery JDBC | Google BigQuery | Bundled |

*Note: JDBC is listed as primary for BigQuery because it supports custom SQL and legacy project/dataset browsing patterns the native connector doesn't cover; the native "Google BigQuery" connector is the simpler alternate for standard OAuth-only, no-custom-SQL use.*
| Amazon Redshift | Amazon Redshift | ODBC generic | Redshift ODBC driver |
| Azure Synapse | Azure Synapse Analytics | ODBC generic | Bundled |

## Relational Databases

| Source | Primary Connector | Alternate | Driver Required |
|---|---|---|---|
| PostgreSQL (self-hosted or RDS) | PostgreSQL | ODBC generic | PostgreSQL ODBC driver |
| MySQL | MySQL | ODBC generic | MySQL ODBC driver |
| Microsoft SQL Server | Microsoft SQL Server | ODBC generic | Bundled |
| Oracle | Oracle | ODBC generic | Oracle Instant Client |
| SQLite | SQLite | ODBC generic | Bundled |

## File-Based

| Source | Primary Connector | Alternate | Driver Required |
|---|---|---|---|
| Microsoft Excel (.xlsx, .xls) | Excel | — | Bundled |
| CSV / TSV / TXT | Text file | — | Bundled |
| JSON | JSON file | — | Bundled |
| PDF (tables) | PDF file | — | Bundled |
| Statistical file (.sav, .sas7bdat) | Statistical file | — | Bundled |

## Cloud Services

| Source | Primary Connector | Alternate | Driver Required |
|---|---|---|---|
| Salesforce | Salesforce | — | Bundled |
| Salesforce Data Cloud | Salesforce Data Cloud | Salesforce | Bundled |
| Google Sheets | Google Sheets | — | Bundled |
| Google Analytics | Google Analytics | — | Bundled |
| Marketo | Marketo | — | Bundled |
| ServiceNow | ServiceNow ITSM | — | Bundled |

## Other Databases

| Source | Primary Connector | Alternate | Driver Required |
|---|---|---|---|
| MongoDB | MongoDB BI Connector | ODBC generic | MongoDB BI driver |
| Hadoop / Hive | Cloudera Hadoop | ODBC generic | Cloudera Hive ODBC |
| Presto / Trino | Presto | ODBC generic | Presto ODBC driver |
| SAP HANA | SAP HANA | — | SAP HANA client |

## Generic Fallback

If a source is not listed above:
- Recommend ODBC generic with the vendor's official ODBC driver.
- Note that the ODBC path loses connector-specific optimizations (custom SQL support, connector-native auth patterns, published-datasource metadata).

## Deprecated / Retired

- Web Data Connector (WDC): retired in 2024. Recommend a REST-to-file bridge or the Extract API for custom sources.

## Clarifier-Answer to Row Mapping (Locked)

When the intake fires the one clarifier (hosting mode or auth environment), map the answer to a specific row deterministically. Never re-interpret; look up the row.

### Hosting-Mode Answers

| Source | Answer: self-hosted | Answer: cloud-hosted | Answer: on-prem behind VPN |
|---|---|---|---|
| PostgreSQL | PostgreSQL connector, standard | PostgreSQL connector, ensure port allow-listed | PostgreSQL connector, VPN client active first |
| MySQL | MySQL connector | MySQL connector | MySQL connector, VPN active |
| Microsoft SQL Server | Microsoft SQL Server, Windows Auth default | Microsoft SQL Server, cloud-native auth (SQL Auth on Azure SQL) | Microsoft SQL Server, VPN active |
| Oracle | Oracle connector, Instant Client | Oracle connector, Instant Client, cloud-native user | Oracle connector, VPN active |
| MongoDB | MongoDB BI Connector | MongoDB Atlas via BI Connector | MongoDB BI Connector, VPN active |

### Auth-Environment Answers

| Source Type | Answer: SSO/Okta | Answer: service account | Answer: personal credentials |
|---|---|---|---|
| Cloud warehouse (Snowflake, Databricks, BigQuery, Redshift, Synapse) | OAuth | Key-pair or PAT | Username + password |
| Relational DB (Postgres, MySQL, SQL Server, Oracle) | Kerberos/Windows Auth if supported, else OAuth | Username + password | Username + password |
| Salesforce | OAuth | OAuth Client Credentials | OAuth |
| Google Sheets / BigQuery / Analytics | OAuth (user account) | Service Account JSON key | OAuth |

### Ambiguity Resolution

If the clarifier answer is genuinely ambiguous ("depends on the team," "not sure"), pick the safer default:
- For hosting mode: assume self-hosted (more permissive; user can adjust to cloud-hosted if wrong).
- For auth: assume service account (more secure default than personal credentials).

Report the assumed default explicitly in the recommendation so the user can correct.
