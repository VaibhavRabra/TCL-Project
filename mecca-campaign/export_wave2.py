"""Export Wave 2 contacts (with a usable email) for the gated-assets campaign.
Usage: python3 export_wave2.py <outdir> <resources_site_url>"""
import sys, glob
import pandas as pd

out, site = sys.argv[1], sys.argv[2].rstrip("/")
df = pd.read_pickle(f"{out}/consolidated.pkl").fillna("")
done = set()
for f in glob.glob(f"{out}/batch*_uids.txt"):
    done |= set(open(f).read().split())
w = df[(df["wave"] == "Wave 2") & df["email_ok"] & ~df["uid"].isin(done)].sort_values("priority_score", ascending=False)
csv = pd.DataFrame(dict(
    email=w["email"], firstName=w["first"], lastName=w["last"], companyName=w["company_short"], jobTitle=w["title"],
    linkedinUrl=w["linkedin"], phone=w["mobile"].where(w["mobile"] != "", w["alt_phone"]),
    portfolio=w["portfolio"], personaGroup=w["persona_group"], personaHook=w["persona_hook"], seniority=w["seniority"],
    country=w["country"], contactUid=w["uid"], teleOwner=w["tele_owner"], accountSegment=w["segment"], resourcesSite=site))
csv.to_csv(f"{out}/lemlist_wave2_assets.csv", index=False)
open(f"{out}/wave2_assets_uids.txt", "w").write("\n".join(w["uid"]))
print(len(csv), "leads", csv["portfolio"].value_counts().to_dict())
print("missing:", {c: int((csv[c] == "").sum()) for c in ["firstName", "companyName", "personaHook", "portfolio"]})
