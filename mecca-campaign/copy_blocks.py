"""Message copy for the TCL Mecca campaign: persona hooks and per-portfolio blocks.

Tone: Gulf / Middle East business English. Courteous greeting, respectful and
unhurried, clear about who is writing and why, and a consultation offered as an
invitation rather than a push. No slang, no hard sell.
"""

HOOKS = {
    ("CX", "C-suite"): "Across the region, customers now expect to reach a brand on WhatsApp first, yet in many organisations the channel still sits outside the core customer journey.",
    ("CX", "VP / SVP / Director"): "Many customer experience leaders in the region tell us contact centre volumes keep climbing while customers increasingly prefer to message rather than call.",
    ("CX", "Heads"): "Bringing WhatsApp, SMS and the contact centre into one customer flow is often where CX roadmaps slow down, especially once automation comes into the picture.",
    ("NWS", "C-suite / IT leadership"): "Most technology leaders we speak with in the region are balancing AI and cloud ambitions against data-residency requirements and tighter budgets.",
    ("NWS", "Network & infrastructure"): "Keeping network performance predictable gets harder as more workloads move across several clouds and sites.",
    ("NWS", "Cloud & architecture"): "Hybrid and multi-cloud estates tend to become costly and hard to govern, particularly when some data has to stay in-country.",
    ("NWS", "IT operations"): "Uptime expectations keep rising while IT operations teams are stretched across more platforms and providers than before.",
    ("Cybersecurity", "C-suite"): "Board-level questions on cyber risk are getting sharper as regulators across the region tighten their requirements.",
    ("Cybersecurity", "Below C-suite"): "Most security operations teams we speak with are handling rising alert volumes while experienced analysts remain hard to hire.",
    ("Cybersecurity", "Cloud & infrastructure security"): "Securing identities and workloads across hybrid cloud is moving faster than the tools most teams started with.",
    ("Cybersecurity", "Risk & compliance"): "Keeping pace with cyber and data-protection regulations takes more evidence and more effort with every audit cycle.",
}

# Portfolio blocks. Kept in one place so the lemlist steps and the sheet stay identical.
P = {
    "CX": dict(
        subject="WhatsApp and SMS for {company} customers",
        value="Tata Communications brings the WhatsApp Business API and bulk SMS together on one platform: verified business profile, chatbots with a smooth handover to live agents, SMS fallback when a message does not land, and integration with your CRM and contact centre.",
        ask="Would you be open to a short consultation call with our customer-engagement specialist, to see whether this fits the 2027 plans at {company}?",
        e2="One practical way teams in the region begin: take a single high-volume journey, such as payment reminders, delivery updates or appointment confirmations, and move it to WhatsApp with SMS as the fallback. It usually shows within a few weeks whether customers respond faster and whether call volumes ease.",
        e2_ask="If it is useful, our specialist can walk you through how that would look for {company} in a 20-minute call. Would a slot this week or next suit you?",
        topic="customer messaging on WhatsApp and SMS",
        li_topic="customer engagement on WhatsApp and SMS",
        li_value="I work with Tata Communications, helping enterprises across the Middle East run WhatsApp Business API and bulk SMS on one platform, with chatbots, live-agent handover and CRM integration.",
        product="WhatsApp Business API + bulk SMS platform",
    ),
    "NWS": dict(
        subject="Cloud and network plans at {company}",
        value="Tata Communications Vayu is our cloud fabric: AI-ready GPU cloud, data-sovereignty controls and multi-cloud connectivity, running on our global network and paired with SD-WAN and managed network services under one plan.",
        ask="Would you be open to a short consultation call with our cloud and network specialist, to see whether this is relevant to the 2027 plans at {company}?",
        e2="A point that comes up often: as workloads spread across hyperscalers and private sites, cost and performance become hard to see in one place. Vayu connects those clouds over one fabric, with a single view of performance and more predictable spend, while keeping sensitive data in-country.",
        e2_ask="If it is useful, our specialist can share how this would map to the current setup at {company} in a 20-minute call. Would a slot this week or next suit you?",
        topic="cloud and network modernisation",
        li_topic="cloud, AI infrastructure and network modernisation",
        li_value="I work with Tata Communications, supporting enterprises across the Middle East on Vayu, an AI-ready cloud fabric with data-sovereignty controls and multi-cloud connectivity, alongside SD-WAN and managed network.",
        product="Vayu cloud fabric + SD-WAN / managed network",
    ),
    "Cybersecurity": dict(
        subject="Security operations at {company}",
        value="Tata Communications runs managed security for enterprises in the region: 24x7 detection and response from our SOCs, cloud and network security, identity and access management, and threat intelligence as a service.",
        ask="Would you be open to a short consultation call with our security specialist, to see whether this is relevant to the 2027 priorities at {company}?",
        e2="Many teams we meet have good tools but thin cover at night, at weekends and across cloud workloads. Our managed detection and response service extends your team around the clock, with response times and reporting mapped to the regulations that apply in your sector.",
        e2_ask="If it is useful, our specialist can walk you through how the coverage would look for {company} in a 20-minute call. Would a slot this week or next suit you?",
        topic="24x7 security operations",
        li_topic="security operations and compliance readiness",
        li_value="I work with Tata Communications, supporting enterprises across the Middle East with managed security: 24x7 detection and response, cloud and network security, IAM and threat intelligence.",
        product="Managed security: 24x7 MDR/SOC, cloud & network security, IAM, threat intel",
    ),
}
# Technology & infrastructure leaders are pitched NWS by default (see classify), so no separate cyber hook is needed.

SIGN = "Team Denave\nOn behalf of Tata Communications"


def render_all(r):
    p = P[r["portfolio"]]
    company = r["company_short"]
    first = r["first"]
    hook = r["persona_hook"]
    f = lambda t: t.format(company=company)
    e1 = (f"Dear {first},\n\nGreetings. I am writing on behalf of the Middle East team at Tata Communications.\n\n"
          f"{hook}\n\n{p['value']}\n\n{f(p['ask'])} A one-line reply is enough, and I will arrange a time that suits you.\n\n"
          f"With kind regards,\n{SIGN}")
    e2 = (f"Dear {first},\n\nI trust you are keeping well. Following my earlier note, I thought this might be of interest.\n\n"
          f"{p['e2']}\n\n{f(p['e2_ask'])}\n\nWith kind regards,\n{SIGN}")
    e3 = (f"Dear {first},\n\nI appreciate how full your calendar must be, so I will keep this brief and it will be my last note for now.\n\n"
          f"If {p['topic']} is on the agenda at {company}, a reply with \"interested\" is all I need and I will arrange a consultation call at your convenience. "
          f"If a colleague is better placed to look at this, I would be grateful if you could point me in the right direction.\n\n"
          f"Thank you for your time, and I wish you and the team continued success.\n\nWith kind regards,\n{SIGN}")
    li_invite = f"Dear {first}, greetings. I work with the Middle East team at Tata Communications, alongside technology and business leaders in the region, and would be glad to connect."
    li_msg = (f"Dear {first}, thank you for connecting.\n\n{p['li_value']}\n\n"
              f"Would you be open to a short consultation call with a Tata Communications specialist, to see whether it is relevant for {company}? I would be glad to arrange it at a time that suits you.")
    li_fu = (f"Dear {first}, I hope you are keeping well. I wanted to follow up on my note about {p['li_topic']}.\n\n"
             f"If it is of interest, a simple \"yes\" here is enough and I will set up a 20-minute call with a Tata Communications specialist. If someone else at {company} looks after this, I would appreciate an introduction.")
    call = (f"Good morning {first}, this is [caller name] calling on behalf of Tata Communications. We sent you a short note on {p['topic']}. "
            f"May I take two minutes to check whether it is relevant for {company}, and arrange a consultation call with our specialist?")
    return dict(email1_subject=f(p["subject"]), email1_body=e1, email2_body=e2, email3_body=e3,
                li_invite=li_invite, li_message=li_msg, li_followup=li_fu, call_opener=call)
