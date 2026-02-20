#!/usr/bin/env python3
"""Relay blueprint issues into GitHub Issues."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from glob import glob
from pathlib import Path
from typing import Any
from urllib import error, parse, request

import yaml

DEFAULT_TEMPLATE = """Plan-ID: {{id}}
Title: {{title}}

### Goal / Summary
{{summary}}

### Scope
{{scope}}

### Non-goals
{{non_goals}}

### Acceptance Criteria (DoD)
{{acceptance_criteria}}

### Verify
{{verify}}

### Constraints
{{constraints}}

### Risk
{{risk}}

### Depends On
{{depends_on}}
"""

MANAGED_LABELS = {"agent-task", "agent-ready", "risk-high"}
LABEL_STYLES = {
    "agent-task": {"color": "0e8a16", "description": "Task for coding agent"},
    "agent-ready": {"color": "1d76db", "description": "Ready for agent execution"},
    "risk-high": {"color": "b60205", "description": "High risk task"},
}
DEFAULT_LABEL_STYLE = {"color": "cfd3d7", "description": "Managed by MuseLucid Relay"}


class RelayError(Exception):
    """Relay validation error."""


class GitHubApiError(RelayError):
    """GitHub API failure."""

    def __init__(self, status: int, method: str, path: str, detail: str) -> None:
        self.status = status
        self.method = method
        self.path = path
        self.detail = detail
        super().__init__(f"GitHub API error {status} {method} {path}: {detail}")


@dataclass
class IssueSpec:
    issue_id: str
    title: str
    summary: str
    scope: list[str]
    non_goals: list[str]
    acceptance_criteria: list[str]
    verify: list[str]
    risk: str
    labels: list[str]
    depends_on: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync .muselucid plan issues to GitHub Issues.")
    parser.add_argument("--plan-dir", default=".muselucid/plan")
    parser.add_argument("--template", default=".muselucid/templates/issue.md")
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", ""))
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN", ""))
    parser.add_argument("--api-base", default=os.getenv("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def api_request(
    method: str,
    api_base: str,
    path: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    url = f"{api_base.rstrip('/')}{path}"
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = request.Request(url, data=body, method=method.upper())
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if payload is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with request.urlopen(req) as response:
            raw = response.read().decode("utf-8")
            if not raw:
                return {}
            return json.loads(raw)
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise GitHubApiError(exc.code, method, path, detail) from exc


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RelayError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise RelayError(f"YAML must be a map object: {path}")
    return data


def require_string(data: dict[str, Any], key: str, source: Path) -> str:
    value = data.get(key)
    text = str(value).strip() if value is not None else ""
    if not text:
        raise RelayError(f"'{key}' is required in {source}")
    return text


def require_list(data: dict[str, Any], key: str, source: Path) -> list[str]:
    if key not in data:
        raise RelayError(f"'{key}' key is required in {source}")
    value = data.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise RelayError(f"'{key}' must be a list in {source}")
    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            result.append(text)
    return result


def optional_list(data: dict[str, Any], key: str, source: Path) -> list[str]:
    if key not in data:
        return []
    return require_list(data, key, source)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def bullets(items: list[str], empty: str = "(none)") -> str:
    if not items:
        return f"- {empty}"
    return "\n".join(f"- {item}" for item in items)


def load_issue_specs(plan_dir: Path) -> list[IssueSpec]:
    issue_specs: list[IssueSpec] = []
    issue_paths = sorted(glob(str(plan_dir / "issues" / "*.yaml")))
    for raw_path in issue_paths:
        path = Path(raw_path)
        data = load_yaml(path)
        risk = require_string(data, "risk", path).lower()
        if risk not in {"low", "medium", "high"}:
            raise RelayError(f"'risk' must be one of low|medium|high in {path}")

        labels = require_list(data, "labels", path)
        labels.extend(["agent-task", "agent-ready"])
        if risk == "high":
            labels.append("risk-high")

        issue_specs.append(
            IssueSpec(
                issue_id=require_string(data, "id", path),
                title=require_string(data, "title", path),
                summary=require_string(data, "summary", path),
                scope=require_list(data, "scope", path),
                non_goals=require_list(data, "non_goals", path),
                acceptance_criteria=require_list(data, "acceptance_criteria", path),
                verify=require_list(data, "verify", path),
                risk=risk,
                labels=dedupe(labels),
                depends_on=optional_list(data, "depends_on", path),
            )
        )
    return issue_specs


def load_constraints(plan_dir: Path) -> list[str]:
    vision_path = plan_dir / "vision.yaml"
    vision = load_yaml(vision_path)
    constraints = vision.get("constraints", [])
    if constraints is None:
        return []
    if not isinstance(constraints, list):
        raise RelayError(f"'constraints' must be a list in {vision_path}")
    return [str(item).strip() for item in constraints if str(item).strip()]


def load_template(template_path: Path) -> str:
    if not template_path.exists():
        return DEFAULT_TEMPLATE
    return template_path.read_text(encoding="utf-8")


def render_issue_body(template: str, issue: IssueSpec, constraints: list[str]) -> str:
    context = {
        "id": issue.issue_id,
        "title": issue.title,
        "summary": issue.summary,
        "scope": bullets(issue.scope, empty="(no scope items)"),
        "non_goals": bullets(issue.non_goals, empty="(none)"),
        "acceptance_criteria": bullets(issue.acceptance_criteria, empty="(none)"),
        "verify": bullets(issue.verify, empty="(none)"),
        "constraints": bullets(constraints, empty="(none)"),
        "risk": issue.risk,
        "depends_on": bullets(issue.depends_on, empty="(none)"),
    }
    body = template
    for key, value in context.items():
        body = body.replace(f"{{{{{key}}}}}", value)
    return body.rstrip() + "\n"


def find_issue_by_plan_id(repo: str, plan_id: str, token: str, api_base: str) -> dict[str, Any] | None:
    query = f'repo:{repo} is:issue in:body "Plan-ID: {plan_id}"'
    path = f"/search/issues?q={parse.quote_plus(query)}&per_page=10"
    result = api_request("GET", api_base, path, token)
    items = result.get("items", [])
    if not items:
        return None
    # Pick most recently updated if duplicates exist.
    items = sorted(items, key=lambda item: item.get("updated_at", ""), reverse=True)
    return items[0]


def ensure_label(repo: str, label: str, token: str, api_base: str) -> None:
    style = LABEL_STYLES.get(label, DEFAULT_LABEL_STYLE)
    payload = {"name": label, "color": style["color"], "description": style["description"]}
    try:
        api_request("POST", api_base, f"/repos/{repo}/labels", token, payload)
    except GitHubApiError as exc:
        # 422 means already exists.
        if exc.status == 422:
            return
        raise


def calc_final_labels(existing_labels: list[str], desired_labels: list[str]) -> list[str]:
    preserved = [label for label in existing_labels if label not in MANAGED_LABELS]
    return dedupe(preserved + desired_labels)


def write_summary(lines: list[str]) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("## Relay Result\n\n")
        for line in lines:
            handle.write(f"- {line}\n")


def sync_issues(
    repo: str,
    token: str,
    api_base: str,
    issue_specs: list[IssueSpec],
    template: str,
    constraints: list[str],
    dry_run: bool,
) -> list[str]:
    result_lines: list[str] = []
    for spec in issue_specs:
        body = render_issue_body(template, spec, constraints)

        if dry_run:
            print(f"[DRY-RUN] Plan-ID={spec.issue_id} title={spec.title}")
            print(f"[DRY-RUN] labels={spec.labels}")
            print("[DRY-RUN] body:")
            print(body)
            print("-" * 60)
            result_lines.append(f"DRY-RUN: {spec.issue_id}")
            continue

        existing = find_issue_by_plan_id(repo, spec.issue_id, token, api_base)
        existing_labels: list[str] = []
        if existing:
            existing_labels = [str(label.get("name", "")).strip() for label in existing.get("labels", [])]
            existing_labels = [label for label in existing_labels if label]

        final_labels = calc_final_labels(existing_labels, spec.labels)
        for label in final_labels:
            ensure_label(repo, label, token, api_base)

        payload = {"title": spec.title, "body": body, "labels": final_labels}

        if existing:
            number = int(existing["number"])
            api_request("PATCH", api_base, f"/repos/{repo}/issues/{number}", token, payload)
            msg = f"Updated issue #{number} for Plan-ID {spec.issue_id}"
            print(msg)
            result_lines.append(msg)
        else:
            created = api_request("POST", api_base, f"/repos/{repo}/issues", token, payload)
            number = int(created["number"])
            msg = f"Created issue #{number} for Plan-ID {spec.issue_id}"
            print(msg)
            result_lines.append(msg)

    return result_lines


def main() -> int:
    args = parse_args()
    plan_dir = Path(args.plan_dir)
    template_path = Path(args.template)

    if not plan_dir.exists():
        raise RelayError(f"Plan directory not found: {plan_dir}")

    issue_specs = load_issue_specs(plan_dir)
    if not issue_specs:
        print("No plan issue files found under .muselucid/plan/issues/*.yaml")
        write_summary(["No issue files found."])
        return 0

    constraints = load_constraints(plan_dir)
    template = load_template(template_path)

    if args.dry_run:
        lines = sync_issues(
            repo=args.repo,
            token=args.token,
            api_base=args.api_base,
            issue_specs=issue_specs,
            template=template,
            constraints=constraints,
            dry_run=True,
        )
        write_summary(lines)
        return 0

    if not args.repo:
        raise RelayError("GITHUB_REPOSITORY is required")
    if not args.token:
        raise RelayError("GITHUB_TOKEN is required")

    lines = sync_issues(
        repo=args.repo,
        token=args.token,
        api_base=args.api_base,
        issue_specs=issue_specs,
        template=template,
        constraints=constraints,
        dry_run=False,
    )
    write_summary(lines)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RelayError as exc:
        print(f"Relay failed: {exc}", flush=True)
        raise SystemExit(1) from exc
