# Preference-Flag: Disable Auto Phone-Layout Generation

Numbered Desktop steps for authors who never wanted a phone layout auto-generated on new dashboards. Delivered when Preference-flag mode fires (P13 trigger) or when the author explicitly asks to disable auto-generation.

## Confirm intent first

Before shipping these steps, confirm:

> "You want to stop Tableau from auto-generating a phone layout on new dashboards going forward. Not delete existing phone layouts from workbooks you have already published."

If the author actually wants to delete an existing phone layout, use the Existing-layout removal steps at the bottom instead (or in addition).

## Path A. Disable on new dashboards (per-dashboard, in Desktop)

The auto-generation setting is a per-dashboard property, not a global Desktop preference. To prevent it going forward, use one of these two approaches:

### Approach 1. Remove phone layout as each dashboard is created

1. Create the dashboard normally.
2. In the Dashboard pane on the left, look for the **Device Preview** section (below Size).
3. If the Device Preview shows a phone layout listed, click the phone layout entry.
4. Right-click the phone layout → **Remove Layout**.
5. Confirm removal.
6. Save the workbook. Tableau will not auto-generate the phone layout again unless the author explicitly adds one via Device Preview.

### Approach 2. Start from a template workbook without phone layouts

1. Create a template workbook: build one dashboard, remove its phone layout per Approach 1, save the workbook as a template file (.twbx or .twb).
2. Store the template in a shared location for the team.
3. For each new project: open the template, save-as under the new project name, build inside.
4. Any dashboard created inside the template starts without a phone layout by default.

## Path B. Bulk remove phone layouts across many existing dashboards

For a workbook with multiple dashboards that already have unwanted phone layouts:

1. Open the workbook in Desktop.
2. For each dashboard (repeat these steps):
   - Navigate to the dashboard.
   - In the Dashboard pane → Device Preview section → click the phone layout entry.
   - Right-click → **Remove Layout**.
3. Save the workbook.
4. Republish to Server/Cloud if the workbook was already published.

## Path C. Server/Cloud considerations

- Removing the phone layout in Desktop and republishing removes it from Server/Cloud on the next publish.
- Mobile users viewing the workbook after republish see the desktop layout instead of a phone layout.
- If the workbook was already viewed on Mobile with a cached phone layout, the Mobile app will refresh to the desktop layout after next open.

## Optional cleanup: audit existing phone layouts before removal

The author may want to keep some phone layouts. Offer:

> "Before removing all phone layouts, would you like me to run Audit mode on each one? Some may be worth keeping if they were hand-tuned; others were probably auto-generated and are ship-broken. Audit will tell you which."

If yes, run Audit mode on each phone layout in the workbook, then let the author decide which to keep and which to remove.

## Author-communication template (optional)

If the author is removing phone layouts from a workbook already in production, they may want to notify Mobile users. Suggest:

> "The phone layout for [dashboard name] has been retired. Mobile users will now see the desktop layout, which may require horizontal scrolling on phone-sized screens. If you rely on the phone layout, let me know and I can rebuild it as an intentional design pass."

## What this skill does NOT do

- **Does not flip the setting.** The skill cannot mutate the workbook (HC-1, HC-5).
- **Does not remove phone layouts across a Server site programmatically.** No REST API path.
- **Does not prevent Cloud-published workbooks from auto-generating on future republish.** The Desktop workbook is the source of truth. Republishing without a phone layout is what removes it from Cloud.

## Version notes

- **Tableau 2020.1 and later.** Device Preview and per-dashboard phone layout removal available as documented above.
- **Older versions.** Device Preview UI may look different. The Layout pane in the Dashboard section still exposes phone-layout removal via right-click.
