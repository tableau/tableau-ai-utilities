#!/usr/bin/env python3
"""Check that the Esri JDBC driver is installed in Tableau's Drivers folder.

Standard library only (Python 3.9+), so it runs before any venv exists.
Tableau scans every .jar in the folder, so the filename does not matter: a jar counts as
the Esri driver when its MANIFEST has Implementation-Title: esri-jdbc-driver.

Exit 0: found (prints path and version). Exit 1: not found (prints where to get it).
"""
import glob, os, sys, zipfile

DOWNLOAD_URL = "https://downloads.tableau.com/drivers/esri/esri-jdbc-driver-3.2.0.jar"


def drivers_dirs():
    if sys.platform == "darwin":
        return [os.path.expanduser("~/Library/Tableau/Drivers")]
    if sys.platform.startswith("win"):
        return [os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Tableau", "Drivers")]
    return ["/opt/tableau/tableau_driver/jdbc"]


def manifest(jar):
    try:
        with zipfile.ZipFile(jar) as z:
            text = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
    except (OSError, KeyError, zipfile.BadZipFile):
        return {}
    return dict(l.split(": ", 1) for l in text.splitlines() if ": " in l)


def main():
    dirs = drivers_dirs()
    for d in dirs:
        for jar in sorted(glob.glob(os.path.join(d, "*.jar"))):
            m = manifest(jar)
            if m.get("Implementation-Title") == "esri-jdbc-driver":
                print(f"Esri driver found: {jar} (version {m.get('Implementation-Version', 'unknown')})")
                return 0
    print("Esri JDBC driver NOT found in: " + ", ".join(dirs))
    print(f"Download it from: {DOWNLOAD_URL}")
    print(f"Save the .jar into {dirs[0]} then tell the agent it is installed (no Studio restart needed).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
