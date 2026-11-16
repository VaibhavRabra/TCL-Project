"""Write the two deliverable workbooks from out/consolidated.pkl.

Usage: python3 make_workbooks.py <outdir>
"""
import sys
import pandas as pd

from copy_blocks import HOOKS, P

OUT = sys.argv[1]
df = pd.read_pickle(f"{OUT}/consolidated.pkl").fillna("")
E = df["campaign_status"] == "Eligible"

COLS = [  # (header, field, width, group)
    ("Contact UID", "uid", 11, "id"), ("Campaign status", "campaign_status", 30, "plan"), ("Wave", "wave", 9, "plan"),
    ("Priority score", "priority_score", 9, "plan"), ("Channel plan", "channel", 16, "plan"),
    ("Sending mailbox", "mailbox", 30, "plan"), ("LinkedIn sender", "li_sender", 16, "plan"), ("lemlist status", "lemlist", 34, "plan"), ("Email verification (lemlist)", "verify", 34, "plan"),
    ("Portfolio", "portfolio", 13, "persona"), ("Product to pitch", "product", 36, "persona"),
    ("Persona group", "persona_group", 24, "persona"), ("Seniority", "seniority", 10, "persona"),
    ("First name", "first", 14, "contact"), ("Last name", "last", 16, "contact"), ("Full name", "full_name", 24, "contact"),
    ("Designation", "title", 34, "contact"), ("Department", "department", 16, "contact"),
    ("Company", "company", 30, "contact"), ("Company (as used in messages)", "company_short", 26, "contact"),
    ("Country", "country", 16, "contact"), ("Country source", "country_src", 12, "contact"),
    ("Email", "email", 32, "contact"), ("LinkedIn URL", "linkedin", 38, "contact"), ("Mobile", "mobile", 17, "contact"),
    ("Alternate phone", "alt_phone", 17, "contact"), ("Board line", "board_line", 17, "contact"),
    ("Account segment", "segment", 13, "account"), ("Account tier", "account_tier", 20, "account"),
    ("Account status (CRM)", "account_status", 16, "account"), ("Tele-team owner", "tele_owner", 16, "account"),
    ("Past call status", "call_status", 20, "account"), ("Last call remark", "last_remark", 40, "account"),
    ("Email 1: subject", "email1_subject", 34, "draft"), ("Email 1: body (day 0)", "email1_body", 60, "draft"),
    ("Email 2: body (day 3, same thread)", "email2_body", 60, "draft"), ("Email 3: body (day 8, same thread)", "email3_body", 60, "draft"),
    ("LinkedIn: connection note", "li_invite", 50, "draft"), ("LinkedIn: message after acceptance", "li_message", 60, "draft"),
    ("LinkedIn: follow-up (+4 days)", "li_followup", 60, "draft"), ("Tele-team call opener", "call_opener", 60, "draft"),
    ("Source", "source", 14, "ref"), ("Lot", "lot", 7, "ref"), ("CRM contact ID", "crm_contact_id", 11, "ref"),
    ("CRM org ID", "crm_org_id", 10, "ref"), ("ZoomInfo ID", "zoom_id", 12, "ref"), ("Email as received", "raw_email", 30, "ref"),
]
GROUP_COLOR = {"id": "#1F3864", "plan": "#1F3864", "persona": "#2E75B6", "contact": "#375623", "account": "#7F6000", "draft": "#833C0B", "ref": "#595959"}

df["product"] = df["portfolio"].map(lambda p: P[p]["product"] if p in P else "")
import glob, os
_b = {}
for _f in sorted(glob.glob(f"{OUT}/batch*_uids.txt")):
    for _u in open(_f).read().split():
        _b[_u] = "Batch " + os.path.basename(_f)[5:].split("_")[0] + ": loaded in lemlist"
df["mailbox"] = ["khalid@ / techtransformation@digitaldenave.com (rotated by lemlist)" if m else "" for m in df["mailbox"]]
_v = {}
for _f in glob.glob(f"{OUT}/lemlist_batch*_status.csv"):
    _s = pd.read_csv(_f).fillna("")
    _v.update(dict(zip(_s["uid"], _s["emailStatus"])))
df["lemlist"] = [("Live in lemlist since 16 Nov 2026 (batch 1)" if u in _b else ("Queued: needs email verification credits" if w == "Wave 1" else ("Queued: Wave 2" if w else ""))) for u, w in zip(df["uid"], df["wave"])]
df["verify"] = [({"deliverable": "Deliverable: emails sending", "risky": "Risky (catch-all): no email, LinkedIn only", "undeliverable": "Undeliverable: no email, LinkedIn only"}.get(_v.get(u, ""), "No email on file") if u in _b else ("Not yet verified" if (w and e) else "")) for u, w, e in zip(df["uid"], df["wave"], df["email"])]
df["li_sender"] = [("Supriya Rathour" if (e and l) else "") for e, l in zip(E, df["linkedin"])]


def fmt(wb, **k):
    base = dict(font_name="Calibri", font_size=10, valign="top")
    base.update(k)
    return wb.add_format(base)


# =============================================================== workbook 1
path1 = f"{OUT}/TCL Mecca - Consolidated Contact Database.xlsx"
wb = pd.ExcelWriter(path1, engine="xlsxwriter").book if False else None
import xlsxwriter

wb = xlsxwriter.Workbook(path1, {"strings_to_urls": False, "strings_to_numbers": False})
title = fmt(wb, bold=True, font_size=16, font_color="#1F3864")
h2 = fmt(wb, bold=True, font_size=12, font_color="#1F3864", bottom=1)
txt = fmt(wb, text_wrap=True)
bold = fmt(wb, bold=True)
num = fmt(wb, num_format="#,##0")
th = fmt(wb, bold=True, font_color="white", bg_color="#1F3864", border=1, text_wrap=True)

ws = wb.add_worksheet("Summary")
ws.hide_gridlines(2)
ws.set_column(0, 0, 46)
ws.set_column(1, 6, 15)
ws.write(0, 0, "TCL Mecca campaign: consolidated contact database", title)
ws.write(1, 0, "Built 16 Nov 2026 from: Master Accounts and Contacts.xlsx, Mecca Contact Linkedin URL 06 Nov.xlsx, Zoom Info - Lot 9.csv", txt)
ws.write(2, 0, "Goal: 50 hand-raisers by 31 Dec 2026. Every contact sits on one row of the 'Consolidated Database' tab, with details, plan and drafted messages.", txt)
r = 4


def table(ws, r, heading, header, rows):
    ws.write(r, 0, heading, h2)
    r += 1
    for c, h in enumerate(header):
        ws.write(r, c, h, th)
    for row in rows:
        r += 1
        for c, v in enumerate(row):
            ws.write(r, c, v, num if isinstance(v, (int, float)) else txt)
    return r + 2


e = df[E]
r = table(ws, r, "1. Database at a glance", ["Measure", "Contacts"], [
    ["Contacts in the consolidated database", len(df)],
    ["  from the master sheet", int((~df["source"].str.contains("not in master")).sum())],
    ["  added from ZoomInfo Lot 9 (not in master)", int(df["source"].str.contains("not in master").sum())],
    ["With a valid email", int((df["email"] != "").sum())],
    ["With a LinkedIn profile URL", int((df["linkedin"] != "").sum())],
    ["With a mobile or direct number", int(((df["mobile"] != "") | (df["alt_phone"] != "")).sum())],
    ["Eligible for outreach", len(e)],
    ["  Wave 1 (senior, priority accounts, max 4 per account)", int((e["wave"] == "Wave 1").sum())],
    ["  Wave 2 (everyone else who is eligible)", int((e["wave"] == "Wave 2").sum())],
])
st = df["campaign_status"].value_counts()
r = table(ws, r, "2. Campaign status of every contact", ["Status", "Contacts"], [[k, int(v)] for k, v in st.items()])
pv = e.groupby(["portfolio", "wave"]).size().unstack(fill_value=0)
r = table(ws, r, "3. Eligible contacts by portfolio", ["Portfolio", "Wave 1", "Wave 2", "Total"],
          [[p, int(pv.loc[p].get("Wave 1", 0)), int(pv.loc[p].get("Wave 2", 0)), int(pv.loc[p].sum())] for p in pv.index])
pg = e.groupby(["portfolio", "persona_group", "wave"]).size().unstack(fill_value=0)
r = table(ws, r, "4. Eligible contacts by persona group", ["Portfolio / persona group", "Wave 1", "Wave 2", "Total"],
          [[f"{a}: {b}", int(v.get("Wave 1", 0)), int(v.get("Wave 2", 0)), int(v.sum())] for (a, b), v in pg.iterrows()])
ch = e.groupby(["channel", "wave"]).size().unstack(fill_value=0)
r = table(ws, r, "5. Eligible contacts by channel", ["Channel plan", "Wave 1", "Wave 2", "Total"],
          [[c, int(v.get("Wave 1", 0)), int(v.get("Wave 2", 0)), int(v.sum())] for c, v in ch.iterrows()])
sn = e.groupby(["seniority", "wave"]).size().unstack(fill_value=0)
r = table(ws, r, "6. Eligible contacts by seniority", ["Seniority", "Wave 1", "Wave 2", "Total"],
          [[c, int(v.get("Wave 1", 0)), int(v.get("Wave 2", 0)), int(v.sum())] for c, v in sn.iterrows()])
ct = e["country"].replace("", "Unknown").value_counts().head(12)
r = table(ws, r, "7. Eligible contacts by country (top 12)", ["Country", "Contacts"], [[k, int(v)] for k, v in ct.items()])
ws.write(r, 0, "How to read the database tab", h2)
notes = [
    "Filter 'Campaign status' = Eligible to see who is in the outreach plan. Excluded rows stay in the sheet with the reason.",
    "Wave 1 = priority score of 40 or more (C-suite and leaders at Top 400 / Tier 1-2 accounts, plus warm call history), capped at 4 contacts per account.",
    "Portfolio and persona group are assigned from the designation and department, in the order Cybersecurity, CX, NWS.",
    "Country is taken from the source file where given; otherwise it is inferred from the email domain or phone code (see 'Country source').",
    "Emails are signed 'Team Denave, on behalf of Tata Communications', the same convention as the other campaigns in this lemlist account.",
    "Emails marked Bad Data by the tele-team are not mailed. Those contacts are approached on LinkedIn only where a profile URL exists.",
]
for i, n in enumerate(notes):
    ws.merge_range(r + 1 + i, 0, r + 1 + i, 6, n, txt)

# ---- database tab
ws = wb.add_worksheet("Consolidated Database")
wrap = fmt(wb, text_wrap=True)
plain = fmt(wb)
heads = {g: fmt(wb, bold=True, font_color="white", bg_color=c, border=1, text_wrap=True) for g, c in GROUP_COLOR.items()}
for c, (h, f, w, g) in enumerate(COLS):
    ws.write(0, c, h, heads[g])
    ws.set_column(c, c, w, wrap if g == "draft" or f == "last_remark" else plain)
ws.set_row(0, 32)
for i, row in enumerate(df[[f for _, f, _, _ in COLS]].itertuples(index=False), start=1):
    for c, v in enumerate(row):
        if isinstance(v, (int, float)):
            ws.write_number(i, c, v)
        elif v != "":
            ws.write_string(i, c, str(v))
    ws.set_row(i, 15)
ws.freeze_panes(1, 3)
ws.autofilter(0, 0, len(df), len(COLS) - 1)
green = wb.add_format({"bg_color": "#E2EFDA"})
grey = wb.add_format({"font_color": "#808080"})
ws.conditional_format(1, 1, len(df), 1, {"type": "text", "criteria": "begins with", "value": "Eligible", "format": green})
ws.conditional_format(1, 1, len(df), 1, {"type": "text", "criteria": "begins with", "value": "Excluded", "format": grey})

# ---- templates tab
ws = wb.add_worksheet("Message Templates")
ws.hide_gridlines(2)
ws.set_column(0, 0, 26)
ws.set_column(1, 3, 62)
ws.write(0, 0, "Message templates and sequence", title)
ws.merge_range(1, 0, 1, 3, "Tone: Gulf / Middle East business English. Courteous greeting, clear about who is writing, a consultation offered as an invitation. "
               "Variables: {{firstName}}, {{companyName}}, {{personaHook}}.", txt)
r = 3
ws.write(r, 0, "Sequence", h2)
seq = [("Step", "Channel", "When", "Purpose"),
       ("Email 1", "Email (khalid@ / techtransformation@digitaldenave.com)", "Day 0", "Introduce Tata Communications, persona hook, product in two lines, ask for a consultation call"),
       ("Email 2", "Email, same thread", "Day 3", "A practical angle and a direct ask for a 20-minute call"),
       ("Email 3", "Email, same thread", "Day 8", "Courteous close: reply 'interested' or point to the right colleague"),
       ("LinkedIn visit", "LinkedIn (Supriya Rathour)", "Day 0", "Profile visit before the invite"),
       ("LinkedIn invite", "LinkedIn", "Day 1", "Connection request with a short, non-sales note"),
       ("LinkedIn message", "LinkedIn", "On acceptance", "Short product note and ask for a consultation call"),
       ("LinkedIn follow-up", "LinkedIn", "+4 days", "Reminder: reply 'yes' or introduce the right owner"),
       ("Tele-team call", "Phone", "On any reply, and for Wave 1 from day 2", "Convert interest into a scheduled consultation call")]
for i, row in enumerate(seq):
    for c, v in enumerate(row):
        ws.write(r + 1 + i, c, v, th if i == 0 else txt)
r += len(seq) + 3
sample = dict(first="{{firstName}}", company_short="{{companyName}}", persona_hook="{{personaHook}}")
from copy_blocks import render_all
labels = [("email1_subject", "Email 1: subject"), ("email1_body", "Email 1: body"), ("email2_body", "Email 2: body"), ("email3_body", "Email 3: body"),
          ("li_invite", "LinkedIn: connection note"), ("li_message", "LinkedIn: message after acceptance"), ("li_followup", "LinkedIn: follow-up"), ("call_opener", "Tele-team call opener")]
ws.write(r, 0, "Copy by portfolio", h2)
r += 1
ports = ["CX", "NWS", "Cybersecurity"]
ws.write(r, 0, "Message", th)
for c, p in enumerate(ports):
    ws.write(r, c + 1, f"{p}: {P[p]['product']}", th)
rend = {p: render_all(dict(sample, portfolio=p)) for p in ports}
for k, lab in labels:
    r += 1
    ws.write(r, 0, lab, bold)
    for c, p in enumerate(ports):
        ws.write(r, c + 1, rend[p][k], txt)
r += 3
ws.write(r, 0, "Persona hooks ({{personaHook}})", h2)
r += 1
for c, h in enumerate(["Portfolio", "Persona group", "Hook"]):
    ws.write(r, c, h, th)
for (p, g), hook in HOOKS.items():
    r += 1
    ws.write(r, 0, p, txt)
    ws.write(r, 1, g, txt)
    ws.write(r, 2, hook, txt)
wb.close()

# =============================================================== workbook 2
path2 = f"{OUT}/TCL Mecca - Response and Teleteam Tracker.xlsx"
wb = xlsxwriter.Workbook(path2, {"strings_to_urls": False, "strings_to_numbers": False})
title = fmt(wb, bold=True, font_size=16, font_color="#1F3864")
h2 = fmt(wb, bold=True, font_size=12, font_color="#1F3864", bottom=1)
txt = fmt(wb, text_wrap=True)
th = fmt(wb, bold=True, font_color="white", bg_color="#1F3864", border=1, text_wrap=True)
th_in = fmt(wb, bold=True, font_color="white", bg_color="#833C0B", border=1, text_wrap=True)
th_auto = fmt(wb, bold=True, font_color="white", bg_color="#595959", border=1, text_wrap=True)
big = fmt(wb, bold=True, font_size=22, font_color="#1F3864", align="center", valign="vcenter", border=1)
lab = fmt(wb, bold=True, align="center", valign="vcenter", bg_color="#DDEBF7", border=1, text_wrap=True)
cell = fmt(wb, border=1)
cellw = fmt(wb, border=1, text_wrap=True)
auto = fmt(wb, border=1, bg_color="#F2F2F2")
date = fmt(wb, border=1, num_format="dd-mmm-yyyy")
pct = fmt(wb, bold=True, font_size=22, font_color="#1F3864", align="center", valign="vcenter", border=1, num_format="0%")

CHANNELS = ["Email reply", "LinkedIn reply", "LinkedIn accepted (no reply yet)", "Inbound call / WhatsApp", "Landing page form", "Tele-team call"]
RTYPES = ["Interested: wants a consultation call", "Interested: wants more information", "Interested: wants a proposal", "Asked for a callback",
          "Referred to a colleague", "Not now: revisit later", "Not interested", "Wrong person", "Out of office", "Unsubscribe / do not contact"]
OUTCOMES = ["Not yet called", "Connected: consultation call scheduled", "Connected: callback requested", "Connected: info to be sent",
            "Connected: not interested", "No answer", "Wrong number", "Voicemail / message left", "Gatekeeper"]
STAGES = ["New response", "Tele-team to call", "Call scheduled with specialist", "Consultation call done", "Proposal / next step", "Closed: no interest"]
OWNERS = ["Shivli Banerjee", "Supriya Rathour"]
N = 600

# lists
wl = wb.add_worksheet("Lists")
for c, (name, vals) in enumerate([("Channel", CHANNELS), ("Response type", RTYPES), ("Call outcome", OUTCOMES), ("Stage", STAGES), ("Owner", OWNERS),
                                  ("Y/N", ["Y", "N"]), ("Portfolio", ["CX", "NWS", "Cybersecurity"])]):
    wl.write(0, c, name, th)
    for i, v in enumerate(vals):
        wl.write(i + 1, c, v)
    wl.set_column(c, c, 36)


def rng(col, n):
    L = "ABCDEFG"[col]
    return f"=Lists!${L}$2:${L}${n + 1}"


# contact lookup
lk_cols = [("Contact UID", "uid"), ("Full name", "full_name"), ("Designation", "title"), ("Company", "company"), ("Country", "country"),
           ("Portfolio", "portfolio"), ("Product to pitch", "product"), ("Email", "email"), ("Mobile", "mobile"), ("Alternate phone", "alt_phone"),
           ("Board line", "board_line"), ("LinkedIn URL", "linkedin"), ("Tele-team owner", "tele_owner"), ("Wave", "wave"), ("Past call status", "call_status")]
wk = wb.add_worksheet("Contact Lookup")
for c, (h, f) in enumerate(lk_cols):
    wk.write(0, c, h, th)
    wk.set_column(c, c, 22)
for i, row in enumerate(df[[f for _, f in lk_cols]].itertuples(index=False), start=1):
    for c, v in enumerate(row):
        if v != "":
            wk.write_string(i, c, str(v))
wk.freeze_panes(1, 2)
wk.autofilter(0, 0, len(df), len(lk_cols) - 1)
LAST = len(df) + 1

# response log
ws = wb.add_worksheet("Response Log")
RL = [  # header, width, kind, extra
    ("Date received", 13, "in", "date"), ("Contact UID\n(type to auto-fill)", 13, "in", None), ("Full name", 22, "auto", 2), ("Designation", 26, "auto", 3),
    ("Company", 26, "auto", 4), ("Country", 14, "auto", 5), ("Portfolio", 12, "auto", 6), ("Email", 28, "auto", 8), ("Mobile", 17, "auto", 9),
    ("Alternate phone", 17, "auto", 10), ("LinkedIn URL", 28, "auto", 12), ("Channel", 22, "in", 0), ("Response type", 30, "in", 1),
    ("What they said (short)", 44, "in", None), ("Hand-raiser?\n(Y/N)", 11, "in", 5), ("Tele-team owner", 17, "in", 4), ("Sequence stopped in lemlist? (Y/N)", 14, "in", 5),
    ("Call date", 13, "in", "date"), ("Call outcome", 30, "in", 2), ("Consultation call date", 14, "in", "date"), ("TCL specialist / AM", 20, "in", None),
    ("Stage", 26, "in", 3), ("Next step", 34, "in", None), ("Next step due", 13, "in", "date"), ("Notes", 40, "in", None)]
LIST_N = {0: len(CHANNELS), 1: len(RTYPES), 2: len(OUTCOMES), 3: len(STAGES), 4: len(OWNERS), 5: 2}
for c, (h, w, kind, extra) in enumerate(RL):
    ws.write(0, c, h, th_in if kind == "in" else th_auto)
    ws.set_column(c, c, w)
    for r in range(1, N + 1):
        if kind == "auto":
            ws.write_formula(r, c, f'=IF($B{r + 1}="","",IFERROR(INDEX(\'Contact Lookup\'!${chr(64 + extra)}$2:${chr(64 + extra)}${LAST},MATCH($B{r + 1},\'Contact Lookup\'!$A$2:$A${LAST},0)),"UID not found"))', auto, "")
        elif extra == "date":
            ws.write_blank(r, c, None, date)
        else:
            ws.write_blank(r, c, None, cellw if h.startswith(("What", "Notes", "Next step")) else cell)
    if kind == "in" and isinstance(extra, int):
        ws.data_validation(1, c, N, c, {"validate": "list", "source": rng(extra, LIST_N[extra])})
    if extra == "date":
        ws.data_validation(1, c, N, c, {"validate": "date", "criteria": ">", "value": pd.Timestamp("2026-01-01").to_pydatetime(),
                                        "error_message": "Enter a date, e.g. 17-Nov-2026"})
ws.set_row(0, 44)
ws.freeze_panes(1, 5)
ws.autofilter(0, 0, N, len(RL) - 1)
ws.conditional_format(1, 0, N, len(RL) - 1, {"type": "formula", "criteria": '=$O2="Y"', "format": wb.add_format({"bg_color": "#E2EFDA"})})

# call queue
q = df[(df["wave"] == "Wave 1") | df["campaign_status"].str.startswith(("Already", "Call only"))].copy()
q = q[(q["mobile"] != "") | (q["alt_phone"] != "") | (q["board_line"] != "")]
warm = {"Interested - MQL": 1, "Callback": 2, "Follow UP": 3, "Nurture": 4, "Profiled": 5}
q["call_priority"] = [f"P{warm[c]}: {c}" if c in warm else ("P6: C-suite" if s == "C-suite" else "P7: Leader / other") for c, s in zip(q["call_status"], q["seniority"])]
q = q.sort_values(["call_priority", "priority_score"], ascending=[True, False])
wq = wb.add_worksheet("Tele-team Call Queue")
QC = [("Call priority", "call_priority", 20), ("Tele-team owner", "tele_owner", 16), ("Contact UID", "uid", 11), ("Full name", "full_name", 22),
      ("Designation", "title", 30), ("Company", "company", 26), ("Country", "country", 14), ("Mobile", "mobile", 17), ("Alternate phone", "alt_phone", 17),
      ("Board line", "board_line", 17), ("Email", "email", 28), ("Portfolio", "portfolio", 12), ("Product to pitch", "product", 34),
      ("In email / LinkedIn sequence", "channel", 16), ("Past call status", "call_status", 18), ("Last call remark", "last_remark", 36), ("Call opener", "call_opener", 60)]
QIN = [("Call date", 13, "date"), ("Call outcome", 30, 2), ("Hand-raiser? (Y/N)", 11, 5), ("Consultation call date", 14, "date"), ("Notes / next step", 40, None)]
for c, (h, f, w) in enumerate(QC):
    wq.write(0, c, h, th)
    wq.set_column(c, c, w, wb.add_format({"text_wrap": True, "valign": "top", "font_size": 10}) if f in ("call_opener", "last_remark") else None)
for i, row in enumerate(q[[f for _, f, _ in QC]].itertuples(index=False), start=1):
    for c, v in enumerate(row):
        if v != "":
            wq.write_string(i, c, str(v))
    wq.set_row(i, 15)
base = len(QC)
for j, (h, w, extra) in enumerate(QIN):
    c = base + j
    wq.write(0, c, h, th_in)
    wq.set_column(c, c, w)
    if isinstance(extra, int):
        wq.data_validation(1, c, len(q), c, {"validate": "list", "source": rng(extra, LIST_N[extra])})
wq.set_row(0, 32)
wq.freeze_panes(1, 6)
wq.autofilter(0, 0, len(q), base + len(QIN) - 1)

# dashboard
wd = wb.add_worksheet("Dashboard")
wd.hide_gridlines(2)
wd.set_column(0, 0, 34)
wd.set_column(1, 6, 17)
wd.write(0, 0, "TCL Mecca: responses and hand-raisers", title)
wd.write(1, 0, "Target: 50 hand-raisers by 31 Dec 2026. All figures update from the 'Response Log' and 'Tele-team Call Queue' tabs.", txt)
HR = f"COUNTIF('Response Log'!$O$2:$O${N + 1},\"Y\")+COUNTIF('Tele-team Call Queue'!$T$2:$T${len(q) + 1},\"Y\")"
cards = [("Hand-raisers so far", f"={HR}", big), ("Target", 50, big), ("Progress to target", f"=({HR})/50", pct),
         ("Days left to 31 Dec", '=MAX(0,DATE(2026,12,31)-TODAY())', big), ("Responses logged", f"=COUNTA('Response Log'!$B$2:$B${N + 1})", big),
         ("Consultation calls scheduled", f"=COUNT('Response Log'!$T$2:$T${N + 1})+COUNT('Tele-team Call Queue'!$U$2:$U${len(q) + 1})", big)]
for c, (l, v, f) in enumerate(cards):
    wd.write(3, c, l, lab)
    if isinstance(v, str):
        wd.write_formula(4, c, v, f)
    else:
        wd.write_number(4, c, v, f)
wd.set_row(3, 30)
wd.set_row(4, 40)
wd.set_column(0, 5, 20)
r = 7


def block(r, heading, items, col_letter, extra_hr=True):
    wd.write(r, 0, heading, h2)
    wd.write(r + 1, 0, "", th)
    wd.write(r + 1, 1, "Responses", th)
    wd.write(r + 1, 2, "Hand-raisers", th)
    for i, it in enumerate(items):
        rr = r + 2 + i
        wd.write(rr, 0, it, cell)
        wd.write_formula(rr, 1, f"=COUNTIF('Response Log'!${col_letter}$2:${col_letter}${N + 1},A{rr + 1})", cell)
        wd.write_formula(rr, 2, f"=COUNTIFS('Response Log'!${col_letter}$2:${col_letter}${N + 1},A{rr + 1},'Response Log'!$O$2:$O${N + 1},\"Y\")", cell)
    return r + len(items) + 4


r = block(r, "By channel", CHANNELS, "L")
r = block(r, "By portfolio", ["CX", "NWS", "Cybersecurity"], "G")
r = block(r, "By response type", RTYPES, "M")
r = block(r, "By tele-team owner", OWNERS, "P")
r = block(r, "By stage", STAGES, "V")
wd.write(r, 0, "Tele-team call queue", h2)
wd.write(r + 1, 0, "", th)
wd.write(r + 1, 1, "Contacts", th)
wd.write(r + 1, 2, "Called", th)
wd.write(r + 1, 3, "Hand-raisers", th)
for i, o in enumerate(OWNERS):
    rr = r + 2 + i
    wd.write(rr, 0, o, cell)
    wd.write_formula(rr, 1, f"=COUNTIF('Tele-team Call Queue'!$B$2:$B${len(q) + 1},A{rr + 1})", cell)
    wd.write_formula(rr, 2, f"=COUNTIFS('Tele-team Call Queue'!$B$2:$B${len(q) + 1},A{rr + 1},'Tele-team Call Queue'!$S$2:$S${len(q) + 1},\"<>\")", cell)
    wd.write_formula(rr, 3, f"=COUNTIFS('Tele-team Call Queue'!$B$2:$B${len(q) + 1},A{rr + 1},'Tele-team Call Queue'!$T$2:$T${len(q) + 1},\"Y\")", cell)

# guide
wg = wb.add_worksheet("How to use")
wg.hide_gridlines(2)
wg.set_column(0, 0, 120)
wg.write(0, 0, "How to use this tracker", title)
guide = [
    "WHO: campaign owner logs every email and LinkedIn response in 'Response Log'. Tele-team (Shivli Banerjee, Supriya Rathour) work the 'Tele-team Call Queue' and call every responder.",
    "",
    "RESPONSE LOG (one row per response)",
    "1. Enter the date and the Contact UID (from the consolidated database, e.g. MEC-0042). Name, company, phone, email and LinkedIn fill in automatically.",
    "2. Choose the channel and response type from the drop-downs and note in one line what they said.",
    "3. Mark Hand-raiser = Y for any positive response: wants a consultation call, a callback, a proposal or more information. A LinkedIn acceptance alone is not a hand-raiser.",
    "4. Assign the tele-team owner. The owner calls within one working day, records the call date and outcome, and books the consultation call.",
    "5. Confirm the lemlist sequence has stopped for that contact (lemlist stops on reply automatically; pause it by hand for call or form hand-raisers).",
    "6. Move the stage along until the consultation call is done.",
    "",
    "TELE-TEAM CALL QUEUE",
    "Sorted by call priority: P1 past MQLs, P2 callbacks, P3 follow-ups, P4 nurture, P5 profiled, then C-suite, then other Wave 1 leaders.",
    "Use the call opener in column Q. Record the call date, outcome and whether the contact is a hand-raiser (columns R to V).",
    "A hand-raiser from a call counts once: mark it in the call queue OR the response log, not both.",
    "",
    "DASHBOARD",
    "Counts hand-raisers from both tabs against the target of 50, with splits by channel, portfolio, response type, owner and stage.",
    "",
    "Grey columns are filled by formula. Brown-header columns are for you to fill in.",
]
for i, g in enumerate(guide):
    wg.write(i + 2, 0, g, fmt(wb, text_wrap=True, bold=g.isupper()))
wb.worksheets_objs.sort(key=lambda w: ["How to use", "Dashboard", "Response Log", "Tele-team Call Queue", "Contact Lookup", "Lists"].index(w.name))
wb.get_worksheet_by_name("Dashboard").activate()
wb.close()
print("call queue", len(q), q["call_priority"].value_counts().to_dict())
print(path1, path2)
