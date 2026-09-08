# Nyaya

**A personal banker in your pocket that is a file, not a service.**

*(nyaya, NYAH-yuh: the Indian school of logic; literally "method, rule". Not
affiliated with Nyaaya, the Indian legal-information nonprofit.)*

Every bank and UPI message on an Indian phone is a record of something that
mattered. Nyaya reads those messages **on the phone**, learns readable
beliefs about your money, and shows them to you as sentences you can mute,
rename and correct. No server, no account, no model, no network connection.
The beliefs are a file. If we disappear, the file keeps working.

```text
Look at this
  - Rs 12,000 went to kyc.update9@ybl, a first-time recipient, 9 minutes after
    a message from +919811234567 that said 'kyc' and 'blocked'. That is the
    shape of a scam.

Counted
  - In the last 30 days Rs 68,123 left and Rs 63,200 came in. Spending is +10%
    against the 30 days before.
  - Every month around the 2nd, Rs 18,000 to sunil.rent@okaxis. Seen 4 times.

Learned
  - A payment of under Rs 100 goes to chaiwala@ybl. Right 72 of 72 times.
  - On Sundays, in the evening, money goes to Zomato. Right 14 of 14 times.
```

Three kinds of sentence, labelled so you know which is which. *Counted* is
arithmetic. *Learned* was found by a program synthesiser searching your own
payments, and every learned line carries how often it fired and how often it
was right, scored against every payment. *Look at this* is a shape worth a
second look: money to someone new, minutes after a stranger's message that
said KYC.

## Put it on a phone

Android, inside Termux. Install **Termux** and **Termux:API** from F-Droid
(the Play Store builds are stale), open Termux, paste one line:

```bash
curl -sL https://raw.githubusercontent.com/let-the-dreamers-rise/nyaya/main/install-termux.sh | bash
```

Allow SMS when Android asks. Type `money`. Open **http://127.0.0.1:8765/** in
the phone's browser. The script is 40 lines and does nothing it does not say;
read it first.

**On a laptop**, from an SMS Backup & Restore export:

```bash
pip install git+https://github.com/let-the-dreamers-rise/nyaya
nyaya-money serve sms-20260908.xml
```

**With nobody's data at all:**

```bash
nyaya-money serve demo
```

The demo person is Meera: salaried, Bangalore, two accounts, one bad
afternoon in late August. Nothing in it is real. `nyaya-money report` prints
the same sentences as text; `nyaya-money skill -o mine.py` writes them as
Python you can open, edit and delete lines from.

## What it will never do

- **Open a network connection.** The page loads no font, script or image from
  anywhere. A test asserts no external URL exists in it and that the server
  binds 127.0.0.1 only. Check it with `netstat` while it runs.
- **Read a message from a phone number as a transaction.** A bank-shaped
  message from a person's number is what phishing looks like. It is dropped
  before it can enter the ledger.
- **Sell the ledger, refer a loan off it, or meter the sentences.** That is
  the incumbents' model and it is why people distrust them.

## Who it is for

The son or daughter in Bangalore whose mother is in Ghaziabad, who reads
about digital-arrest scams and cannot be there. They install it, read it, and
rename the payees. The parent never opens settings. Digital-arrest scams took
Rs 3,012 crore across 241,537 cases in India between 2022 and 2025; the phone
in the victim's hand is enough hardware to catch the shape of one.

## Where the money comes from

Free on your own phone, forever. **Rs 499, once,** for the family version:
the same file on your parents' phones, with the alerts delivered to yours.
Never monthly, never ads, never your data. A subscription is a revocation
with a due date, and revocation is the thing this sells against. Later,
belief files that have learned a language's bank templates or a district's
scam patterns are worth copying, and a place to share and pay for them is
the second business. [docs/MONEY.md](docs/MONEY.md) has the reasoning and
the Google Play policy that makes this shape the compliant one.

## How it works

1. **Parse.** Bank and UPI messages become a ledger: amount, direction,
   payee, channel. Two dozen small extractors rather than one regex per bank.
2. **Search.** A program synthesiser looks for rules over the ledger: *when
   weekday is Sunday and time is evening, money goes to Zomato*. Every rule is
   a conjunction a person can read, and it ships with its evidence.
3. **Serve.** A 180-line loopback server hands the sentences to the phone's
   own browser. Mutes and names persist to a local file.

The synthesiser is the same one this repository benchmarks against the
frontier on ARC-AGI-3. That story, the cost-capability curve nobody has
drawn, the baselines that beat us and the claims we retracted, is in
[docs/ENGINE.md](docs/ENGINE.md). It is why the learning costs milliseconds
of CPU instead of a frontier call, and why it fits in a 4 GB phone that
cannot run a language model at all.

## Roadmap

| Stage | What | Status |
|---|---|---|
| 0 | Ten phones, by hand. Day-8 keeps. | **now**, September 2026 |
| 1 | An APK under Play's SMS-based money management exception. Bank templates as readable parse rules people can contribute. Hindi, Tamil, Bengali, Marathi sentences. | next |
| 2 | Export a belief file; import someone else's. The first scam-shape rule forwarded between two strangers. | after ten phones |
| 3 | The second stream: who you message and when it stopped. Beliefs across streams. | 2027 |
| 4 | The engine learns a new stream with no new code. Measured on the benchmark, attempted twice, failed twice so far. | research, ongoing |

## Status, for anyone deciding whether to bet on this

Solo founder, India. Public since 31 August 2026; the money product since
8 September. Pre-revenue. Every number above regenerates from a command in
this repo, and when the evidence has gone against us we have published it:
naive Bayes beats our readable rules by nine points of F1, a one-line
heuristic beats our world-model learner, and two of our earlier claims were
retracted in writing. That record is in the commit log and it is the reason
to trust the rest.

**231 tests. MIT. Python 3.9 or later, standard library only.**
[`docs/`](docs/README.md) is indexed by reader.

## Licence

MIT, corpus included. The ARC-AGI-3 logs in `bench/` were produced with the
TAAF/Duck harness; see [docs/LANDSCAPE.md](docs/LANDSCAPE.md) for provenance.
