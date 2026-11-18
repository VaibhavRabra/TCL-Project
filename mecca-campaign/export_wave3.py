"""Wave 3: widen the persona net to business leaders, procurement, risk/compliance and IT/CX titles
the first classifier missed, plus the Wave 2 contacts that only have LinkedIn.

Only contacts whose sole exclusion was "title matches no target persona" are reconsidered, so
DNC, pipeline/disqualified accounts, duplicates and bad data stay excluded.

Usage: python3 export_wave3.py <outdir> <resources_site_url>
Writes:
  <outdir>/lemlist_wave3_email.csv     contacts with an email  -> gated-assets campaign
  <outdir>/lemlist_wave3_linkedin.csv  LinkedIn-only contacts -> Wave 1b (LinkedIn track)
"""
import re
import sys
import glob
import pandas as pd

from copy_blocks import HOOKS

out, site = sys.argv[1], sys.argv[2].rstrip("/")
df = pd.read_pickle(f"{out}/consolidated.pkl").fillna("")
done = set()
for f in glob.glob(f"{out}/*uids.txt"):
    done |= set(open(f).read().split())

BIZ_HOOK = ("Leadership teams across the region are planning 2027 around AI, data-residency rules and tighter budgets, "
            "and the technology choices made now tend to fix costs for years.")
PROC_HOOK = ("Technology contracts that renew over the next year are a good moment to consolidate providers and make "
             "cloud, network and security costs more predictable.")

RULES = [  # (pattern on lower-cased title, portfolio, persona group, hook, seniority)
    (r"\b(security|cyber|soc|risk|compliance|bcm|business continuity|audit|governance)\b",
     "Cybersecurity", "Risk & compliance", HOOKS[("Cybersecurity", "Risk & compliance")], "Leader"),
    (r"(customer|\bcx\b|contact cent|call cent|crm|e-?commerce|marketing|brand|experience|commercial|cco\b)",
     "CX", "Heads", HOOKS[("CX", "Heads")], "Leader"),
    (r"\b(it|ict|information|technology|tech|digital|systems?|infrastructure|network|cloud|data|software|application|erp)\b",
     "NWS", "IT operations", HOOKS[("NWS", "IT operations")], "Leader"),
    (r"\b(procurement|purchasing|sourcing|supply chain|vendor)\b",
     "NWS", "Procurement", PROC_HOOK, "Manager"),
    (r"\b(ceo|coo|cfo|cso|cdo|chief|president|general manager|managing director|executive director|founder|owner|board member|deputy general manager)\b",
     "NWS", "Business leadership", BIZ_HOOK, "C-suite"),
]
SKIP = r"\b(sales|chef|supervisor|construction|leasing|television|team lead(er)?|assistant manager|intern|student)\b"


def classify(title):
    t = title.lower()
    if not t or re.search(SKIP, t):
        return None
    for pat, port, grp, hook, sen in RULES:
        if re.search(pat, t):
            return port, grp, hook, sen
    return None


x = df[(df["campaign_status"] == "Excluded: title matches no target persona") & ~df["uid"].isin(done)].copy()
cls = x["title"].map(classify)
x = x[cls.notna()].copy()
cls = cls[cls.notna()]
x["portfolio"], x["persona_group"], x["persona_hook"], x["seniority"] = zip(*cls)
x["wave"] = "Wave 3"

# Wave 2 contacts with LinkedIn only (no email) were not loaded with the email campaign.
li2 = df[(df["campaign_status"] == "Eligible") & (df["wave"] == "Wave 2") & ~df["email_ok"] & (df["linkedin"] != "") & ~df["uid"].isin(done)]

# At most 4 new contacts per company, best seniority first, so no account is flooded.
order = {"C-suite": 0, "Leader": 1, "Manager": 2}
x = x.assign(_o=x["seniority"].map(order)).sort_values(["company", "_o"]).groupby("company").head(4).drop(columns="_o")


def frame(b, with_email):
    return pd.DataFrame(dict(
        email=b["email"] if with_email else "", firstName=b["first"], lastName=b["last"], companyName=b["company_short"],
        jobTitle=b["title"], linkedinUrl=b["linkedin"], phone=b["mobile"].where(b["mobile"] != "", b["alt_phone"]),
        portfolio=b["portfolio"], personaGroup=b["persona_group"], personaHook=b["persona_hook"], seniority=b["seniority"],
        country=b["country"], contactUid=b["uid"], teleOwner=b["tele_owner"], accountSegment=b["segment"], resourcesSite=site))


em = x[x["email_ok"]]
li = pd.concat([x[~x["email_ok"] & (x["linkedin"] != "")], li2])
frame(em, True).to_csv(f"{out}/lemlist_wave3_email.csv", index=False)
frame(li, False).to_csv(f"{out}/lemlist_wave3_linkedin.csv", index=False)
open(f"{out}/wave3_uids.txt", "w").write("\n".join(list(em["uid"]) + list(li["uid"])))
print("email:", len(em), em["portfolio"].value_counts().to_dict(), em["persona_group"].value_counts().to_dict())
print("linkedin-only:", len(li), "(of which Wave 2:", len(li2), ")")
print(em["title"].sample(min(25, len(em)), random_state=1).to_string())
