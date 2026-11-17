"""Generate the static gated-assets site for the TCL Mecca campaign into ./public.

Usage: python3 build_site.py
Same structure as the India resources site: a hub page plus one gated page per asset.
The form posts to the webhook set in assets/gate.js, then reveals the asset on the page.
"""
import html
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "public")
TOP = 'Free for IT and business leaders in the Middle East · <b>No sales pitch, no obligation</b>'
FOOT = "Tata Communications · Your details are used only to send this resource and follow up about it."
MORE = [("/soc-score/", "Security readiness score"), ("/cloud/", "Sovereign cloud checklist"), ("/network/", "Multi-cloud network checklist"),
        ("/whatsapp/", "WhatsApp &amp; SMS launch guide"), ("/docs/", "2027 product pack"), ("/", "All free resources")]


def head(title, desc, og):
    e = html.escape
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex">\n<title>{e(title)}</title><meta name="description" content="{e(desc)}">'
            f'<meta property="og:title" content="{e(og)}"><meta property="og:description" content="{e(desc)}">\n'
            f'<link rel="stylesheet" href="/assets/site.css"></head><body>\n<div class="top">{TOP}</div>')


def form(heading, button, asset, product, specialist):
    p = html.escape(product)
    return f'''<div class="formcard" id="form"><h2>{heading}</h2><p class="small">Instant access. It opens on this page as soon as you submit.</p>
<form id="leadform">
<label for="name">Full name</label><input type="text" id="name" name="name" required autocomplete="name">
<label for="email">Work email</label><input type="email" id="email" name="email" required autocomplete="email">
<label for="company">Company</label><input type="text" id="company" name="company" required autocomplete="organization">
<label for="job_title">Job title</label><input type="text" id="job_title" name="job_title" autocomplete="organization-title">
<label for="country">Country</label><input type="text" id="country" name="country" autocomplete="country-name">
<label for="phone">Phone (optional)</label><input type="tel" id="phone" name="phone" autocomplete="tel">
<label class="check"><input type="checkbox" name="wants_call" value="yes"> <span><b>Also book my free 15-minute consultation call</b> with {specialist} to go through my answers.</span></label>
<input type="hidden" name="asset" value="{html.escape(asset)}"><input type="hidden" name="product" value="{p}"><input type="hidden" name="campaign" value="Mecca gated asset - {html.escape(asset)}">
<button type="submit">{button}</button>
<p class="privacy">We'll use these details only for this resource and a follow-up about {p}.</p>
</form></div>'''


def callbox(specialist, noun="team"):
    return f'''<div class="callbox"><h3>Would a second opinion help? Take the free 15-minute consultation call.</h3>
<p>{specialist} will walk through your answers with you and point out the two or three fixes that matter most for your {noun}. No slides, no obligation.</p>
<p><b>To book:</b> reply <b>"CALL"</b> to the email or LinkedIn message that brought you here, and we'll send you a time.</p></div>'''


def more():
    return '<div class="more">' + "".join(f'<a href="{u}">{t} →</a>' for u, t in MORE) + "</div>"


def gated(slug, title, desc, og, eyebrow, h1, lede, inside, bonus, form_html, why, cta, doc_html, call_html):
    lis = "".join(f"<li>{x}</li>" for x in inside)
    cards = "".join(f'<div class="card"><div class="k">{k}</div><h3>{h}</h3><p>{p}</p></div>' for k, h, p in why)
    return (head(title, desc, og) + f'<div id="gate"><header class="hero"><div class="wrap grid"><div><span class="eyebrow"><i></i>{eyebrow}</span>'
            f'<h1>{h1}</h1><p class="lede">{lede}</p>\n<ul class="inside">{lis}</ul>'
            f'<div class="bonus"><span>🎁</span><span><b>Bonus:</b> {bonus}</span></div></div>\n{form_html}</div></header></div>\n'
            f'<section class="band" id="why"><div class="wrap"><div class="cards">{cards}</div></div></section>\n'
            f'<div class="cta-row" id="cta"><a class="btn" href="#form">{cta}</a></div>\n'
            f'<section id="asset"><div class="wrap"><div class="doc"><div class="thanks">Unlocked. Your copy is below. Bookmark this page or use "Save as PDF".</div>\n'
            f'<button class="print" onclick="window.print()">Save as PDF</button>{doc_html}{call_html}\n{more()}</div></div></section>'
            f'<footer>{FOOT}</footer>\n<script src="/assets/gate.js"></script></body></html>\n')


def write(slug, content):
    d = os.path.join(OUT, slug) if slug else OUT
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(content)


if os.path.isdir(OUT):
    shutil.rmtree(OUT)
shutil.copytree(os.path.join(HERE, "assets"), os.path.join(OUT, "assets"))

# ------------------------------------------------------------------ hub
hub_cards = [
    ("2-minute quiz", "What's your 24x7 security readiness score?", "10 yes/no questions, a score out of 100 and a personal fix list.", "/soc-score/", "Get my score"),
    ("Checklist", "Is your cloud ready for in-country data rules?", "12 questions on data residency, AI capacity and cost before you commit 2027 budget.", "/cloud/", "Get the checklist"),
    ("Checklist", "More clouds, slower apps? Fix the network first.", "12 checks for multi-cloud connectivity, SD-WAN and uptime.", "/network/", "Get the checklist"),
    ("Guide", "Customers message first. Is WhatsApp in your journey?", "The WhatsApp Business and SMS launch guide for Gulf brands.", "/whatsapp/", "Get the guide"),
    ("Product pack", "The 2027 product pack", "Three one-page briefs for your budget meeting.", "/docs/", "Get the pack"),
]
write("", head("Free resources for Middle East technology leaders",
               "Checklists, a readiness score and product briefs for sovereign cloud, multi-cloud networks, 24x7 security and WhatsApp + SMS.",
               "Free resources for Middle East technology leaders")
      + '<header class="hero"><div class="wrap"><span class="eyebrow"><i></i>Free resources</span>'
        '<h1>The 2027 planning toolkit for <em>Middle East technology leaders</em></h1>'
        '<p class="lede">Checklists, a 2-minute readiness score and plain-English product briefs for sovereign cloud and AI, multi-cloud networks, 24x7 security and WhatsApp + SMS. Free, instant, no sales pitch.</p></div></header>'
        '<section class="band hub"><div class="wrap"><div class="cards">'
      + "".join(f'<div class="card"><div class="k">{k}</div><h3>{h}</h3><p>{p}</p><a class="btn" href="{u}">{b}</a></div>' for k, h, p, u, b in hub_cards)
      + '</div></div></section><footer>Tata Communications</footer></body></html>\n')

# ------------------------------------------------------------------ cloud checklist (NWS)
SPEC_CLOUD = "a Tata Communications Vayu cloud specialist"
write("cloud", gated(
    "cloud", "The sovereign cloud and AI checklist for Middle East enterprises",
    "12 questions to answer before you commit 2027 cloud and AI budget: data residency, GPU capacity, multi-cloud cost and exit.",
    "Is your cloud ready for in-country data rules?", "Free checklist · Cloud and AI infrastructure",
    "Is your cloud ready for <em>in-country data rules</em>? Answer these 12 questions before you commit 2027 budget.",
    "The checklist technology leaders in the region use to compare hyperscaler regions, private cloud and a sovereign cloud fabric, before the budget is locked.",
    ["The data-residency questions to settle before a workload moves", "How to size AI and GPU capacity without overbuying",
     "The three costs that make multi-cloud bills hard to predict", "A one-page scorecard you can share with finance and risk"],
    "tick the box for a free 15-minute cloud review with a Vayu specialist.",
    form("Get the cloud checklist free", "Unlock the checklist", "Sovereign cloud checklist", "Tata Communications Vayu cloud", SPEC_CLOUD),
    [("Sovereignty", "Control where data lives", "Data-sovereignty controls for workloads that must stay in-country."),
     ("AI-ready", "GPU when you need it", "AI-ready GPU cloud for training and inference, without buying hardware."),
     ("One fabric", "Clouds that connect", "Multi-cloud connectivity on Tata Communications' global network.")],
    "Unlock the checklist",
    '''<h2>The sovereign cloud and AI checklist for Middle East enterprises</h2>
<p>Score each item 0 (not sorted), 1 (partly) or 2 (clear answer). Below 16 out of 24 means the decision needs more work before you sign.</p>
<h3>1. Data and residency</h3><ol><li><strong>Which data must stay in-country?</strong> List the systems holding personal, financial, health or government data. National data-protection laws and sector regulators in the region can restrict where this data is stored and processed.</li>
<li><strong>Where is every copy?</strong> Include backups, DR copies, logs and analytics extracts, not only the primary database.</li>
<li><strong>Who can access it, and from where?</strong> Ask each provider which staff and which countries can reach your data, and how that access is logged.</li></ol>
<h3>2. AI and GPU capacity</h3><ol start="4"><li><strong>Training or inference?</strong> Training needs bursts of large capacity. Inference needs steady, smaller capacity close to users.</li>
<li><strong>How spiky is demand?</strong> If GPUs would sit idle a third of the time or more, owning them is rarely cheaper than renting.</li>
<li><strong>Can the model and its data stay in-region?</strong> Check this before a pilot becomes production.</li></ol>
<h3>3. Multi-cloud cost</h3><ol start="7"><li><strong>Data transfer.</strong> Ask what it costs to move data between clouds and out of each one. It is a common surprise on the bill.</li>
<li><strong>Duplicate services.</strong> List tools you now pay for in more than one cloud: security, monitoring, backup.</li>
<li><strong>Commitments.</strong> Note minimum terms and what happens if a project pauses or moves.</li></ol>
<h3>4. Operations and exit</h3><ol start="10"><li><strong>One view.</strong> Can you see performance and spend across all clouds in one place?</li>
<li><strong>Support.</strong> Who do you call when a critical workload fails at night or on a weekend, and in which time zone?</li>
<li><strong>Exit.</strong> Confirm how you get data out, in what format, and what is deleted afterwards.</li></ol>
<h3>Scorecard</h3><p>Put the 12 questions in a sheet with one column each for <em>hyperscaler region</em>, <em>private cloud</em> and <em>sovereign cloud fabric</em>. Total each column and share it with finance and your data-protection lead before the decision meeting.</p>
<h3>Where Tata Communications Vayu fits</h3><ul><li>AI-ready GPU cloud</li><li>Data-sovereignty controls</li><li>Multi-cloud connectivity on Tata Communications' global network</li><li>Pairs with SD-WAN and managed network services under one plan</li></ul>''',
    callbox(SPEC_CLOUD[0].upper() + SPEC_CLOUD[1:])))

# ------------------------------------------------------------------ network checklist (NWS)
SPEC_NET = "a Tata Communications network specialist"
write("network", gated(
    "network", "The multi-cloud network checklist",
    "12 checks for multi-cloud connectivity, SD-WAN and uptime before your next network renewal.",
    "More clouds, slower apps? Fix the network first.", "Free checklist · Network and connectivity",
    "More clouds, <em>slower apps</em>? Run these 12 checks before your next network renewal.",
    "A practical checklist for heads of network, infrastructure and IT operations whose workloads now sit across several clouds and sites.",
    ["Where multi-cloud traffic really flows, and what it costs", "The SD-WAN questions to ask before you renew circuits",
     "Uptime and service-assurance checks for stretched operations teams", "A one-page scorecard for your renewal meeting"],
    "tick the box for a free 15-minute network review with a specialist.",
    form("Get the network checklist free", "Unlock the checklist", "Multi-cloud network checklist", "Tata Communications SD-WAN and managed network", SPEC_NET),
    [("One plan", "Cloud and network together", "Vayu cloud fabric with SD-WAN and managed network under one plan."),
     ("Global reach", "One network", "Multi-cloud connectivity on Tata Communications' global network."),
     ("Managed", "Less to run", "Managed network services for teams stretched across providers.")],
    "Unlock the checklist",
    '''<h2>The multi-cloud network checklist</h2>
<p>Score each item 0 (not sorted), 1 (partly) or 2 (clear answer). Below 16 out of 24 is a sign the network needs attention before more workloads move.</p>
<h3>1. Traffic and paths</h3><ol><li><strong>Do you have a current map of traffic between sites, data centres and each cloud?</strong> Most performance complaints start with a path nobody drew.</li>
<li><strong>Does cloud-to-cloud traffic go direct?</strong> Traffic that returns through a data centre adds delay and cost.</li>
<li><strong>Are critical applications prioritised?</strong> Voice, payments and customer-facing apps should not compete with backups.</li></ol>
<h3>2. Performance</h3><ol start="4"><li><strong>Do you measure application response from the user's side?</strong> Link uptime alone hides slow applications.</li>
<li><strong>Is there a second path for every important site?</strong> Check that the two paths do not share the same cable route or provider.</li>
<li><strong>How long does a failover take, and when was it last tested?</strong></li></ol>
<h3>3. Cost and contracts</h3><ol start="7"><li><strong>What do you pay per site per month, all in?</strong> Include circuits, devices, licences and support.</li>
<li><strong>Which contracts renew in the next 12 months?</strong> Renewals are the moment to simplify.</li>
<li><strong>How many providers do you manage?</strong> Each one adds a bill, a portal and an escalation path.</li></ol>
<h3>4. Operations and security</h3><ol start="10"><li><strong>Can one team see the whole network in one view?</strong></li>
<li><strong>How long does a new site or cloud connection take?</strong> Days, weeks or a procurement cycle?</li>
<li><strong>Are security policies the same at every site and cloud entry point?</strong></li></ol>
<h3>Where Tata Communications fits</h3><ul><li>SD-WAN and managed network services</li><li>Multi-cloud connectivity on Tata Communications' global network</li><li>Vayu cloud fabric and network under one plan</li></ul>''',
    callbox(SPEC_NET[0].upper() + SPEC_NET[1:])))

# ------------------------------------------------------------------ WhatsApp guide (CX)
SPEC_CX = "a Tata Communications customer-engagement specialist"
write("whatsapp", gated(
    "whatsapp", "WhatsApp Business and SMS launch guide for Gulf brands",
    "A step-by-step launch guide for WhatsApp Business and bulk SMS: sender registration, templates, opt-in, chatbots and SMS fallback.",
    "Customers message first. Is WhatsApp in your journey?", "Free guide · WhatsApp and SMS",
    "Customers message first. Put <em>WhatsApp and SMS</em> into the customer journey, step by step.",
    "The launch guide for CX, digital and contact-centre leaders: one high-volume journey on WhatsApp, with SMS as the fallback, live in weeks.",
    ["Which messages belong on WhatsApp and which on SMS", "Sender registration, templates and opt-in, in the right order",
     "How chatbots hand over to live agents without losing the customer", "A peak-day readiness checklist for campaigns and seasonal volumes"],
    "tick the box for a free 15-minute journey review with a specialist.",
    form("Get the launch guide free", "Unlock the guide", "WhatsApp and SMS launch guide", "WhatsApp Business API and bulk SMS", SPEC_CX),
    [("One platform", "WhatsApp + SMS", "Both channels on one platform, with SMS fallback."),
     ("Automated and human", "Bots and live agents", "Chatbots with a smooth handover to live agents."),
     ("Connected", "CRM and contact centre", "Integrates with your CRM and contact-centre systems.")],
    "Unlock the guide",
    '''<h2>WhatsApp Business and SMS launch guide</h2>
<h3>Step 1. Pick one journey</h3><ul><li>Start with a single high-volume journey: payment reminders, delivery updates, appointment confirmations or OTPs.</li>
<li>Write down what success looks like: fewer calls, faster replies or higher completion.</li></ul>
<h3>Step 2. Decide the job of each channel</h3><ul><li><strong>SMS:</strong> OTPs, alerts and short updates that must reach every phone.</li>
<li><strong>WhatsApp:</strong> richer conversations with images, buttons, order updates, support and two-way chat.</li></ul>
<h3>Step 3. Get SMS ready</h3><ul><li>Register your sender names with the operators or regulator in each country you send to. Unregistered senders are commonly blocked.</li>
<li>Separate promotional and transactional traffic, and respect local sending hours for promotions.</li></ul>
<h3>Step 4. Set up WhatsApp Business</h3><ul><li>Verify your business with Meta and connect a dedicated number.</li>
<li>Apply for the verified badge: a consistent brand name, an active website and public presence help the review.</li>
<li>Submit message templates for approval, in Arabic and English, with variables for personalisation.</li>
<li>Collect and record opt-in before the first business-initiated message.</li></ul>
<h3>Step 5. Automate, then hand over</h3><ul><li>Let the chatbot answer the five most common questions.</li>
<li>Pass the conversation to a live agent with its history when the customer asks, or when the bot cannot help.</li></ul>
<h3>Step 6. Integrate</h3><ul><li>Trigger messages from your CRM, app or order system by API.</li>
<li>Show the conversation inside the contact-centre desktop so agents see one history.</li></ul>
<h3>Step 7. Peak-day readiness</h3><ul><li>Campaign templates approved at least a week ahead.</li><li>Expected peak volume shared with your provider.</li>
<li>Fallback: if a WhatsApp message is not delivered, send the key update by SMS.</li></ul>
<h3>Measure</h3><p>Track delivery rate, read rate, replies and completions per template. Retire weak templates and test new ones each month.</p>''',
    callbox(SPEC_CX[0].upper() + SPEC_CX[1:], "next campaign")))

# ------------------------------------------------------------------ product pack
SPEC_ALL = "a Tata Communications specialist"


def facts(rows):
    return '<table class="facts">' + "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows) + "</table>"


write("docs", gated(
    "docs", "2027 product pack: Vayu cloud, managed security, WhatsApp + SMS",
    "Three one-page briefs for your 2027 budget meeting: Vayu cloud fabric and network, managed security, and WhatsApp Business + bulk SMS.",
    "The 2027 product pack", "Free download · Product pack",
    "Planning 2027? Get the <em>3 one-page briefs</em> your budget meeting needs.",
    "Plain-English briefs for Vayu cloud fabric and network, managed security, and WhatsApp Business + bulk SMS: what each does, who it is for, and when it fits.",
    ["Vayu cloud fabric and network: AI-ready, sovereign, connected", "Managed security: 24x7 detection and response",
     "WhatsApp Business + bulk SMS: one platform, two channels", "A fit check for each, so you know in a minute if it is relevant"],
    "tick the box for a free 15-minute fit call on whichever brief matters most.",
    form("Get the product pack free", "Unlock the pack", "2027 product pack", "Tata Communications Vayu, managed security and WhatsApp + SMS", SPEC_ALL),
    [("Cloud and network", "Vayu cloud fabric", "AI-ready GPU cloud, data-sovereignty controls, multi-cloud connectivity."),
     ("Security", "24x7 managed security", "Detection and response from Tata Communications SOCs."),
     ("Engagement", "WhatsApp + SMS", "WhatsApp Business API and bulk SMS on one platform.")],
    "Unlock the pack",
    "<h2>Brief 1 · Vayu cloud fabric and network</h2>" + facts([
        ("What it is", "Tata Communications Vayu: an AI-ready GPU cloud with data-sovereignty controls and multi-cloud connectivity, running on Tata Communications' global network and paired with SD-WAN and managed network services under one plan."),
        ("Who it's for", "CIOs, CTOs, heads of cloud, infrastructure, network and IT operations."),
        ("Why it matters", "AI and cloud ambitions meet data-residency requirements and tighter budgets. One fabric gives a single view of performance and more predictable spend."),
        ("Good fit if…", "Workloads are spread across several clouds, some data has to stay in-country, or AI projects need GPU capacity without a hardware purchase.")])
    + "<h2>Brief 2 · Managed security</h2>" + facts([
        ("What it is", "24x7 managed detection and response from Tata Communications SOCs, with cloud and network security, identity and access management, and threat intelligence as a service."),
        ("Who it's for", "CISOs, heads of security operations, cloud and infrastructure security, risk and compliance."),
        ("Why it matters", "Alert volumes are rising while experienced analysts are hard to hire, and regulators across the region are tightening requirements."),
        ("Good fit if…", "Cover is thin at night, at weekends or across cloud workloads, or audits take more evidence each cycle.")])
    + "<h2>Brief 3 · WhatsApp Business + bulk SMS</h2>" + facts([
        ("What it is", "WhatsApp Business API and bulk SMS on one platform: verified business profile, chatbots, live-agent handover, SMS fallback, and CRM and contact-centre integration."),
        ("Who it's for", "CX, digital, marketing and contact-centre leaders."),
        ("Why it matters", "Customers increasingly prefer to message rather than call, while contact-centre volumes keep climbing."),
        ("Good fit if…", "WhatsApp still sits outside the core customer journey, or reminders and updates go out on several disconnected tools.")]),
    callbox(SPEC_ALL[0].upper() + SPEC_ALL[1:])))

# ------------------------------------------------------------------ security readiness score (Cyber)
Q = [("Is someone watching security alerts 24 hours a day, 7 days a week, including weekends and public holidays?", "Close the night, weekend and holiday gap first: it is when most serious incidents start."),
     ("Do you know how long it takes, on average, from an alert to a first response?", "Start measuring time to first response. You cannot improve what is not timed."),
     ("Are cloud workloads monitored to the same standard as on-premises systems?", "Bring cloud logs and alerts into the same monitoring as your data centre."),
     ("Is multi-factor authentication enforced for every administrator and remote user?", "Enforce multi-factor authentication for all administrators and remote access."),
     ("Is there a current list of who has privileged access, reviewed in the last 6 months?", "Review privileged accounts and remove access that is no longer needed."),
     ("Have you run an incident-response exercise in the last 12 months?", "Run a tabletop incident exercise this quarter with IT, legal and communications."),
     ("Do you receive threat intelligence specific to your sector and region?", "Add sector and regional threat intelligence so detection reflects who targets you."),
     ("Can you produce evidence for your regulator or auditor within a week?", "Agree the evidence your regulator expects and keep it ready, not rebuilt for each audit."),
     ("Are critical systems patched within a defined, measured time?", "Set and measure a patching target for critical vulnerabilities."),
     ("Is at least one backup copy isolated so ransomware cannot reach it?", "Keep one immutable or isolated backup copy and test a restore.")]
SPEC_SEC = "a Tata Communications security specialist"
qs = "".join(f'<div class="q"><p>{i + 1}. {q}</p><label><input type="radio" name="q{i}" value="1" required> Yes</label>'
             f'<label><input type="radio" name="q{i}" value="0"> No / not sure</label></div>' for i, (q, _) in enumerate(Q))
fix_js = "[" + ", ".join('"' + f.replace('"', '\\"') + '"' for _, f in Q) + "]"
score_page = (head("24x7 security readiness score", "10 yes/no questions. Get your security operations readiness score and a personal fix list in 2 minutes.",
                   "What is your 24x7 security readiness score?")
              + '<header class="hero"><div class="wrap"><span class="eyebrow"><i></i>2-minute self-assessment</span>'
                "<h1>What's your <em>24x7 security readiness</em> score?</h1>\n"
                '<p class="lede">10 yes/no questions. Get a score out of 100 and a personal fix list for every gap. Useful before your next audit or board review.</p></div></header>\n'
              + f'<section class="band" id="quiz"><div class="wrap grid"><div>{qs}</div>\n<div id="gate">'
              + form("See my score and fix list", "Show my score", "Security readiness score", "Tata Communications managed security", SPEC_SEC)
              + '</div></div></section>\n<section id="asset"><div class="wrap"><div class="doc"><div class="thanks">Your 24x7 security readiness score</div>'
                '<div class="score" id="scoreval">–</div><div class="meter"><i id="meterfill" style="width:0"></i></div>\n'
                '<p><b id="verdict"></b></p><h3>Your fix list</h3><ol id="fixes"></ol>\n'
                '<p class="small">This is a self-assessment, not an audit or legal advice.</p>'
              + callbox(SPEC_SEC[0].upper() + SPEC_SEC[1:]) + "\n" + more() + "</div></div></section>"
              + "<script>window.noAutoUnlock=true;var FIX=" + fix_js + ''';
window.extraPayload=function(p){var s=0,a=[];for(var i=0;i<10;i++){var r=document.querySelector('input[name=q'+i+']:checked');var v=r?+r.value:0;s+=v;a.push(v)}p.append("score",s*10);p.append("answers",a.join(""))};
window.onUnlock=function(){var s=0,miss=[];for(var i=0;i<10;i++){var r=document.querySelector('input[name=q'+i+']:checked');var v=r?+r.value:0;s+=v;if(!v)miss.push(FIX[i])}
var pct=s*10;document.getElementById("scoreval").textContent=pct+"/100";document.getElementById("meterfill").style.width=pct+"%";
document.getElementById("verdict").textContent=pct>=80?"Strong. A few gaps to tidy before your next audit.":pct>=50?"Partly ready. Close these gaps this quarter.":"At risk. Treat round-the-clock monitoring and response as a priority project.";
var ol=document.getElementById("fixes");ol.innerHTML="";(miss.length?miss:["No gaps flagged. Re-run this after your next incident exercise."]).forEach(function(m){var li=document.createElement("li");li.textContent=m;ol.appendChild(li)});
document.getElementById("quiz").style.display="none"};
</script>''' + f'<footer>{FOOT}</footer>\n<script src="/assets/gate.js"></script></body></html>\n')
write("soc-score", score_page)
print("built", sorted(os.path.relpath(os.path.join(r, f), OUT) for r, _, fs in os.walk(OUT) for f in fs))
