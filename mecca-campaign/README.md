# TCL Mecca campaign

Scripts that build the consolidated contact database, the per-contact drafts and the tele-team tracker, and export lemlist import batches.
Contact data and generated workbooks live in `out/`, which is not committed (personal data).

| Script | What it does |
|---|---|
| `build.py <master.xlsx> <linkedin.xlsx> <zoominfo.csv> out` | Merges the three sources, cleans names/emails/phones, assigns portfolio, persona group, seniority, eligibility, wave and drafts |
| `copy_blocks.py` | Persona hooks and message copy (single source for the sheet and lemlist) |
| `make_workbooks.py out` | Writes the consolidated database workbook and the response / tele-team tracker |
| `lemlist_steps.py` | Prints the lemlist step content (Liquid on the `portfolio` lead variable) |
| `export_batch.py out <n> <max_email_leads>` | Exports the next Wave 1 batch as a lemlist import CSV |

lemlist campaign: `cam_EzzgBKLEAs2F5SEjC` ("TCL Mecca | CX-NWS-Cyber | Email + LinkedIn | Wave 1"), launched 16 Nov 2026 with batch 1 (271 leads).
Senders: khalid@digitaldenave.com, techtransformation@digitaldenave.com, LinkedIn profile of Supriya Rathour.
Only addresses lemlist verifies as deliverable receive email; the rest are approached on LinkedIn only.
