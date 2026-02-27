#!/usr/bin/env python3
"""Inspect an installed skill and output a structured report.

Usage:
    inspect_skill.py <skill-name>
    inspect_skill.py --list
    inspect_skill.py --all

Scans ~/.claude/skills/<skill-name>/ and reports:
- Frontmatter (name, description)
- File tree with sizes
- Scripts inventory (highlights executable code)
- Security observations for third-party skills
"""

import sys
import os
import re
from pathlib import Path

SKILLS_DIR = Path.home() / ".claude" / "skills"


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def file_tree(root: Path, prefix: str = "") -> list[str]:
    lines = []
    entries = sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name))
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            ext = "    " if is_last else "\u2502   "
            lines.extend(file_tree(entry, prefix + ext))
        else:
            size = entry.stat().st_size
            if size < 1024:
                sz = f"{size}B"
            elif size < 1024 * 1024:
                sz = f"{size / 1024:.1f}KB"
            else:
                sz = f"{size / (1024 * 1024):.1f}MB"
            lines.append(f"{prefix}{connector}{entry.name} ({sz})")
    return lines


def inspect_scripts(skill_dir: Path) -> list[str]:
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return []
    notes = []
    for f in sorted(scripts_dir.rglob("*")):
        if f.is_file():
            rel = f.relative_to(skill_dir)
            is_exec = os.access(f, os.X_OK)
            ext = f.suffix.lower()
            flags = []
            if is_exec:
                flags.append("executable")
            if ext in (".py", ".sh", ".bash", ".zsh", ".rb", ".js", ".ts"):
                flags.append(f"code:{ext}")
            # Quick content scan for risky patterns
            try:
                content = f.read_text(errors="replace")[:8000]
                risky = []
                if re.search(r"(rm\s+-rf|rmdir|shutil\.rmtree)", content):
                    risky.append("file-deletion")
                if re.search(r"(curl|wget|requests\.(get|post)|fetch\(|urllib)", content):
                    risky.append("network-access")
                if re.search(r"(subprocess|os\.system|exec\(|eval\()", content):
                    risky.append("shell-exec")
                if re.search(r"(password|secret|token|api.key)", content, re.IGNORECASE):
                    risky.append("credential-ref")
                if re.search(r"(open\(.*(w|a)\)|write\(|>>)", content):
                    risky.append("file-write")
                if risky:
                    flags.append(f"patterns:[{','.join(risky)}]")
            except Exception:
                flags.append("unreadable")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            notes.append(f"  {rel}{flag_str}")
    return notes


def inspect_skill(name: str) -> None:
    skill_dir = SKILLS_DIR / name
    if not skill_dir.is_dir():
        print(f"Error: skill '{name}' not found at {skill_dir}")
        sys.exit(1)

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(f"Error: {skill_md} not found")
        sys.exit(1)

    text = skill_md.read_text()
    fm = parse_frontmatter(text)

    print(f"=== Skill: {fm.get('name', name)} ===\n")

    # Description
    desc = fm.get("description", "(no description)")
    print(f"Description:\n  {desc}\n")

    # File tree
    print("File tree:")
    for line in file_tree(skill_dir):
        print(f"  {line}")
    print()

    # Scripts analysis
    scripts = inspect_scripts(skill_dir)
    if scripts:
        print("Scripts analysis:")
        for s in scripts:
            print(s)
        print()

    # References
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        ref_files = list(refs_dir.rglob("*"))
        ref_files = [f for f in ref_files if f.is_file()]
        if ref_files:
            print("References:")
            for f in sorted(ref_files):
                print(f"  {f.relative_to(skill_dir)}")
            print()

    # Assets
    assets_dir = skill_dir / "assets"
    if assets_dir.is_dir():
        asset_files = list(assets_dir.rglob("*"))
        asset_files = [f for f in asset_files if f.is_file()]
        if asset_files:
            print("Assets:")
            for f in sorted(asset_files):
                print(f"  {f.relative_to(skill_dir)}")
            print()

    # Body preview (first 20 non-empty lines after frontmatter)
    body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.DOTALL)
    body_lines = [l for l in body.splitlines() if l.strip()][:20]
    if body_lines:
        print("SKILL.md body preview (first 20 lines):")
        for l in body_lines:
            print(f"  {l}")
        print()


def list_skills() -> None:
    if not SKILLS_DIR.is_dir():
        print(f"No skills directory found at {SKILLS_DIR}")
        sys.exit(1)
    skills = sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())
    if not skills:
        print("No skills installed.")
        return
    print(f"Installed skills ({len(skills)}):\n")
    for name in skills:
        skill_md = SKILLS_DIR / name / "SKILL.md"
        fm = parse_frontmatter(skill_md.read_text())
        desc = fm.get("description", "(no description)")
        # Truncate long descriptions
        if len(desc) > 120:
            desc = desc[:117] + "..."
        print(f"  {name}")
        print(f"    {desc}\n")


def inspect_all() -> None:
    if not SKILLS_DIR.is_dir():
        print(f"No skills directory found at {SKILLS_DIR}")
        sys.exit(1)
    skills = sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())
    for i, name in enumerate(skills):
        if i > 0:
            print("\n" + "=" * 60 + "\n")
        inspect_skill(name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: inspect_skill.py <skill-name> | --list | --all")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == "--list":
        list_skills()
    elif arg == "--all":
        inspect_all()
    else:
        inspect_skill(arg)
