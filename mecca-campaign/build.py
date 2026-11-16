"""Build the consolidated TCL Mecca contact database with per-contact drafts.

Usage: python3 build.py <master.xlsx> <linkedin.xlsx> <zoominfo_lot9.csv> <outdir>
"""
import re
import sys
import pandas as pd

from copy_blocks import HOOKS, render_all

MASTER, LINKEDIN, ZOOM, OUT = sys.argv[1:5]


def s(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    v = str(v).strip()
    return "" if v in ("0", "nan", "None", "#REF!") else v


EMAIL_RE = re.compile(r"^[a-z0-9._%+\-']+@[a-z0-9\-]+(\.[a-z0-9\-]+)+$")


def clean_email(v):
    v = s(v).lower().replace(" ", "").strip(".,;")
    return v if EMAIL_RE.match(v) else ""


def clean_li(v):
    v = s(v)
    m = re.search(r"linkedin\.com/in/([^/?#\s]+)", v, re.I)
    return f"https://www.linkedin.com/in/{m.group(1)}" if m else ""


def clean_phone(v):
    v = s(v).lstrip("'").strip()
    if v.endswith(".0"):
        v = v[:-2]
    digits = re.sub(r"\D", "", v)
    if len(digits) < 7:
        return ""
    return v if v.startswith("+") else ("+" + digits if len(digits) >= 11 else v)


PARTICLES = {"al", "el", "bin", "bint", "ibn", "abu", "abdul", "abd", "de", "van", "von", "del", "da", "di"}


def nice(word):
    if not word:
        return word
    if word.isupper() or word.islower():
        return "-".join(p.capitalize() for p in word.split("-"))
    return word


def split_name(full):
    full = re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", s(full))).strip(" .,")
    full = re.sub(r"^(mr|mrs|ms|dr|eng|engr|prof|sheikh|shaikh)\.?\s+", "", full, flags=re.I)
    full = re.sub(r"^(mr|mrs|ms|dr|eng|engr|prof)\.\s*", "", full, flags=re.I)
    parts = [nice(p) for p in full.split(" ") if p]
    if parts and re.match(r"^Dr(joseph|rajeev|faisal|ehab)$", parts[0], re.I):  # "Dr" glued to the name in the source
        parts[0] = parts[0][2:].capitalize()
    if not parts:
        return "", "", ""
    first = parts[0]
    # "Abdul Rahman X" / "Al Something" style first names
    if first.lower() in PARTICLES and len(parts) > 2:
        first = f"{parts[0]} {parts[1]}"
        last = " ".join(parts[2:])
    else:
        last = " ".join(parts[1:])
    return first, last, " ".join(parts)


def clean_company(v):
    v = re.sub(r"\s+", " ", s(v))
    v = re.sub(r"\s*\((?!.*\b[A-Z]{2,}\b).*?\)\s*$", "", v)
    short = re.sub(r",?\s+(P\.?J\.?S\.?C\.?|L\.?L\.?C\.?|W\.?L\.?L\.?|S\.?A\.?[EOK]\.?[GCP]?\.?|Ltd\.?|Limited|Inc\.?|Co\.|FZ-?LLC|FZE|PLC|SAKP|K\.?S\.?C\.?P?\.?|Q\.?P?\.?S\.?C\.?|B\.?S\.?C\.?)$", "", v, flags=re.I)
    return short.strip(" ,.-") or v


DIAL = [("971", "United Arab Emirates"), ("966", "Saudi Arabia"), ("974", "Qatar"), ("965", "Kuwait"),
        ("973", "Bahrain"), ("968", "Oman"), ("962", "Jordan"), ("961", "Lebanon"), ("964", "Iraq"),
        ("20", "Egypt"), ("27", "South Africa"), ("254", "Kenya"), ("234", "Nigeria"), ("260", "Zambia"),
        ("264", "Namibia"), ("256", "Uganda"), ("255", "Tanzania"), ("233", "Ghana"), ("230", "Mauritius"),
        ("261", "Madagascar"), ("212", "Morocco"), ("216", "Tunisia"), ("213", "Algeria"), ("90", "Turkey"),
        ("251", "Ethiopia"), ("258", "Mozambique"), ("244", "Angola"), ("267", "Botswana"), ("250", "Rwanda"),
        ("91", "India"), ("44", "United Kingdom"), ("1", "United States")]
TLD = {"ae": "United Arab Emirates", "sa": "Saudi Arabia", "qa": "Qatar", "kw": "Kuwait", "bh": "Bahrain",
       "om": "Oman", "eg": "Egypt", "za": "South Africa", "ke": "Kenya", "ng": "Nigeria", "jo": "Jordan",
       "lb": "Lebanon", "iq": "Iraq", "tr": "Turkey", "zm": "Zambia", "na": "Namibia", "ug": "Uganda",
       "tz": "Tanzania", "gh": "Ghana", "mu": "Mauritius", "ma": "Morocco", "tn": "Tunisia"}


def guess_country(country, email, *phones):
    if s(country):
        return s(country), "given"
    tld = email.rsplit(".", 1)[-1] if email else ""
    if tld in TLD:
        return TLD[tld], "email domain"
    for p in phones:
        d = re.sub(r"\D", "", p).lstrip("0")
        for code, name in DIAL:
            if d.startswith(code) and len(d) >= 10:
                return name, "phone code"
    return "", ""


def has(t, *pats):
    return any(re.search(p, t) for p in pats)


CYBER = [r"\bcyber", r"secur", r"\bciso\b", r"\bcso\b", r"infosec", r"\bsoc\b", r"\bgrc\b", r"\brisk", r"complian",
         r"privacy", r"data protection", r"\bdpo\b", r"\baudit", r"\biam\b", r"identity", r"threat", r"incident response",
         r"business continuity", r"governance"]
CX = [r"customer", r"\bcx\b", r"contact cent", r"call cent", r"omni", r"experience", r"engagement", r"marketing",
      r"\bcmo\b", r"\bcrm\b", r"loyalty", r"e-?commerce", r"digital", r"\bbrand", r"client (service|relation|success)",
      r"communications?\b", r"chief commercial", r"\bcco\b", r"\bcxo\b", r"\bcdo\b", r"growth"]
NWS = [r"\bit\b", r"\bict\b", r"\bhict\b", r"information tech", r"information system", r"\btechnology", r"\btechnical", r"network",
       r"infrastructure", r"\binfra\b", r"cloud", r"\bcio\b", r"\bcto\b", r"architect", r"data cent", r"\bnoc\b",
       r"service delivery", r"connectivity", r"telecom", r"systems?\b", r"devops", r"\bdigital transformation",
       r"chief (information|technology|digital|technical|data)", r"\bcdo\b", r"platform", r"\bsoftware", r"\bdata\b", r"\bai\b",
       r"engineering"]
NOT_PERSONA = [r"procure", r"purchas", r"supply chain", r"\bsales\b", r"financ", r"\bcfo\b", r"account(s|ing|ant)\b",
               r"\bhr\b", r"human res", r"talent", r"legal", r"counsel", r"\bchef\b", r"construction", r"\bproject",
               r"laborator", r"logistic", r"warehouse", r"facilit", r"\bstore\b", r"quality", r"\bhse\b", r"health",
               r"mechanical", r"electrical", r"civil", r"maintenance", r"production", r"treasury", r"tax\b",
               r"real estate", r"demand planning", r"business development", r"relationship manager", r"\badmin"]


def seniority(title, level):
    t = title.lower()
    if has(t, r"\bchief\b", r"\bc[iteofmdsrx]o\b", r"\bciso\b", r"\bcdo\b", r"\bcco\b", r"\bcxo\b") and not has(t, r"chief of staff", r"office of", r"assistant to", r"\bto (the )?c[a-z]o\b"):
        return "C-suite"
    if has(t, r"\bvp\b", r"\bsvp\b", r"\bevp\b", r"\bavp\b", r"vice president", r"director", r"\bhead\b", r"general manager", r"\bgm\b", r"president"):
        return "Leader"
    if has(t, r"manager", r"\blead\b", r"leader", r"architect", r"principal", r"supervisor"):
        return "Manager"
    lv = level.lower()
    if lv.startswith("c "):
        return "C-suite"
    if lv.startswith(("vp", "director")):
        return "Leader"
    if lv.startswith("manager"):
        return "Manager"
    return "Staff"


def classify(title, dept):
    """Return (portfolio, persona_group) or ("", "") when the title maps to no persona."""
    t = f" {title.lower()} "
    d = dept.lower()
    sen = seniority(title, "")
    it_dept = d in ("it", "information technology", "network", "cloud", "engineering & technical", "cyber security")
    if has(t, r"chief strategy", r"chief development", r"chief commercial", r"railway", r"baggage", r"\bwater\b", r"cargo", r"\bflight", r"\broute", r"retail infrastructure", r"budget", r"terminal operating", r"quality", r"physical security", r"safety", r"\bsales\b"):
        return "", ""
    if not it_dept and not has(t, r"\bit\b", r"\bict\b", r"information", r"cyber", r"network", r"cloud", r"digital", r"\bc[it]o\b", r"technology"):
        # generic words (systems, technical, data, infrastructure, compliance...) only count inside IT / security teams
        t = re.sub(r"systems?|technical|engineering|platform|\bdata\b|infrastructure|\binfra\b|complian|governance|\baudit|\brisk|secur|architect|\bai\b|software", " ", t)
    # --- Cybersecurity first
    if has(t, *CYBER) or d == "cyber security":
        if has(t, r"\bciso\b", r"chief (information )?security", r"chief risk", r"\bcro\b") or (sen == "C-suite" and has(t, r"secur", r"risk", r"cyber")):
            return "Cybersecurity", "C-suite"
        if has(t, r"\brisk", r"\bgrc\b", r"complian", r"privacy", r"data protection", r"\bdpo\b", r"\baudit", r"governance", r"business continuity"):
            return "Cybersecurity", "Risk & compliance"
        if has(t, r"cloud", r"infrastructure", r"\biam\b", r"identity", r"network"):
            return "Cybersecurity", "Cloud & infrastructure security"
        if has(t, r"physical security", r"security guard", r"safety"):
            return "", ""
        return "Cybersecurity", "Below C-suite"
    # --- CX
    cx_title = has(t, *CX)
    nws_title = has(t, *NWS)
    cx_dept = d in ("marketing", "customer experience", "customer success")
    if cx_title and not (it_dept and nws_title and not has(t, r"customer", r"\bcx\b", r"contact cent", r"marketing")):
        if has(t, r"digital transformation", r"chief digital", r"\bcdo\b", r"\bdigital\b") and it_dept:
            pass  # digital leaders sitting in IT go to NWS below
        else:
            if sen == "C-suite":
                return "CX", "C-suite"
            if has(t, r"\bvp\b", r"\bsvp\b", r"\bevp\b", r"vice president", r"director"):
                return "CX", "VP / SVP / Director"
            return "CX", "Heads"
    # --- NWS
    if nws_title or (it_dept and not has(t, *NOT_PERSONA)):
        if has(t, *NOT_PERSONA) and not has(t, r"\bit\b", r"information tech", r"network", r"cloud", r"infrastructure"):
            return "", ""
        if has(t, r"\bcio\b", r"\bcto\b", r"\bcdo\b", r"chief (information|technology|digital|technical|data)", r"vp.{0,6}(it|information tech)", r"vice president.{0,6}(it\b|information tech|technology)"):
            return "NWS", "C-suite / IT leadership"
        if has(t, r"cloud", r"architect", r"digital transformation", r"devops", r"platform"):
            return "NWS", "Cloud & architecture"
        if has(t, r"network", r"infrastructure", r"\binfra\b", r"connectivity", r"telecom", r"data cent", r"\bwan\b"):
            return "NWS", "Network & infrastructure"
        if has(t, r"operations", r"service delivery", r"\bnoc\b", r"support", r"service desk", r"\bops\b"):
            return "NWS", "IT operations"
        if sen in ("C-suite", "Leader"):
            return "NWS", "C-suite / IT leadership"
        return "NWS", "IT operations"
    if cx_dept and not has(t, *NOT_PERSONA) and sen != "Staff":
        if sen == "C-suite":
            return "CX", "C-suite"
        if has(t, r"\bvp\b", r"vice president", r"director"):
            return "CX", "VP / SVP / Director"
        return "CX", "Heads"
    return "", ""


# ---------------------------------------------------------------- load
acc = pd.read_excel(MASTER, sheet_name=0, dtype=str)
con = pd.read_excel(MASTER, sheet_name=1, dtype=str)
li2 = pd.read_excel(LINKEDIN, sheet_name=1, dtype=str)
li1 = pd.read_excel(LINKEDIN, sheet_name=0, dtype=str)
zi = pd.read_csv(ZOOM, dtype=str)

assert (con["Contact Name"] == li2["Contact Name"]).all()
con["li_url"] = li2["Url"].map(clean_li)

# fallback LinkedIn URL from sheet 1 (keyed on email, then org+name)
li1.columns = ["org", "name", "last", "x", "email", "url", "orgkey", "namekey", "k"]
li1["url"] = li1["url"].map(clean_li)
li1 = li1[li1["url"] != ""]
by_email = {clean_email(e): u for e, u in zip(li1["email"], li1["url"]) if clean_email(e)}


def key(*parts):
    return re.sub(r"[^a-z0-9]", "", "".join(s(p) for p in parts).lower())


by_name = {key(o, n, l): u for o, n, l, u in zip(li1["org"], li1["name"], li1["last"], li1["url"])}

acc = acc.drop_duplicates("CRM Org Id").set_index("CRM Org Id")
zi["em"] = zi["Email Address"].map(clean_email)
zi_by_email = {r["em"]: r for _, r in zi.iterrows() if r["em"]}
zi_by_id = {s(r["ZoomInfo Contact ID"]): r for _, r in zi.iterrows()}
zi_by_name = {key(r["First Name"], r["Last Name"]): r for _, r in zi.iterrows()}

rows = []
used_zi = set()
for _, r in con.iterrows():
    email = clean_email(r["Email"])
    first, last, full = split_name(r["Contact Name"])
    z = zi_by_email.get(email) if email else None
    if z is None and s(r["zoom id"]):
        z = zi_by_id.get(s(r["zoom id"]))
    if z is None and s(r["Lot"]).replace(" ", "") == "Lot9":
        z = zi_by_name.get(key(first, last))
    if z is not None:
        used_zi.add(s(z["ZoomInfo Contact ID"]))
    li = r["li_url"] or by_email.get(email, "") or by_name.get(key(r["Organization_Name"], r["Contact Name"]), "")
    if not li and z is not None:
        li = clean_li(z["LinkedIn Contact Profile URL"])
    a = acc.loc[r["Org"]] if r["Org"] in acc.index else None
    mob, alt, board = clean_phone(r["MobileNumber"]), clean_phone(r["AlternateNumber"]), clean_phone(r["Board Line"])
    if z is not None:
        mob = mob or clean_phone(z["Mobile phone"])
        alt = alt or clean_phone(z["Direct Phone Number"])
    country, csrc = guess_country(r["Country"] or (z["Country"] if z is not None else ""), email, mob, alt, board)
    rows.append(dict(
        crm_contact_id=s(r["Contact ID CRM"]), lot=s(r["Lot"]).replace("Lot", "Lot ").replace("  ", " "),
        source={"Zoom ifno": "ZoomInfo", "Zoom info": "ZoomInfo"}.get(s(r["Contactid"]), s(r["Contactid"])),
        company=s(r["Organization_Name"]), crm_org_id=s(r["Org"]), segment=s(r["Segment"]),
        account_tier=s(a["Priority"]) if a is not None else "", account_status=s(a["Account Status"]) if a is not None else "",
        tele_owner=s(r["Resource"]), full_name=full, first=first, last=last, title=s(r["Designation"]),
        department=s(r["Department"]), level=s(r["Level"]), country=country, country_src=csrc, email=email,
        raw_email=s(r["Email"]), linkedin=li, mobile=mob, alt_phone=alt, board_line=board,
        call_status=s(r["Contact Status"]), last_remark=s(r["Remarks"]), zoom_id=s(r["zoom id"]) or (s(z["ZoomInfo Contact ID"]) if z is not None else "")))

# ZoomInfo Lot 9 contacts that are not in the master sheet
org_by_key = {key(clean_company(c)): (c, o) for c, o in zip(con["Organization_Name"], con["Org"])}
for _, z in zi.iterrows():
    if s(z["ZoomInfo Contact ID"]) in used_zi:
        continue
    first, last, full = split_name(f"{s(z['First Name'])} {s(z['Last Name'])}")
    comp, org = org_by_key.get(key(clean_company(z["Company Name"])), (s(z["Company Name"]), ""))
    a = acc.loc[org] if org in acc.index else None
    mob, alt = clean_phone(z["Mobile phone"]), clean_phone(z["Direct Phone Number"])
    rows.append(dict(
        crm_contact_id="", lot="Lot 9", source="ZoomInfo (Lot 9 file, not in master)", company=comp, crm_org_id=org,
        segment=s(a["Seg"]) if a is not None else "", account_tier=s(a["Priority"]) if a is not None else "",
        account_status=s(a["Account Status"]) if a is not None else "", tele_owner=s(a["Resource Name"]) if a is not None else "",
        full_name=full, first=first, last=last, title=s(z["Job Title"]), department=s(z["Department"]),
        level=s(z["Management Level"]), country=s(z["Country"]), country_src="given", email=z["em"], raw_email=s(z["Email Address"]),
        linkedin=clean_li(z["LinkedIn Contact Profile URL"]), mobile=mob, alt_phone=alt, board_line=clean_phone(z["Company HQ Phone"]),
        call_status="Untouched", last_remark="", zoom_id=s(z["ZoomInfo Contact ID"])))

df = pd.DataFrame(rows)

# ---------------------------------------------------------------- classify
df["seniority"] = [seniority(t, l) for t, l in zip(df["title"], df["level"])]
pp = [classify(t, d) for t, d in zip(df["title"], df["department"])]
df["portfolio"] = [p[0] for p in pp]
df["persona_group"] = [p[1] for p in pp]
df["persona_hook"] = [HOOKS.get((p, g), "") for p, g in pp]
df["company_short"] = df["company"].map(clean_company)

BAD_ACC = {"Pipeline", "Lead", "Account Disqualified"}
seen_email, seen_person = set(), set()
status = []
for _, r in df.iterrows():
    pk = key(r["company"], r["full_name"])
    dup = (r["email"] and r["email"] in seen_email) or pk in seen_person
    if r["email"]:
        seen_email.add(r["email"])
    seen_person.add(pk)
    cs = r["call_status"]
    if cs == "DNC":
        st = "Excluded: do not contact (DNC)"
    elif cs.startswith("Disqualified"):
        st = f"Excluded: {cs.lower()}"
    elif cs == "Interested - MQL":
        st = "Already a hand-raiser (MQL): tele-team to progress"
    elif r["account_status"] in BAD_ACC:
        st = f"Excluded: account is {r['account_status'].lower()}"
    elif dup:
        st = "Excluded: duplicate contact"
    elif cs == "Bad Data" and not r["linkedin"]:
        st = "Excluded: bad data (left company / wrong details)"
    elif not r["first"] or len(r["first"]) < 2:
        st = "Excluded: no usable name"
    elif not r["portfolio"]:
        st = "Excluded: title matches no target persona"
    elif r["seniority"] == "Staff":
        st = "Excluded: staff / executive level"
    elif not r["email"] and not r["linkedin"]:
        st = "Call only: no email or LinkedIn URL" if (r["mobile"] or r["alt_phone"]) else "Excluded: no contact channel"
    else:
        st = "Eligible"
    status.append(st)
df["campaign_status"] = status

elig = df["campaign_status"] == "Eligible"
bad = df["call_status"] == "Bad Data"
df["email_ok"] = (df["email"] != "") & ~bad          # bad-data emails are not mailed
df["channel"] = ""
df.loc[elig & df["email_ok"] & (df["linkedin"] != ""), "channel"] = "Email + LinkedIn"
df.loc[elig & df["email_ok"] & (df["linkedin"] == ""), "channel"] = "Email only"
df.loc[elig & ~df["email_ok"] & (df["linkedin"] != ""), "channel"] = "LinkedIn only"
df.loc[elig & (df["channel"] == ""), "campaign_status"] = "Excluded: bad data (left company / wrong details)"
elig = df["campaign_status"] == "Eligible"

# ---------------------------------------------------------------- priority
WARM = {"Callback": 40, "Follow UP": 35, "Nurture": 25, "Profiled": 20}
score = (df["seniority"].map({"C-suite": 30, "Leader": 20, "Manager": 8}).fillna(0)
         + df["segment"].eq("Top 400") * 15
         + df["account_tier"].map({"Tier 1 - 250 Accounts": 10, "Tier 2 - 250 Accounts": 5}).fillna(0)
         + df["call_status"].map(WARM).fillna(0)
         + (df["channel"] == "Email + LinkedIn") * 5
         + df["country"].isin(["Saudi Arabia", "United Arab Emirates", "Qatar", "Kuwait", "Bahrain", "Oman"]) * 5)
df["priority_score"] = score.where(elig, 0).astype(int)
df = df.sort_values(["priority_score", "company"], ascending=[False, True]).reset_index(drop=True)

# no more than 4 contacts per account in wave 1, so one company is not flooded
rank_in_acc = df[elig.reindex(df.index, fill_value=False) if False else (df["campaign_status"] == "Eligible")].groupby("company").cumcount()
df["rank_in_account"] = rank_in_acc
e = df["campaign_status"] == "Eligible"
w1 = e & (df["rank_in_account"] < 4) & (df["priority_score"] >= 40)
df["wave"] = ""
df.loc[e, "wave"] = "Wave 2"
df.loc[w1, "wave"] = "Wave 1"
df.insert(0, "uid", [f"MEC-{i + 1:04d}" for i in range(len(df))])

# alternate the two mailboxes per account (same account always gets the same sender)
mailbox = {}
MB = ["khalid@digitaldenave.com", "techtransformation@digitaldenave.com"]
for c in df.loc[e & df["email_ok"], "company"]:
    mailbox.setdefault(c, MB[len(mailbox) % 2])
df["mailbox"] = [mailbox.get(c, "") if (ok and el) else "" for c, ok, el in zip(df["company"], df["email_ok"], e)]

# ---------------------------------------------------------------- drafts
drafts = [render_all(r) if r["campaign_status"] == "Eligible" else {} for _, r in df.iterrows()]
for col in ["email1_subject", "email1_body", "email2_body", "email3_body", "li_invite", "li_message", "li_followup", "call_opener"]:
    df[col] = [d.get(col, "") for d in drafts]
for c in ["email1_subject", "email1_body", "email2_body", "email3_body"]:
    df.loc[~df["email_ok"], c] = ""
for c in ["li_invite", "li_message", "li_followup"]:
    df.loc[df["linkedin"] == "", c] = ""

df.to_pickle(f"{OUT}/consolidated.pkl")
print(len(df), "contacts")
print(df["campaign_status"].value_counts().to_string())
print(df[e].groupby(["wave", "portfolio"]).size().unstack(fill_value=0).to_string())
print(df[e]["channel"].value_counts().to_string())
print(df[e].groupby(["wave", "seniority"]).size().unstack(fill_value=0).to_string())
print("li invite max len", df["li_invite"].str.len().max())
