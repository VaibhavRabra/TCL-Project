"""Build the 'Outreach' tab values from lemlist exports.

Usage: python3 sync_outreach.py <outdir> <leads_export.json> <activities_page.json> [more activity pages...]
Activity pages are merged into <outdir>/activities_store.json (keyed by activity id), so later runs only need the newest pages.
Writes <outdir>/outreach.csv (columns A:R of the Outreach tab, no header), sorted by contact UID.
"""
import json, os, sys, collections
from datetime import datetime, timedelta, timezone

out, leads_file, act_files = sys.argv[1], sys.argv[2], sys.argv[3:]
GST = timezone(timedelta(hours=4))


def load(f):
    j = json.load(open(f))
    return j["data"] if isinstance(j, dict) else j


def t(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(GST).strftime("%d %b, %H:%M GST") if iso else ""


store_f = f"{out}/activities_store.json"
store = json.load(open(store_f)) if os.path.exists(store_f) else {}
new = 0
for f in act_files:
    for a in load(f):
        if a["_id"] not in store:
            new += 1
            store[a["_id"]] = dict(type=a["type"], at=a["createdAt"], lead=a.get("leadId", ""), bot=a.get("bot", False))
json.dump(store, open(store_f, "w"))

by = collections.defaultdict(lambda: collections.defaultdict(list))
for a in store.values():
    by[a["lead"]][a["type"]].append(a["at"])

leads = sorted(load(leads_file), key=lambda r: r.get("contactUid", ""))
ver = {"deliverable": "Deliverable", "risky": "Risky: LinkedIn only", "undeliverable": "Undeliverable: LinkedIn only"}
static, status = [], []
now = datetime.now(GST).strftime("%Y-%m-%d %H:%M")
for r in leads:
    a = by[r["_id"]]
    f = lambda k: t(min(a[k])) if a.get(k) else ""
    static.append([r.get("contactUid", ""), f"{r.get('firstName', '')} {r.get('lastName', '')}".strip(), r.get("jobTitle", ""), r.get("companyName", ""),
                   r.get("country", ""), r.get("portfolio", ""), r.get("email", ""), ver.get(r.get("emailStatus", ""), "No email" if not r.get("email") else "Not verified"),
                   r.get("linkedinUrl", ""), r.get("teleOwner", "")])
    li = ("Replied" if a.get("linkedinReplied") else "Connected" if a.get("linkedinInviteAccepted") else "Invite sent" if a.get("linkedinInviteDone")
          else "Profile visited" if a.get("linkedinVisitDone") else ("Queued" if r.get("linkedinUrl") else "No LinkedIn URL"))
    replied = "Email" if a.get("emailsReplied") else ("LinkedIn" if a.get("linkedinReplied") else "")
    bounced = "Bounced" if a.get("emailsBounced") else ""
    last = max((x for v in a.values() for x in v), default="")
    status.append([len(a.get("emailsSent", [])), f("emailsSent"), "Opened" if a.get("emailsOpened") else "", f("emailsOpened"), bounced, li, replied, t(last)])
json.dump(static, open(f"{out}/outreach_static.json", "w"))
json.dump(status, open(f"{out}/outreach_status.json", "w"))
import csv
with open(f"{out}/outreach.csv", "w", newline="") as fh:
    csv.writer(fh).writerows([s + st for s, st in zip(static, status)])
c = collections.Counter(a["type"] for a in store.values())
print("new activities", new, "| store", len(store), dict(c))
print("leads", len(leads), "| emailed", sum(1 for s in status if s[0]), "| opened", sum(1 for s in status if s[2]), "| replied", sum(1 for s in status if s[6]),
      "| bounced", sum(1 for s in status if s[4]), "| LI touched", sum(1 for s in status if s[5] not in ("Queued", "No LinkedIn URL")))
print("static chars", len(json.dumps(static)), "status chars", len(json.dumps(status)))
