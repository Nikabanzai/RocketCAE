from pathlib import Path

p = Path("README.md")
t = p.read_text(encoding="utf-8")
if "Formerly developed" not in t[:1200]:
    lines = t.splitlines()
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and line.startswith("# "):
            out.append("")
            out.append(
                "> **Formerly developed under the working name RocketCAE.** "
                "Renamed to **PyCHEMA** to honor the 2017 CHEMA project and avoid "
                "confusion with the unrelated PyPI package "
                "[RocketCEA](https://pypi.org/project/rocketcea/) and NASA's "
                "`cea` package."
            )
            inserted = True
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("readme notice added")
else:
    print("readme ok")

for f in [Path("pyproject.toml"), Path("src/pychema/__init__.py"), Path("CITATION.cff")]:
    t = f.read_text(encoding="utf-8")
    f.write_text(t.replace("0.1.0", "0.2.0"), encoding="utf-8")
print("version 0.2.0")

cl = Path("CHANGELOG.md")
t = cl.read_text(encoding="utf-8")
if "0.2.0" not in t:
    entry = """## [0.2.0] — 2026-07-09

### Changed
- **Rebranded** project from working name RocketCAE to **PyCHEMA** (package `pychema`, CLI `pychema`)
- Clarifies no relation to PyPI `rocketcea` (RocketCEA); uses official NASA `cea`

### Added
- Rename notice in README; updated docs/citations for PyCHEMA

"""
    if t.lstrip().startswith("#"):
        # after first line
        parts = t.split("\n", 1)
        t = parts[0] + "\n\n" + entry + (parts[1] if len(parts) > 1 else "")
    else:
        t = entry + t
    cl.write_text(t, encoding="utf-8")
    print("changelog updated")

# Write announcements file
ann = Path("docs/ANNOUNCEMENTS.md")
ann.write_text(ANNOUNCE, encoding="utf-8")
print("announcements written")
