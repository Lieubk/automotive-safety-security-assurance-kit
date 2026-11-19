#!/usr/bin/env python3
"""Exchange with ALM tools over their REST interfaces: Polarion, codebeamer, Jama Connect.

`pull` reads work items of a project, tracker or item type and registers them as imported
items (or, with --compare, says what a new state changes against them). `push` creates or
updates work items from the project's items and keeps the pairing of IDs in
`.alm/map.json` of the project, so that a second push updates instead of duplicating.

Written from the public descriptions of the interfaces and tested against a simulated
server; try it against your own server with --dry-run first. Field names differ between
installations: --text-field and --map adapt them.

Credentials never go into files or arguments: a token is read from the environment
variable --token-env names (default ALM_TOKEN), or user and password from ALM_USER and
ALM_PASSWORD.

Usage:
    python tools/alm.py [--project DIR] pull polarion --url URL --alm-project ID [--query Q] --type T --source NAME --version V
    python tools/alm.py [--project DIR] pull codebeamer --url URL --tracker ID --type T --source NAME --version V
    python tools/alm.py [--project DIR] pull jama --url URL --alm-project ID --item-type ID --type T --source NAME --version V
        [--compare] [--text-field F] [--map ATTR=FIELD ...] [--received DATE] [--dry-run] [--token-env NAME]
    python tools/alm.py [--project DIR] push polarion|codebeamer|jama --url URL <scope> --type T [--type T ...]
        [--work-item-type NAME] [--parent ID] [--dry-run] [--token-env NAME]

Exit code 0 = done, 1 = refused or the server answered with an error (printed), 2 = usage.
"""
import argparse
import base64
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exchange  # noqa: E402
import record  # noqa: E402
from traceability import Project  # noqa: E402

PAGE = 100


class AlmError(Exception):
    pass


def plain_text(value):
    """Text of a field that may be HTML, a rich-text object or a plain string."""
    if isinstance(value, dict):
        value = value.get("value") or value.get("text") or ""
    text = re.sub(r"<\s*(br|/p|/div|/li)\s*/?>", "\n", str(value or ""), flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    return "\n".join(line.strip() for line in text.split("\n") if line.strip())


class Client:
    def __init__(self, url, token_env, timeout=60):
        self.base, self.timeout = url.rstrip("/"), timeout
        token = os.environ.get(token_env)
        user, password = os.environ.get("ALM_USER"), os.environ.get("ALM_PASSWORD")
        if token:
            self.auth = "Bearer %s" % token
        elif user and password:
            self.auth = "Basic %s" % base64.b64encode(("%s:%s" % (user, password)).encode()).decode()
        else:
            raise AlmError("no credentials: set %s, or ALM_USER and ALM_PASSWORD, in the environment" % token_env)

    def call(self, method, path, body=None, query=None):
        url = self.base + path + (("?" + urllib.parse.urlencode(query)) if query else "")
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": self.auth, "Accept": "application/json", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            raise AlmError("%s %s answered %d: %s" % (method, path, exc.code, detail))
        except urllib.error.URLError as exc:
            raise AlmError("%s %s: %s" % (method, path, exc.reason))
        return json.loads(raw.decode("utf-8")) if raw.strip() else {}


# --------------------------------------------------------------------------- adapters

class Polarion:
    """Polarion REST API (JSON:API): /polarion/rest/v1/projects/{project}/workitems."""
    name = "polarion"

    def __init__(self, client, args):
        self.client, self.project = client, args.alm_project
        self.prefix = "/polarion/rest/v1/projects/%s" % urllib.parse.quote(self.project)
        self.text_field = args.text_field or "description"
        self.query, self.wi_type = args.query, args.work_item_type or "requirement"

    def items(self):
        number, out = 1, []
        while True:
            query = {"fields[workitems]": "@all", "page[size]": PAGE, "page[number]": number}
            if self.query:
                query["query"] = self.query
            data = self.client.call("GET", self.prefix + "/workitems", query=query)
            for entry in data.get("data") or []:
                attributes = entry.get("attributes") or {}
                out.append({"source_id": str(entry.get("id", "")).split("/")[-1], "title": attributes.get("title"),
                            "text": plain_text(attributes.get(self.text_field)), "fields": attributes})
            if not (data.get("links") or {}).get("next") or not data.get("data"):
                return out
            number += 1

    def create(self, item, text):
        body = {"data": [{"type": "workitems", "attributes": {
            "type": self.wi_type, "title": item.title, self.text_field: {"type": "text/plain", "value": text}}}]}
        data = self.client.call("POST", self.prefix + "/workitems", body)
        return str(((data.get("data") or [{}])[0]).get("id", "")).split("/")[-1]

    def update(self, alm_id, item, text):
        body = {"data": {"type": "workitems", "id": "%s/%s" % (self.project, alm_id), "attributes": {
            "title": item.title, self.text_field: {"type": "text/plain", "value": text}}}}
        self.client.call("PATCH", self.prefix + "/workitems/%s" % urllib.parse.quote(alm_id), body)


class Codebeamer:
    """codebeamer REST API v3: /api/v3/trackers/{tracker}/items and /api/v3/items/{id}."""
    name = "codebeamer"

    def __init__(self, client, args):
        self.client, self.tracker = client, args.tracker
        self.text_field = args.text_field or "description"

    def items(self):
        page, out = 1, []
        while True:
            data = self.client.call("GET", "/api/v3/trackers/%s/items" % self.tracker, query={"page": page, "pageSize": PAGE})
            refs = data.get("itemRefs") or []
            for ref in refs:
                item = self.client.call("GET", "/api/v3/items/%s" % ref["id"])
                out.append({"source_id": str(item.get("id")), "title": item.get("name"),
                            "text": plain_text(item.get(self.text_field)), "fields": item})
            if not refs or page * PAGE >= int(data.get("total") or 0):
                return out
            page += 1

    def create(self, item, text):
        data = self.client.call("POST", "/api/v3/trackers/%s/items" % self.tracker,
                                {"name": item.title, self.text_field: text, "descriptionFormat": "PlainText"})
        return str(data.get("id", ""))

    def update(self, alm_id, item, text):
        current = self.client.call("GET", "/api/v3/items/%s" % alm_id)
        current.update({"name": item.title, self.text_field: text, "descriptionFormat": "PlainText"})
        self.client.call("PUT", "/api/v3/items/%s" % alm_id, current)


class Jama:
    """Jama Connect REST API: /rest/v1/abstractitems, /rest/v1/items."""
    name = "jama"

    def __init__(self, client, args):
        self.client, self.project, self.item_type, self.parent = client, args.alm_project, args.item_type, args.parent
        self.text_field = args.text_field or "description"

    def items(self):
        start, out = 0, []
        while True:
            data = self.client.call("GET", "/rest/v1/abstractitems", query={
                "project": self.project, "itemType": self.item_type, "startAt": start, "maxResults": 50})
            for entry in data.get("data") or []:
                fields = entry.get("fields") or {}
                out.append({"source_id": entry.get("documentKey") or str(entry.get("id")), "title": fields.get("name"),
                            "text": plain_text(fields.get(self.text_field)), "fields": dict(fields, id=entry.get("id"))})
            info = ((data.get("meta") or {}).get("pageInfo") or {})
            start += int(info.get("resultCount") or 0)
            if not data.get("data") or start >= int(info.get("totalResults") or 0):
                return out

    def create(self, item, text):
        body = {"project": int(self.project), "itemType": int(self.item_type),
                "fields": {"name": item.title, self.text_field: html.escape(text).replace("\n", "<br/>")}}
        if self.parent:
            body["location"] = {"parent": {"item": int(self.parent)}}
        data = self.client.call("POST", "/rest/v1/items", body)
        return str((data.get("meta") or {}).get("id") or data.get("id") or "")

    def update(self, alm_id, item, text):
        self.client.call("PATCH", "/rest/v1/items/%s" % alm_id, [
            {"op": "replace", "path": "/fields/name", "value": item.title},
            {"op": "replace", "path": "/fields/%s" % self.text_field, "value": html.escape(text).replace("\n", "<br/>")}])


ADAPTERS = {"polarion": Polarion, "codebeamer": Codebeamer, "jama": Jama}
NEEDS = {"polarion": ["alm_project"], "codebeamer": ["tracker"], "jama": ["alm_project", "item_type"]}


# --------------------------------------------------------------------------- commands

def adapter(args):
    missing = ["--%s" % n.replace("_", "-") for n in NEEDS[args.tool] if not getattr(args, n)]
    if missing:
        raise AlmError("%s needs %s" % (args.tool, ", ".join(missing)))
    return ADAPTERS[args.tool](Client(args.url, args.token_env), args)


def cmd_pull(project, args):
    try:
        records = adapter(args).items()
    except AlmError as exc:
        return record.stop([str(exc)])
    mapped = [tuple(m.split("=", 1)) for m in args.map or [] if "=" in m]
    for rec in records:
        rec["attributes"] = {name: rec["fields"].get(field) for name, field in mapped
                             if rec["fields"].get(field) not in (None, "")}
        for name, value in list(rec["attributes"].items()):
            if isinstance(value, dict):                   # enumerations come as {id, name}
                rec["attributes"][name] = value.get("name") or value.get("id")
    if args.compare:
        return exchange.print_comparison(project, args.source, records)
    problems, written = exchange.register(project, args.type, args.source, args.version, args.received, records, args.dry_run)
    if problems:
        return record.stop(problems)
    print("%s %d %s items from %s (%s), version %s: %s" % (
        "would write" if args.dry_run else "wrote", len(written), args.type, args.source, args.tool, args.version,
        "%s to %s" % (written[0], written[-1]) if written else "-"))
    return 0


def map_file(project):
    return project.root / ".alm" / "map.json"


def cmd_push(project, args):
    unknown = [t for t in args.type if t not in project.types]
    if unknown:
        return record.stop(["unknown type: %s" % ", ".join(unknown)])
    items = sorted((i for i in project.items.values() if i.type in args.type and project.live(i) and not i.imported),
                   key=lambda i: i.id)
    path = map_file(project)
    pairing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    key = "%s %s" % (args.tool, args.url.rstrip("/"))
    known = pairing.setdefault(key, {})
    if args.dry_run:
        for item in items:
            print("%s %s  %s" % ("update" if item.id in known else "create", item.id, item.title))
        print("would push %d items to %s" % (len(items), args.tool))
        return 0
    try:
        target = adapter(args)
    except AlmError as exc:
        return record.stop([str(exc)])
    created = updated = 0
    try:
        for item in items:
            text = item.sections.get(exchange.first_section(project, item.type), "").strip()
            if item.id in known:
                target.update(known[item.id], item, text)
                updated += 1
            else:
                known[item.id] = target.create(item, text)
                created += 1
    except AlmError as exc:
        print("stopped after %d created, %d updated: %s" % (created, updated, exc))
        return 1
    finally:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pairing, indent=2, sort_keys=True), encoding="utf-8")
    print("pushed %d items to %s: %d created, %d updated; pairing kept in %s"
          % (len(items), args.tool, created, updated, path.relative_to(project.root).as_posix()))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project", default=".")
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("pull", "push"):
        p = sub.add_parser(name)
        p.add_argument("tool", choices=sorted(ADAPTERS))
        p.add_argument("--url", required=True)
        p.add_argument("--alm-project", help="Polarion project ID, Jama project ID")
        p.add_argument("--tracker", help="codebeamer tracker ID")
        p.add_argument("--item-type", help="Jama item type ID")
        p.add_argument("--parent", help="Jama parent item ID for created items")
        p.add_argument("--query", help="Polarion query that selects the work items")
        p.add_argument("--work-item-type", help="Polarion work item type for created items (default requirement)")
        p.add_argument("--text-field", help="the field that holds the text (default description)")
        p.add_argument("--token-env", default="ALM_TOKEN")
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--type", required=True, action="append" if name == "push" else None)
        if name == "pull":
            p.add_argument("--source", required=True)
            p.add_argument("--version", required=True)
            p.add_argument("--received")
            p.add_argument("--compare", action="store_true")
            p.add_argument("--map", action="append", help="ATTR=FIELD: take a field over, for example asil=asil")
    args = ap.parse_args()
    if args.command == "pull" and isinstance(args.type, list):
        args.type = args.type[0]
    project = Project(args.project)
    return {"pull": cmd_pull, "push": cmd_push}[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
