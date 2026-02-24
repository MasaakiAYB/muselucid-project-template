#!/usr/bin/env python3
"""Relay blueprint issues into GitHub Issues."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
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

MANAGED_LABELS = {"agent-task", "agent-ready", "agent-blocked", "risk-high"}
LABEL_STYLES = {
    "agent-task": {"color": "0e8a16", "description": "Task for coding agent"},
    "agent-ready": {"color": "1d76db", "description": "Ready for agent execution"},
    "agent-blocked": {"color": "d73a4a", "description": "Blocked by dependency"},
    "risk-high": {"color": "b60205", "description": "High risk task"},
}
DEFAULT_LABEL_STYLE = {"color": "cfd3d7", "description": "Managed by MuseLucid Relay"}
ISSUE_SYNC_SLEEP_SECONDS = 10
API_MIN_INTERVAL_SECONDS_DEFAULT = 1.0
SEARCH_MIN_INTERVAL_SECONDS_DEFAULT = 2.2
API_MAX_RETRIES_DEFAULT = 5
API_BACKOFF_SECONDS_DEFAULT = 2.0
API_MAX_BACKOFF_SECONDS_DEFAULT = 60.0


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


API_MIN_INTERVAL_SECONDS = _env_float("RELAY_API_MIN_INTERVAL_SECONDS", API_MIN_INTERVAL_SECONDS_DEFAULT)
SEARCH_MIN_INTERVAL_SECONDS = _env_float("RELAY_SEARCH_MIN_INTERVAL_SECONDS", SEARCH_MIN_INTERVAL_SECONDS_DEFAULT)
API_MAX_RETRIES = _env_int("RELAY_API_MAX_RETRIES", API_MAX_RETRIES_DEFAULT)
API_BACKOFF_SECONDS = _env_float("RELAY_API_BACKOFF_SECONDS", API_BACKOFF_SECONDS_DEFAULT)
API_MAX_BACKOFF_SECONDS = _env_float("RELAY_API_MAX_BACKOFF_SECONDS", API_MAX_BACKOFF_SECONDS_DEFAULT)
_LAST_REQUEST_AT = {"default": 0.0, "search": 0.0}
PLAN_ID_PATTERN = re.compile(r"(?im)^Plan-ID:\s*([^\s]+)\s*$")


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

    for attempt in range(API_MAX_RETRIES + 1):
        _throttle_request(path)

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
            if attempt < API_MAX_RETRIES and _is_rate_limited_error(exc.code, detail):
                delay = _retry_delay_seconds(exc, attempt)
                print(
                    f"Rate limited ({exc.code}) on {method.upper()} {path}. "
                    f"Sleeping {delay:.1f}s before retry {attempt + 1}/{API_MAX_RETRIES}."
                )
                time.sleep(delay)
                continue
            raise GitHubApiError(exc.code, method, path, detail) from exc

    raise RelayError(f"API request retries exhausted: {method.upper()} {path}")


def _request_bucket(path: str) -> str:
    if path.startswith("/search/"):
        return "search"
    return "default"


def _bucket_min_interval_seconds(bucket: str) -> float:
    if bucket == "search":
        return SEARCH_MIN_INTERVAL_SECONDS
    return API_MIN_INTERVAL_SECONDS


def _throttle_request(path: str) -> None:
    bucket = _request_bucket(path)
    min_interval = _bucket_min_interval_seconds(bucket)
    if min_interval <= 0:
        return

    elapsed = time.monotonic() - _LAST_REQUEST_AT[bucket]
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    _LAST_REQUEST_AT[bucket] = time.monotonic()


def _is_rate_limited_error(status: int, detail: str) -> bool:
    if status == 429:
        return True
    if status != 403:
        return False
    lowered = detail.lower()
    return "rate limit" in lowered or "secondary rate limit" in lowered or "abuse detection" in lowered


def _retry_delay_seconds(exc: error.HTTPError, attempt: int) -> float:
    retry_after = exc.headers.get("Retry-After")
    if retry_after:
        try:
            return max(1.0, float(retry_after))
        except ValueError:
            pass

    reset_at = exc.headers.get("X-RateLimit-Reset")
    if reset_at:
        try:
            wait_seconds = int(reset_at) - int(time.time()) + 1
            if wait_seconds > 0:
                return float(wait_seconds)
        except ValueError:
            pass

    backoff = API_BACKOFF_SECONDS * (2**attempt)
    return min(max(1.0, backoff), API_MAX_BACKOFF_SECONDS)


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


def dependency_status(
    repo: str,
    depends_on: list[str],
    token: str,
    api_base: str,
) -> tuple[bool, list[str]]:
    if not depends_on:
        return True, []

    unresolved: list[str] = []
    for dep_plan_id in depends_on:
        dep_issue = find_issue_by_plan_id(repo, dep_plan_id, token, api_base)
        if not dep_issue:
            unresolved.append(f"{dep_plan_id}: not found")
            continue

        state = str(dep_issue.get("state", "")).lower()
        number = dep_issue.get("number")
        if state != "closed":
            unresolved.append(f"{dep_plan_id}: open#{number}")

    return len(unresolved) == 0, unresolved


def desired_labels_for_issue(spec: IssueSpec, deps_resolved: bool) -> list[str]:
    labels = [label for label in spec.labels if label not in MANAGED_LABELS]
    labels.append("agent-task")
    if spec.risk == "high":
        labels.append("risk-high")
    if deps_resolved:
        labels.append("agent-ready")
    else:
        labels.append("agent-blocked")
    return dedupe(labels)


def write_summary(lines: list[str]) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("## Relay Result\n\n")
        for line in lines:
            handle.write(f"- {line}\n")


def extract_plan_id_from_body(body: str) -> str:
    match = PLAN_ID_PATTERN.search(body or "")
    if not match:
        return ""
    return match.group(1).strip()


def load_closed_issue_trigger() -> tuple[int | None, str]:
    if os.getenv("GITHUB_EVENT_NAME", "") != "issues":
        return None, ""

    event_path = os.getenv("GITHUB_EVENT_PATH", "").strip()
    if not event_path:
        return None, ""

    try:
        with open(event_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle) or {}
    except (OSError, json.JSONDecodeError):
        return None, ""

    if str(payload.get("action", "")) != "closed":
        return None, ""

    issue_data = payload.get("issue")
    issue = issue_data if isinstance(issue_data, dict) else {}

    issue_number: int | None = None
    raw_number = issue.get("number")
    if isinstance(raw_number, int):
        issue_number = raw_number
    else:
        number_text = str(raw_number or "").strip()
        if number_text.isdigit():
            issue_number = int(number_text)

    plan_id = extract_plan_id_from_body(str(issue.get("body", "")))
    return issue_number, plan_id


def sync_issues(
    repo: str,
    token: str,
    api_base: str,
    issue_specs: list[IssueSpec],
    template: str,
    constraints: list[str],
    dry_run: bool,
    closed_trigger_issue_number: int | None = None,
    closed_trigger_plan_id: str = "",
) -> list[str]:
    result_lines: list[str] = []
    for index, spec in enumerate(issue_specs):
        body = render_issue_body(template, spec, constraints)
        deps_resolved, unresolved = dependency_status(
            repo=repo,
            depends_on=spec.depends_on,
            token=token,
            api_base=api_base,
        )
        desired_labels = desired_labels_for_issue(spec, deps_resolved)

        if dry_run:
            print(f"[DRY-RUN] Plan-ID={spec.issue_id} title={spec.title}")
            print(f"[DRY-RUN] labels={desired_labels}")
            if unresolved:
                print(f"[DRY-RUN] blocked_by={unresolved}")
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

        final_labels = calc_final_labels(existing_labels, desired_labels)
        for label in final_labels:
            ensure_label(repo, label, token, api_base)

        payload = {"title": spec.title, "body": body, "labels": final_labels}

        if existing:
            number = int(existing["number"])
            state = str(existing.get("state", "")).lower()
            skip_reopen = state == "closed" and (
                (closed_trigger_issue_number is not None and number == closed_trigger_issue_number)
                or (closed_trigger_plan_id and spec.issue_id == closed_trigger_plan_id)
            )

            if skip_reopen:
                msg = (
                    f"Kept closed issue #{number} for Plan-ID {spec.issue_id} "
                    "(skip reopen on issues.closed trigger)"
                )
                if unresolved:
                    msg += f" (blocked by: {', '.join(unresolved)})"
                print(msg)
                result_lines.append(msg)
            else:
                reopened = False
                if state == "closed":
                    api_request("PATCH", api_base, f"/repos/{repo}/issues/{number}", token, {"state": "open"})
                    reopened = True

                api_request("PATCH", api_base, f"/repos/{repo}/issues/{number}", token, payload)
                msg_prefix = "Reopened and updated" if reopened else "Updated"
                msg = f"{msg_prefix} issue #{number} for Plan-ID {spec.issue_id}"
                if unresolved:
                    msg += f" (blocked by: {', '.join(unresolved)})"
                print(msg)
                result_lines.append(msg)
        else:
            created = api_request("POST", api_base, f"/repos/{repo}/issues", token, payload)
            number = int(created["number"])
            msg = f"Created issue #{number} for Plan-ID {spec.issue_id}"
            if unresolved:
                msg += f" (blocked by: {', '.join(unresolved)})"
            print(msg)
            result_lines.append(msg)

        if index < len(issue_specs) - 1:
            print(f"Sleeping {ISSUE_SYNC_SLEEP_SECONDS} seconds before next issue sync...")
            time.sleep(ISSUE_SYNC_SLEEP_SECONDS)

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
    closed_trigger_issue_number, closed_trigger_plan_id = load_closed_issue_trigger()

    if args.dry_run:
        lines = sync_issues(
            repo=args.repo,
            token=args.token,
            api_base=args.api_base,
            issue_specs=issue_specs,
            template=template,
            constraints=constraints,
            dry_run=True,
            closed_trigger_issue_number=closed_trigger_issue_number,
            closed_trigger_plan_id=closed_trigger_plan_id,
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
        closed_trigger_issue_number=closed_trigger_issue_number,
        closed_trigger_plan_id=closed_trigger_plan_id,
    )
    write_summary(lines)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RelayError as exc:
        print(f"Relay failed: {exc}", flush=True)
        raise SystemExit(1) from exc
