"""Wave 4: load every remaining contact whose only exclusion was "title matches no target persona".

Wave 3 took the best-fit 497 of these (max 4 per company, some titles skipped). Wave 4 takes the
rest, with no per-company cap and no title filter, because the client confirmed the shared data is
already verified. DNC, pipeline / disqualified accounts, duplicates and bad data stay excluded.

Usage: python3 export_wave4.py <outdir> <resources_site_url>
Writes:
  <outdir>/lemlist_wave4_email.csv     contacts with an email  -> gated-assets campaign
  <outdir>/lemlist_wave4_linkedin.csv  LinkedIn-only contacts -> Wave 1b (LinkedIn track)
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
    if "wave4" not in f:
        done |= set(open(f).read().split())

BIZ_HOOK = ("Leadership teams across the region are planning 2027 around AI, data-residency rules and tighter budgets, "
            "and the technology choices made now tend to fix costs for years.")
PROC_HOOK = ("Technology contracts that renew over the next year are a good moment to consolidate providers and make "
             "cloud, network and security costs more predictable.")
OPS_HOOK = ("Operations teams across the region are under pressure to do more with the same headcount, and much of that "
            "now depends on how reliable the network, cloud and customer channels underneath are.")

RULES = [  # (pattern on lower-cased title, portfolio, persona group, hook, seniority)
    (r"\b(security|cyber|soc|risk|compliance|bcm|business continuity|audit|governance)\b",
     "Cybersecurity", "Risk & compliance", HOOKS[("Cybersecurity", "Risk & compliance")], "Leader"),
    (r"(customer|\bcx\b|contact cent|call cent|crm|e-?commerce|marketing|brand|experience|commercial|sales|cco\b)",
     "CX", "Heads", HOOKS[("CX", "Heads")], "Leader"),
    (r"\b(it|ict|information|technology|tech|digital|systems?|infrastructure|network|cloud|data|software|application|erp)\b",
     "NWS", "IT operations", HOOKS[("NWS", "IT operations")], "Leader"),
    (r"\b(procurement|purchasing|sourcing|supply chain|vendor)\b",
     "NWS", "Procurement", PROC_HOOK, "Manager"),
    (r"\b(ceo|coo|cfo|cso|cdo|chief|president|general manager|managing director|executive director|founder|owner|board member|deputy general manager)\b",
     "NWS", "Business leadership", BIZ_HOOK, "C-suite"),
]


def classify(title):
    t = title.lower()
    for pat, port, grp, hook, sen in RULES:
        if re.search(pat, t):
            return port, grp, hook, sen
    return "NWS", "Operations & other", OPS_HOOK, "Manager"


x = df[(df["campaign_status"] == "Excluded: title matches no target persona") & ~df["uid"].isin(done)].copy()
cls = x["title"].map(classify)
x["portfolio"], x["persona_group"], x["persona_hook"], x["seniority"] = zip(*cls)
x["wave"] = "Wave 4"


def frame(b, with_email):
    return pd.DataFrame(dict(
        email=b["email"] if with_email else "", firstName=b["first"], lastName=b["last"], companyName=b["company_short"],
        jobTitle=b["title"], linkedinUrl=b["linkedin"], phone=b["mobile"].where(b["mobile"] != "", b["alt_phone"]),
        portfolio=b["portfolio"], personaGroup=b["persona_group"], personaHook=b["persona_hook"], seniority=b["seniority"],
        country=b["country"], contactUid=b["uid"], teleOwner=b["tele_owner"], accountSegment=b["segment"], resourcesSite=site))


em = x[x["email_ok"]]
li = x[~x["email_ok"] & (x["linkedin"] != "")]
frame(em, True).to_csv(f"{out}/lemlist_wave4_email.csv", index=False)
frame(li, False).to_csv(f"{out}/lemlist_wave4_linkedin.csv", index=False)
open(f"{out}/wave4_uids.txt", "w").write("\n".join(list(em["uid"]) + list(li["uid"])))
print("candidates:", len(x), "email:", len(em), "linkedin-only:", len(li), "neither:", len(x) - len(em) - len(li))
print(em["portfolio"].value_counts().to_dict(), em["persona_group"].value_counts().to_dict())
