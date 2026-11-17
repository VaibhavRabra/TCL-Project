# TCL Mecca gated resources site

Static site, same structure as the India resources site: a hub page and five gated assets.

| Page | Asset | Portfolio |
|---|---|---|
| `/` | Hub: all free resources | all |
| `/soc-score/` | 24x7 security readiness score (10-question quiz) | Cybersecurity |
| `/cloud/` | Sovereign cloud and AI checklist | NWS (Vayu) |
| `/network/` | Multi-cloud network checklist | NWS (SD-WAN / managed network) |
| `/whatsapp/` | WhatsApp Business and SMS launch guide | CX |
| `/docs/` | 2027 product pack (three one-page briefs) | all |

- Edit content in `build_site.py`, then run `python3 build_site.py` to regenerate `public/`.
- Deploy: import the repository in Vercel and set the root directory to `mecca-resources` (output directory `public`, no build step).
- Lead capture: `assets/gate.js` posts each form to a webhook, then reveals the asset on the page. Change `HOOK` there to route Mecca leads elsewhere.
- Links in emails can carry `?src=email&c=<Contact UID>`; both are sent with the form so a form fill can be matched to the contact.
