"""
Project Structure Validator
Run this before the full automation to verify everything is set up correctly.
"""
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR / "project"

def validate():
    print("=" * 60)
    print("PROJECT VIDEO AUTOMATION — STRUCTURE VALIDATOR")
    print("=" * 60)

    # Check project folder exists
    if not PROJECT_DIR.exists():
        print(f"\n[FAIL] Project folder NOT found: {PROJECT_DIR}")
        print("\nPlease create a 'project' folder and put your files inside it.")
        print("Expected structure:")
        print("  project/")
        print("    main.py")
        print("    README.md")
        print("    src/")
        print("      app.py")
        return 1

    print(f"\n[OK] Project folder found: {PROJECT_DIR}")

    # Collect files
    files = []
    for path in PROJECT_DIR.rglob("*"):
        if path.is_file():
            files.append(path)

    if not files:
        print("[FAIL] No files found inside project/ folder!")
        return 1

    print(f"[OK] Found {len(files)} file(s) inside project/")
    print("\n" + "-" * 60)
    print("PROJECT FILES:")
    print("-" * 60)

    py_files = []
    for f in sorted(files, key=lambda p: str(p.relative_to(PROJECT_DIR))):
        rel = f.relative_to(PROJECT_DIR)
        size = f.stat().st_size
        print(f"  {rel}  ({size:,} bytes)")
        if f.suffix.lower() == ".py":
            py_files.append(f)

    # Check for main.py
    entrypoint = PROJECT_DIR / "main.py"
    if entrypoint.exists():
        print(f"\n[OK] Entry point found: main.py")
    else:
        print(f"\n[WARN] Entry point 'main.py' NOT found.")
        print("       If your main file has a different name, update ENTRYPOINT")
        print("       in whole_project_automation.py")

    # Validate Python syntax
    if py_files:
        print("\n" + "-" * 60)
        print("PYTHON SYNTAX CHECK:")
        print("-" * 60)
        import ast
        all_ok = True
        for f in py_files:
            rel = f.relative_to(PROJECT_DIR)
            try:
                ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
                print(f"  [OK]   {rel}")
            except SyntaxError as e:
                print(f"  [FAIL] {rel}: {e}")
                all_ok = False

        if not all_ok:
            print("\n[FAIL] Some Python files have syntax errors. Fix them first.")
            return 1

    print("\n" + "=" * 60)
    print("ALL CHECKS PASSED!")
    print("=" * 60)
    print("\nYou can now run:")
    print("  python whole_project_automation.py --dry-run")
    print("  python whole_project_automation.py")
    return 0

if __name__ == "__main__":
    sys.exit(validate())
