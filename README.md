# ROM Translator — GBA Edition

Initial Linux/Windows buildable starter for ROM Translator.

## Included in this starter

- PySide6 desktop GUI.
- Read-only GBA ROM header inspection: title, game code, maker code, version and header checksum.
- Heuristic scan for long `0xFF` runs that may be candidate free space.
- Automated tests.
- GitHub Actions builds Linux and Windows desktop artifacts on pushes, pull requests, published releases, or manual workflow runs.

## Local setup

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
PYTHONPATH=src python -m romtran.main
```

## GitHub Actions

After this repository contains the workflow file, open **Actions → Romtran Automated Build**. Pushes and pull requests trigger builds automatically; `workflow_dispatch` allows manual runs. Download artifacts from the completed workflow run.

**Important limitations:** this is a buildable starter, not yet a full Thai ROM translation suite. A run of `0xFF` bytes is only a candidate and is not proof that the region is safe to use. This code does not patch or expand ROM files. The workflow creates Linux and Windows desktop builds, not an Android APK; Android packaging/device validation is a separate future task.
