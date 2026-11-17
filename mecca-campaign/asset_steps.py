"""Print the lemlist step content for the gated-asset email campaign (Liquid on the `portfolio` lead variable).

Each lead needs the custom variables portfolio, personaHook, contactUid and resourcesSite
(the deployed site address without a trailing slash, for example https://example.vercel.app).
"""
import json

SIGN = "With kind regards,<br>Team Denave<br>On behalf of Tata Communications"


def link(path, text):
    return '<a href="{{resourcesSite}}/' + path + '?src=email&c={{contactUid}}">' + text + "</a>"


def lq(cx, cyber, nws):
    return '{% if portfolio == "CX" %}' + cx + '{% elsif portfolio == "Cybersecurity" %}' + cyber + "{% else %}" + nws + "{% endif %}"


steps = {
    "email1_subject": lq("A WhatsApp and SMS launch guide for {{companyName}}", "A 2-minute security readiness score", "12 cloud questions before 2027 budgets close"),
    "email1": "Dear {{firstName}},<br><br>Greetings. I am writing on behalf of the Middle East team at Tata Communications.<br><br>{{personaHook}}<br><br>"
    + lq("We have put together a short launch guide for WhatsApp Business and SMS: which messages belong on each channel, sender registration and opt-in in the right order, and how a chatbot hands over to a live agent. It is free and opens straight away: " + link("whatsapp/", "the WhatsApp and SMS launch guide") + ".",
         "We have put together a 2-minute self-assessment: 10 yes/no questions, a score out of 100 and a personal fix list for every gap. It is free and useful ahead of an audit or board review: " + link("soc-score/", "get your security readiness score") + ".",
         "We have put together a 12-question checklist to settle before 2027 cloud and AI budgets are locked: data residency, GPU capacity, multi-cloud cost and exit. It is free and opens straight away: " + link("cloud/", "the sovereign cloud checklist") + ".")
    + "<br><br>If it is useful for {{companyName}}, there is a box on the page to request a 15-minute consultation call with our specialist, at a time that suits you.<br><br>" + SIGN,
    "email2": "Dear {{firstName}},<br><br>I trust you are keeping well. Following my earlier note, one more resource that may help with planning for 2027.<br><br>"
    + lq("Three one-page briefs, written for a budget meeting, including WhatsApp Business and bulk SMS on one platform with chatbots, live-agent handover and CRM integration: " + link("docs/", "the 2027 product pack") + ".",
         "Three one-page briefs, written for a budget meeting, including 24x7 managed detection and response, cloud and network security, IAM and threat intelligence: " + link("docs/", "the 2027 product pack") + ".",
         "A 12-point checklist for teams whose workloads now sit across several clouds and sites, covering traffic paths, SD-WAN, uptime and renewals: " + link("network/", "the multi-cloud network checklist") + ".")
    + "<br><br>Both are free, and a reply with \"CALL\" is all I need to arrange a short consultation with our specialist.<br><br>" + SIGN,
    "email3": "Dear {{firstName}},<br><br>I appreciate how full your calendar must be, so this will be my last note for now.<br><br>All of the free resources are on one page, for you or a colleague to use whenever "
    + lq("customer messaging", "security operations", "cloud and network planning") + " comes up at {{companyName}}: " + link("", "the 2027 planning toolkit")
    + ".<br><br>If a consultation call would be useful, a reply with \"CALL\" is enough and I will arrange it at your convenience. If a colleague is better placed to look at this, I would be grateful for an introduction.<br><br>Thank you for your time, and I wish you and the team continued success.<br><br>" + SIGN,
}
if __name__ == "__main__":
    json.dump(steps, open("out/asset_steps.json", "w"), indent=1)
    for k, v in steps.items():
        print(f"=== {k}\n{v}\n")
