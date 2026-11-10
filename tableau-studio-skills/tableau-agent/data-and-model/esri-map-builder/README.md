# Esri Map Builder

Builds a Tableau workbook (`.twb`) with one map layer per layer of an ArcGIS REST service (MapServer or FeatureServer). Layers are stacked on a single sheet, each as its own Esri datasource, and tables without geometry become plain datasources.

**Example:** You say "Map all the layers from https://mapdata.tucsonaz.gov/arcgis/rest/services/ParkTucson." The skill lists the three services, builds a workbook with six map layers and two tables, and tells you to run **Extract > Refresh All Extracts**.

## Requirements

- **Local Python is required.** The skill runs scripts on your machine. `check_driver.py` and `list_layers.py` use only the Python standard library. `gen_workbook.py` also needs the `tableauhyperapi` package; if no interpreter has it, the Agent asks once before creating a virtual environment and running `pip install tableauhyperapi`. If you decline, the skill stops. It never installs Python itself.
- **The Esri JDBC driver must be installed by you.** The skill checks for the jar and, if it is missing, points you to the download page (https://downloads.tableau.com/drivers/esri/esri-jdbc-driver-3.2.0.jar). It never downloads, copies or bundles the driver. No Studio restart is needed after you install it.
- Public ArcGIS REST services only. Services behind sign-in are out of scope.

## What it does

- Explores a service, a folder or an ArcGIS Online org (read-only) and groups layers by service, group layer and name prefix, so you can pick by meaning.
- Takes several services at once. Service names are added to layer names only when they would otherwise collide.
- Writes the workbook and one-row placeholder `.hyper` extracts under your Tableau Repository (`Workbooks/` and `Datasources/`). Nothing existing is changed.
- Names the first sheet as a reminder to refresh extracts, and sets a tooltip of the layer name plus `<All Fields>`.

## After it runs

The layers are empty placeholders until you run **Extract > Refresh All Extracts** and save. This is expected: the Esri connector is extract-only.

## When to use it

- "Map this ArcGIS service," "Esri layers in Tableau," "recreate this ArcGIS map in Tableau."
- A MapServer or FeatureServer URL, or a folder or org URL plus a theme such as "voting" or "flood."

## When NOT to use it

- A single Esri layer that is already connected.
- Shapefiles or GeoJSON files.
- Editing an existing workbook's map layers.
- Choosing a connector in general (use `data-source-connector`).

## Known issues

- The Agent panel can close when the skill opens the finished workbook; open it with **File > Open** if that happens.
- Raster layers are skipped, with a note.
- Technical reference notes (XML details, server quirks, refresh behavior) are in `skill-expertise/ESRI-MAPSERVER-TO-TWB.md`.
