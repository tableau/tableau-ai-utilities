# Auth Patterns (Locked)

Locked decision-tree rubric for auth choice. Never fabricate an auth pattern. Match the source type plus the environment description to a row; if no row matches cleanly, ask the one clarifying question.

## Decision Tree

| Source Type | Environment | Recommended Auth | Why |
|---|---|---|---|
| Cloud warehouse (Snowflake, Databricks, BigQuery, Redshift, Synapse) | SSO / Okta / Azure AD | OAuth | Central identity, no shared credentials, refresh handled by provider. |
| Cloud warehouse | Service account with rotation | Key-pair (Snowflake) or PAT (Databricks) | Machine-to-machine credential, rotatable, avoids password-in-config. |
| Cloud warehouse | Personal developer credentials | Username + password | Simplest for prototype work; upgrade to OAuth before publishing. |
| Relational DB (Postgres, MySQL, SQL Server, Oracle) | Kerberos / Windows integrated | Windows Authentication or Kerberos | Zero-credential-in-config; matches enterprise SSO. |
| Relational DB | Service account | Username + password | Standard for scheduled refresh service accounts. |
| Relational DB | Personal developer credentials | Username + password | Prototype only. |
| Salesforce | Standard | OAuth | Salesforce standard; MFA-compliant. |
| Salesforce Data Cloud | Standard | OAuth Client Credentials | Machine-to-machine, matches Data Cloud + Tableau Next pattern. |
| Google Sheets / Google Analytics / BigQuery | Personal Google account | OAuth | Google's only supported pattern. |
| Google Sheets / Google Analytics / BigQuery | Service account | Service Account JSON key | Machine-to-machine, avoids user-consent screen. |
| Marketo | Standard | Client ID + Client Secret | Marketo standard REST API auth. |
| ServiceNow | Standard | OAuth or username + password | OAuth preferred; password fallback for older instances. |
| File-based (Excel, CSV, JSON, PDF) | Local file | None | File-based; no auth required. |
| File-based | Network share (SMB, DFS) | Windows / share credentials | OS-level, not Tableau-managed. |
| MongoDB | Standard | Username + password with SCRAM-SHA-256 | MongoDB BI Connector standard. |

## Escalation Notes

- If the user says "we use MFA" and the row above recommends password, upgrade to OAuth if the source supports it, or PAT/token if not.
- If the user says "this needs to work for scheduled refresh," prefer key-pair, PAT, or service-account JSON over interactive OAuth (interactive OAuth breaks on refresh without a refresh-token pattern).
- If the environment is federated via a broker (Okta, Ping, Azure AD B2B), OAuth is always the recommendation regardless of source type when the source supports it.

## Hybrid Environments (Locked)

Environments that mix identity patterns require a locked escalation. Never invent a hybrid; look up the row.

| Hybrid Signature | Recommendation | Rationale |
|---|---|---|
| SSO-federated service account (Okta federates to a service account credential) | Key-pair or PAT for machine-to-machine; OAuth for interactive users. Split by workflow. | Interactive OAuth doesn't survive scheduled refresh; the service account needs a durable credential. |
| VPN-required source with cloud-hosted identity | Password or PAT auth AT the source, with VPN client active BEFORE opening Desktop's connection dialog. | Cloud IdP can't reach a VPN-only source; auth must be source-native. |
| Cross-tenant SaaS (e.g., partner Salesforce org) | OAuth Connected App with the partner's tenant, not the primary tenant's default OAuth. | Standard OAuth targets the wrong tenant; explicit Connected App required. |
| Shared machine, per-user credentials | Windows Authentication or Kerberos when supported; personal credentials via Desktop's saved-connection store otherwise. | Shared machines cannot hold a shared PAT without leaking; per-user auth is the only safe pattern. |
| Bastion or jump-host access | ODBC generic through the bastion's port-forward. Native connectors typically fail because the bastion masks the actual source. | Native connectors expect direct source reachability; port-forwards break connector-specific reachability probes. |

If a hybrid doesn't match any row above, ask the one clarifier or refuse per HC#3 rather than fabricating.

## Refuse to Fabricate

If none of the rows above matches the source + environment cleanly, do one of:
1. Ask the one clarifying question (e.g., "Is this scheduled refresh or interactive?").
2. Report "no matching auth pattern in the current rubric; consult your DBA or the source vendor's docs" and stop.

Never invent an auth pattern name (e.g., "Snowflake key-pair-with-JWT-rotation" if that's not in the table).
