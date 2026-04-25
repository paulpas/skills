#!/usr/bin/env python3
"""Generate skills-index.json from all SKILL.md frontmatter."""

import os, re, json, sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
OUTPUT = os.path.join(REPO_ROOT, "skills-index.json")
DOMAINS = ["agent", "cncf", "coding", "trading", "programming"]


def parse_frontmatter(content):
    m = re.match(r"^---\r?\n([\s\S]*?)\r?\n---", content)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip("\"'")
    # parse metadata block
    meta = {}
    in_meta = False
    for line in m.group(1).splitlines():
        if line.strip() == "metadata:":
            in_meta = True
            continue
        if in_meta:
            if line.startswith("  ") or line.startswith("\t"):
                k, _, v = line.strip().partition(":")
                meta[k.strip()] = v.strip().strip("\"'")
            else:
                in_meta = False
    fm["_meta"] = meta
    return fm


index = []
for domain in DOMAINS:
    domain_path = os.path.join(SKILLS_DIR, domain)
    if not os.path.isdir(domain_path):
        continue

    for skill_dir in sorted(os.listdir(domain_path)):
        skill_path = os.path.join(domain_path, skill_dir)
        skill_md = os.path.join(skill_path, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        with open(skill_md, encoding="utf-8") as f:
            content = f.read()
        fm = parse_frontmatter(content)
        meta = fm.get("_meta", {})
        name = fm.get("name", skill_dir)
        description = fm.get("description", f"Skill: {name}")
        domain_from_meta = meta.get("domain", domain)
        triggers_raw = meta.get("triggers", "")
        tags = [t.strip() for t in triggers_raw.split(",") if t.strip()]
        if domain_from_meta not in tags:
            tags.insert(0, domain_from_meta)
        index.append(
            {
                "name": name,
                "description": description,
                "domain": domain_from_meta,
                "tags": tags,
                "path": f"skills/{domain}/{skill_dir}/SKILL.md",
            }
        )

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(index, f, indent=2)
print(f"Generated skills-index.json with {len(index)} entries → {OUTPUT}")
