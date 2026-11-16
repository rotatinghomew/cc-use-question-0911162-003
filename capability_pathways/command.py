from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from capability_pathways.profiles.institution import ContractError
from capability_pathways.programme_office import Application, run, verify


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog='capability_pathways', description='人工智能能力建设路径与成果归因平台')
    commands = root.add_subparsers(dest="command", required=True)
    execute = commands.add_parser("run")
    execute.add_argument("--fixture", required=True)
    execute.add_argument("--database", required=True)
    execute.add_argument("--output", required=True)
    execute.add_argument("--slots", type=int, default=None, help="扩容名额")
    execute.add_argument("--mentor-floor", type=float, default=None)
    execute.add_argument("--compute-floor", type=float, default=None)
    execute.add_argument("--as-of", default=None, help="观察截止时间（ISO 8601）")
    check = commands.add_parser("verify")
    check.add_argument("--database", required=True)
    check.add_argument("--output", required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--database", required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--database", required=True)
    compare.add_argument("--output", required=True, help="比较报告写入位置；留空只打印")
    compare.add_argument("--slots", type=int, default=None)
    compare.add_argument("--mentor-floor", type=float, default=None)
    compare.add_argument("--compute-floor", type=float, default=None)
    compare.add_argument("--as-of", default=None)
    resource = commands.add_parser("resources")
    resource.add_argument("--database", required=True)
    resource.add_argument("--slots", type=int, default=None)
    resource.add_argument("--mentor-floor", type=float, default=None)
    resource.add_argument("--compute-floor", type=float, default=None)
    correct = commands.add_parser("correct")
    correct.add_argument("--database", required=True)
    correct.add_argument("--record", required=True)
    correct.add_argument("--set", action="append", default=[], metavar="FIELD=VALUE",
                         help="更正一个画像字段，可重复")
    plan = commands.add_parser("plan")
    plan.add_argument("--database", required=True)
    plan.add_argument("action", choices=["list", "adopt", "withdraw"])
    plan.add_argument("--plan-id", default=None)
    return root


def _resource_updates(args: argparse.Namespace) -> dict[str, object]:
    updates: dict[str, object] = {}
    if getattr(args, "slots", None) is not None:
        updates["expansion_slots"] = args.slots
    if getattr(args, "mentor_floor", None) is not None:
        updates["mentor_capacity_floor"] = args.mentor_floor
    if getattr(args, "compute_floor", None) is not None:
        updates["compute_access_floor"] = args.compute_floor
    return updates


def _as_of(args: argparse.Namespace) -> dict[str, object]:
    return {"as_of": args.as_of} if getattr(args, "as_of", None) else {}


def _assignment(text: str) -> tuple[str, object]:
    if "=" not in text:
        raise SystemExit(f"invalid --set value: {text!r}")
    key, raw = text.split("=", 1)
    key = key.strip()
    if not key:
        raise SystemExit("empty --set field")
    try:
        value: object = json.loads(raw)
    except json.JSONDecodeError:
        value = raw.strip()
    return key, value


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = _dispatch(args)
    except ContractError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("ok", True) else 1


def _dispatch(args: argparse.Namespace) -> dict[str, object]:
    if args.command == "run":
        resources = _resource_updates(args) | _as_of(args)
        result = run(args.fixture, args.database, args.output, resources=resources or None)
    elif args.command == "verify":
        result = verify(args.database, args.output)
    elif args.command == "compare":
        application = Application(args.database)
        resources = _resource_updates(args) | _as_of(args)
        comparison = application.compare(resources or None)
        result = {"ok": True, "comparison": comparison}
        plan = application.publish_plan(comparison, resources or application.repository.resources())
        result["expansion_plan"] = plan
        if args.output:
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps({"comparison": comparison, "expansion_plan": plan},
                                         ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                              encoding="utf-8")
    elif args.command == "resources":
        result = {"ok": True, "refreshed": Application(args.database).update_resources(_resource_updates(args))}
    elif args.command == "correct":
        updates = dict(_assignment(item) for item in args.set)
        result = {"ok": True, "refreshed": Application(args.database).correct_record(args.record, updates)}
    elif args.command == "plan":
        application = Application(args.database)
        if args.action == "list":
            result = {"ok": True, "plans": application.repository.plan_rows()}
        else:
            if not args.plan_id:
                raise SystemExit("--plan-id is required for this action")
            status = "adopted" if args.action == "adopt" else "superseded"
            result = {"ok": True, "plan": application.plan_action(args.plan_id, status)}
    else:
        result = Application(args.database).inspect()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
