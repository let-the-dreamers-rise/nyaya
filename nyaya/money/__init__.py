"""Money: the first stream a personal intelligence learns you from.

Every bank and UPI message on an Indian phone is a structured record of
something that mattered. This package reads those messages on the phone,
turns them into a ledger, learns readable beliefs about the person's money,
and serves them back as sentences the person can read, mute and correct.

Nothing here opens a network connection. Grep for 'socket' or 'urllib' in
this package and you will find only the local server that binds loopback.
"""

from .parse import Transaction, parse_message, is_bank_sender  # noqa: F401
