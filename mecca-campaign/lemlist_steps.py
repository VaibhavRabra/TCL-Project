"""Print the lemlist step content (Liquid on the `portfolio` lead variable), generated from copy_blocks."""
import json
from copy_blocks import P

C = "{{companyName}}"


def lq(fn):
    f = lambda p: fn(P[p]).format(company=C)
    return ('{% if portfolio == "CX" %}' + f("CX") + '{% elsif portfolio == "Cybersecurity" %}' + f("Cybersecurity")
            + '{% else %}' + f("NWS") + '{% endif %}')


def html(t):
    return t.replace("\n", "<br>")


steps = {
    "email1_subject": lq(lambda p: p["subject"]),
    "email1": html("Dear {{firstName}},\n\nGreetings. I am writing on behalf of the Middle East team at Tata Communications.\n\n{{personaHook}}\n\n"
                   + lq(lambda p: p["value"] + "\n\n" + p["ask"])
                   + " A one-line reply is enough, and I will arrange a time that suits you.\n\nWith kind regards,\nTeam Denave\nOn behalf of Tata Communications"),
    "email2": html("Dear {{firstName}},\n\nI trust you are keeping well. Following my earlier note, I thought this might be of interest.\n\n"
                   + lq(lambda p: p["e2"] + "\n\n" + p["e2_ask"]) + "\n\nWith kind regards,\nTeam Denave\nOn behalf of Tata Communications"),
    "email3": html("Dear {{firstName}},\n\nI appreciate how full your calendar must be, so I will keep this brief and it will be my last note for now.\n\nIf "
                   + lq(lambda p: p["topic"]) + " is on the agenda at " + C + ", a reply with \"interested\" is all I need and I will arrange a consultation call at your convenience. "
                   "If a colleague is better placed to look at this, I would be grateful if you could point me in the right direction.\n\n"
                   "Thank you for your time, and I wish you and the team continued success.\n\nWith kind regards,\nTeam Denave\nOn behalf of Tata Communications"),
    "li_invite": "Dear {{firstName}}, greetings. I work with the Middle East team at Tata Communications, alongside technology and business leaders in the region, and would be glad to connect.",
    "li_message": "Dear {{firstName}}, thank you for connecting.\n\n" + lq(lambda p: p["li_value"])
                  + "\n\nWould you be open to a short consultation call with a Tata Communications specialist, to see whether it is relevant for " + C + "? I would be glad to arrange it at a time that suits you.",
    "li_followup": "Dear {{firstName}}, I hope you are keeping well. I wanted to follow up on my note about " + lq(lambda p: p["li_topic"])
                   + ".\n\nIf it is of interest, a simple \"yes\" here is enough and I will set up a 20-minute call with a Tata Communications specialist. If someone else at " + C + " looks after this, I would appreciate an introduction.",
}
json.dump(steps, open("out/lemlist_steps.json", "w"), indent=1)
for k, v in steps.items():
    print(f"=== {k}\n{v}\n")
