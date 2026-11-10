# Spatial Functions (Locked)

Row-level spatial functions. Version-gated. All require compatible datatypes (Geographic role or spatial field).

## Point / Line Construction

| Function | Signature | Return | Version |
|---|---|---|---|
| MAKEPOINT | `MAKEPOINT(latitude, longitude, [SRID])` | Geometry | 2019.2+ |
| MAKELINE | `MAKELINE(spatial1, spatial2)` | Geometry | 2019.2+ |

## Spatial Predicates

| Function | Signature | Return | Version |
|---|---|---|---|
| INTERSECTS | `INTERSECTS(spatial1, spatial2)` | Boolean | 2019.2+ |
| BUFFER | `BUFFER(geometry, distance, unit)` | Geometry | 2024.1+ |

**BUFFER units:** 'miles', 'kilometers', 'meters', 'feet'. Case-insensitive.

## Distance and Measurement

| Function | Signature | Return | Version |
|---|---|---|---|
| DISTANCE | `DISTANCE(spatial1, spatial2, unit)` | Number | 2019.2+ |
| AREA | `AREA(polygon, unit)` | Number | 2020.4+ |
| LENGTH | `LENGTH(line, unit)` | Number | 2020.4+ |
| CENTROID | `CENTROID(geometry)` | Geometry | 2022.4+ |

## Coordinate Extraction

| Function | Signature | Return | Version |
|---|---|---|---|
| X | `X(point)` | Number | Extract longitude. |
| Y | `Y(point)` | Number | Extract latitude. |

## Common Patterns

- Distance between customer and store: `DISTANCE(MAKEPOINT([Cust Lat], [Cust Lon]), [Store Location], 'miles')`.
- Points within X miles: `DISTANCE(MAKEPOINT([Lat], [Lon]), MAKEPOINT([Target Lat], [Target Lon]), 'miles') < 25`.
- Buffer around a point: `BUFFER(MAKEPOINT([Lat], [Lon]), 5, 'miles')`.
- Territory containment: `INTERSECTS(MAKEPOINT([Lat], [Lon]), [Territory Polygon])`.

## Common Anti-Patterns

- Passing city name to MAKEPOINT (needs numeric lat/lon).
- Missing unit argument on DISTANCE, AREA, LENGTH.
- BUFFER with negative distance (results vary by connector).
- Nested BUFFER on already-buffered geometries (perf concern).

## Version Notes

- MAKEPOINT, MAKELINE, DISTANCE, INTERSECTS: Desktop 2019.2+.
- AREA, LENGTH: Desktop 2020.4+.
- CENTROID: Desktop 2022.4+.
- BUFFER: Desktop 2024.1+.

If the user's Desktop version is older, refuse the write per HC#2 or route to alternative logic (e.g., pre-computed distance columns in the data source).
