# Your money, witnessed on your own phone

Every bank and UPI message on an Indian phone is a record of something that
mattered. `nyaya-money` reads those messages **on the phone**, turns them into
a ledger, learns readable beliefs about your money, and shows them to you as
sentences you can mute, rename and correct.

It has no server, no account, and no model. Nothing leaves the phone. That is
not a policy; it is a property of the code, and you can check it with
`netstat` while it runs.

## What you see

Three kinds of sentence, labelled so you know which is which.

**Look at this** (alerts)

> Rs 12,000 went to kyc.update9@ybl, a first-time recipient, 9 minutes after a
> message from +919811234567 that said 'kyc' and 'blocked'. That is the shape
> of a scam.

**Counted** (facts)

> In the last 30 days Rs 68,123 left and Rs 63,200 came in. Spending is +10%
> against the 30 days before.
>
> Every month around the 2nd, Rs 18,000 to sunil.rent@okaxis. Seen 4 times.

**Learned** (beliefs, found by the program synthesiser in `nyaya/synthesis.py`,
the same search that learns grid physics in the benchmark)

> A payment of under Rs 100 goes to chaiwala@ybl. Right 72 of 72 times.
>
> On Sundays, in the evening, money goes to Zomato. Right 14 of 14 times.

Every learned sentence carries how many times it fired and how many times it
was right, scored against every payment, not just the ones earlier rules left
unexplained. Tap the cross and it is gone for good. Tap a payee and give it a
name you recognise.

## Run it on a real Android phone

This is the honest path today. It is a terminal, not an app store listing.
That is what a demo is; the app comes after ten people keep this installed.

1. Install **Termux** and **Termux:API** from F-Droid (the Play Store builds
   are stale). Open Termux.
2. Paste one line. It installs Python, asks Android for SMS permission,
   installs nyaya, and adds a `money` command. Forty lines; read it first.

    ```
    curl -sL https://raw.githubusercontent.com/let-the-dreamers-rise/nyaya/main/install-termux.sh | bash
    ```

3. Type `money`, then open **http://127.0.0.1:8765/** in the phone's browser.

It reads the inbox once at start. Run `nyaya-money report` in the terminal
for the same sentences as text.

## Run it from an export on a laptop

Install **SMS Backup & Restore**, export messages to XML, copy the file over:

```
nyaya-money serve sms-20260908.xml
```

Or try it with nobody's data at all:

```
nyaya-money serve demo
```

The demo person is Meera: salaried, Bangalore, two accounts, and one bad
afternoon in late August. Nothing in it is real.

## What it will never do

- Open a network connection. The page loads no font, script or image from
  anywhere; the only requests go back to the process on the phone.
- Read a message from a phone number as a transaction. A bank-shaped message
  from a person's number is exactly what phishing looks like, so it is
  dropped before it can enter the ledger.
- Send a belief anywhere. The beliefs are a file: `nyaya-money skill -o mine.py`
  writes them as Python you can open, edit and delete lines from.

## Where the money comes from

The pitch is that the intelligence is yours to keep, so the business cannot be
a subscription, an ad, or your data. Three places money can enter without
breaking that:

1. **The installer pays once.** The person who puts this on a parent's phone
   is the customer. Rs 499, once, for the family version: the same file on
   their phones, with alerts delivered to yours. If the company disappears the
   file keeps working, which is the point and the promise.
2. **Skills as files, later.** A belief file that has learned Tamil bank
   templates, or a district's scam patterns, is worth copying. A place to
   share and pay for skills, with a small cut, is the second business. It
   does not exist until skills are being copied by hand first.
3. **Never:** selling the ledger, referring loans off it, or metering the
   sentences. Axio does the first two and that is why people distrust it.

The number is a hypothesis. It gets tested by asking ten installers whether
they would pay it, before anything is built to collect it.

## Google Play, and why this shape is the compliant one

Since July 2026, `READ_SMS` on Play is allowed only for the default SMS
handler or an approved exception. "SMS-based money management" is a listed
exception, with the rule that such apps "may not exfiltrate or share
non-financial or personal SMS history of a user." An app that reads only
bank messages and sends nothing anywhere is the safest thing on that list.
Until there is an app, Termux and F-Droid need no listing at all.
