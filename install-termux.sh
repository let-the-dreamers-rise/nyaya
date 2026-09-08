#!/data/data/com.termux/files/usr/bin/bash
# One line to put the money witness on an Android phone, inside Termux.
#
#   curl -sL https://raw.githubusercontent.com/let-the-dreamers-rise/nyaya/main/install-termux.sh | bash
#
# What it does, in order, and nothing else: installs Python, git and the
# Termux:API bridge; asks Android for SMS permission through Termux:API;
# installs nyaya; adds a `money` command that starts the page. It never sends
# anything anywhere. Read it before you run it; it is short on purpose.
set -e

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }

case "$PREFIX" in
  */com.termux/*) ;;
  *) echo "This installer is for Termux on Android. On a laptop: pip install git+https://github.com/let-the-dreamers-rise/nyaya"; exit 1 ;;
esac

say "1/4  Packages (python, git, termux-api)"
pkg install -y python git termux-api >/dev/null

say "2/4  SMS permission"
if ! command -v termux-sms-list >/dev/null; then
  echo "termux-api did not install. Install the Termux:API app from F-Droid, then run this again."; exit 1
fi
if ! termux-sms-list -l 1 >/dev/null 2>&1; then
  echo "Android will now ask whether Termux may read SMS. Allow it; nothing leaves the phone."
  termux-sms-list -l 1 >/dev/null 2>&1 || true
fi

say "3/4  nyaya"
pip install -q --upgrade "git+https://github.com/let-the-dreamers-rise/nyaya"

say "4/4  The 'money' command"
mkdir -p "$PREFIX/bin"
cat > "$PREFIX/bin/money" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
exec nyaya-money serve "$@"
EOF
chmod +x "$PREFIX/bin/money"

say "Done. Type  money  then open http://127.0.0.1:8765/ in your browser."
echo "To see it as text instead:  nyaya-money report"
