"""Export a lemlist import CSV. Usage: python3 export_batch.py <outdir> <batch_no> <max_email_leads>"""
import sys
import pandas as pd

out, batch, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
df = pd.read_pickle(f"{out}/consolidated.pkl").fillna("")
done = set()
import glob
for f in glob.glob(f"{out}/batch*_uids.txt"):
    done |= set(open(f).read().split())
w = df[(df["wave"] == "Wave 1") & ~df["uid"].isin(done)].sort_values("priority_score", ascending=False)
em = w[w["email_ok"]].head(n)
li = w[~w["email_ok"] & (w["linkedin"] != "")]
b = pd.concat([em, li])
csv = pd.DataFrame(dict(
    email=[e if ok else "" for e, ok in zip(b["email"], b["email_ok"])], firstName=b["first"], lastName=b["last"],
    companyName=b["company_short"], jobTitle=b["title"], linkedinUrl=b["linkedin"], phone=b["mobile"].where(b["mobile"] != "", b["alt_phone"]),
    portfolio=b["portfolio"], personaGroup=b["persona_group"], personaHook=b["persona_hook"], seniority=b["seniority"],
    country=b["country"], contactUid=b["uid"], teleOwner=b["tele_owner"], accountSegment=b["segment"]))
csv.to_csv(f"{out}/lemlist_batch{batch}.csv", index=False)
open(f"{out}/batch{batch}_uids.txt", "w").write("\n".join(b["uid"]))
print(len(b), "leads;", len(em), "with email;", (b["linkedin"] != "").sum(), "with LinkedIn")
print(b["portfolio"].value_counts().to_dict(), b["seniority"].value_counts().to_dict())
print((csv["personaHook"] == "").sum(), "missing hooks;", csv["firstName"].eq("").sum(), "missing names")
