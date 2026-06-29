from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from ..skills.packaging import builtin_skill_templates


SKILL_MANIFEST_COVERAGE_SCHEMA_VERSION = "skill_manifest_coverage/v1"

# Required frontmatter scalars on every rendered SKILL.md. These mirror the
# deterministic frontmatter contract produced by src/skills/render.py so the
# gate fails loudly if a future change drops a field the install manifest and
# Hermes skill loader depend on.
REQUIRED_FRONTMATTER_FIELDS: tuple[str, ...] = (
    "name",
    "description",
    "category",
    "phase",
    "role",
    "quality_tier",
)

# Credential-hygiene scan ported from oh-my-hermes scripts/validate-skills.sh.
# It guards the rendered, shipped skill content against an accidental hardcoded
# secret being baked into a distributed SKILL.md. The original bash gate used a
# case-insensitive `(api_key|token|password|secret)=<20+ chars>` heuristic; this
# keeps the same shape but runs portably (no bash 4 `declare -A` dependency).
_SECRET_PATTERN = re.compile(
    r"(api[_-]?key|token|password|secret)\s*[:=]\s*[A-Za-z0-9_\-]{20,}",
    re.IGNORECASE,
)

# A synthetic line used only as a negative control so the gate proves its own
# secret detector still fires, instead of silently degrading to a tautology.
_SECRET_CONTROL_SAMPLE = "api_key = AKIAEXAMPLE0SECRET0VALUE0ABCDEF123456"


@dataclass(frozen=True)
class _Frontmatter:
    fields: dict[str, str]
    tags: tuple[str, ...]
    has_open: bool
    has_close: bool
    body: str


def build_skill_manifest_coverage_demo() -> dict[str, object]:
    templates = builtin_skill_templates()
    rows = [_evaluate_template(template.name, template.content) for template in templates]
    passing_count = sum(1 for row in rows if bool(row["passed"]))
    secret_findings = sum(1 for row in rows if bool(row["observed"]["secret_detected"]))
    control = _secret_detection_control()
    all_passing = bool(rows) and passing_count == len(rows) and secret_findings == 0 and bool(control["detected"])
    return {
        "schema_version": SKILL_MANIFEST_COVERAGE_SCHEMA_VERSION,
        "summary": {
            "skill_count": len(rows),
            "passing_count": passing_count,
            "secret_finding_count": secret_findings,
            "secret_control_detected": bool(control["detected"]),
            "all_passing": all_passing,
        },
        "check_basis": [
            "Every shipped SKILL.md opens and closes YAML frontmatter.",
            "Required frontmatter fields (name, description, category, phase, role, quality_tier) are present and non-empty.",
            "The frontmatter name matches the skill template name and the description carries the [omj] provenance tag.",
            "Skill tags include the oh-my-jeo pack tag and stay consistent with the declared category.",
            "No rendered skill content contains a hardcoded credential (api key, token, password, or secret).",
            "A synthetic secret control confirms the credential scanner still fires.",
            "This gate checks rendered local skill-pack content only; it does not prove Hermes installed or loaded the pack.",
        ],
        "skills": rows,
        "secret_detection_control": control,
        "claim_boundary": (
            "Skill manifest coverage proves the deterministic local skill-pack frontmatter and credential-hygiene "
            "contracts only. It does not prove Hermes discovered, installed, loaded, or executed any skill, nor any "
            "downstream connector, executor, review, CI, merge, or delivery work."
        ),
    }


def format_skill_manifest_coverage_summary(payload: dict[str, object]) -> str:
    summary = _nested(payload, "summary")
    rows = _dict_rows(payload.get("skills", []))
    total = int(summary.get("skill_count", len(rows)) or 0)
    passing = int(summary.get("passing_count", 0) or 0)
    secrets = int(summary.get("secret_finding_count", 0) or 0)
    control = bool(summary.get("secret_control_detected", False))
    all_passing = bool(summary.get("all_passing", False))
    lines = [
        "OMJ skill manifest coverage",
        f"Result: {passing}/{total} skill manifests passing" + (" (all passing)" if all_passing else ""),
        f"Hardcoded secret findings: {secrets}; secret scanner control: {'fires' if control else 'BROKEN'}",
        "",
        "What this proves:",
    ]
    for basis in payload.get("check_basis", []):
        lines.append(f"- {basis}")
    failed = [row for row in rows if not row.get("passed")]
    if failed:
        lines.extend(["", "Failures:"])
        for row in failed:
            issues = ", ".join(row.get("issues", [])) or "unknown issue"
            lines.append(f"- {row.get('name', 'unknown')}: {issues}")
    if not control:
        lines.extend(["", "Failures:", "- secret-detection-control: credential scanner did not fire on the control sample"])
    lines.extend(
        [
            "",
            f"Boundary: {payload.get('claim_boundary', '')}",
            "Use --json for the full machine-readable payload.",
        ]
    )
    return "\n".join(lines)


def _evaluate_template(name: str, content: str) -> dict[str, object]:
    front = _parse_frontmatter(content)
    fields = front.fields
    category = fields.get("category", "")
    secret_match = _SECRET_PATTERN.search(content)
    section_count = len(re.findall(r"(?m)^##\s+\S", front.body))
    observed = {
        "name": fields.get("name", ""),
        "description": fields.get("description", ""),
        "category": category,
        "phase": fields.get("phase", ""),
        "role": fields.get("role", ""),
        "quality_tier": fields.get("quality_tier", ""),
        "tags": list(front.tags),
        "has_frontmatter_open": front.has_open,
        "has_frontmatter_close": front.has_close,
        "section_count": section_count,
        "secret_detected": bool(secret_match),
    }
    issues: list[str] = []
    if not front.has_open or not front.has_close:
        issues.append("missing frontmatter delimiters")
    for field in REQUIRED_FRONTMATTER_FIELDS:
        if not str(fields.get(field, "")).strip():
            issues.append(f"missing required frontmatter field '{field}'")
    if fields.get("name") and fields.get("name") != name:
        issues.append(f"frontmatter name {fields.get('name')} does not match template {name}")
    if fields.get("description") and not fields["description"].startswith("[omj]"):
        issues.append("description missing [omj] provenance tag")
    if "oh-my-jeo" not in front.tags:
        issues.append("tags missing oh-my-jeo pack tag")
    if category and front.tags and front.tags[-1] != category:
        issues.append(f"tags category {front.tags[-1]} does not match category {category}")
    if section_count < 1:
        issues.append("skill body has no '##' sections")
    if secret_match:
        issues.append(f"possible hardcoded secret near '{secret_match.group(1)}'")
    return {
        "name": name,
        "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "passed": not issues,
        "observed": observed,
        "issues": issues,
    }


def _secret_detection_control() -> dict[str, object]:
    sample = f"---\nname: control\n{_SECRET_CONTROL_SAMPLE}\n---\n"
    match = _SECRET_PATTERN.search(sample)
    return {
        "sample_field": "api_key",
        "detected": bool(match),
        "matched_keyword": match.group(1) if match else "",
    }


def _parse_frontmatter(content: str) -> _Frontmatter:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return _Frontmatter({}, (), False, False, content)
    close_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            close_index = index
            break
    if close_index is None:
        return _Frontmatter({}, (), True, False, "")
    front_lines = lines[1:close_index]
    body = "\n".join(lines[close_index + 1 :])
    fields: dict[str, str] = {}
    tags: tuple[str, ...] = ()
    for raw in front_lines:
        stripped = raw.strip()
        match = re.match(r"([A-Za-z_][\w-]*):\s*(.*)$", stripped)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if key == "tags":
            tags = _parse_tag_list(value)
            continue
        if key in {"name", "description", "category", "phase", "role", "quality_tier"} and key not in fields:
            if value:
                fields[key] = value.strip('"')
    return _Frontmatter(fields, tags, True, True, body)


def _parse_tag_list(value: str) -> tuple[str, ...]:
    inner = value.strip()
    if inner.startswith("[") and inner.endswith("]"):
        inner = inner[1:-1]
    items = [item.strip().strip('"').strip("'") for item in inner.split(",")]
    return tuple(item for item in items if item)


def _nested(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload.get(key)
    return value if isinstance(value, dict) else {}


def _dict_rows(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
