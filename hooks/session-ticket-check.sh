#!/usr/bin/env bash
#
# session-ticket-check.sh — on SessionStart, ask the help skill for recent ticket
# updates, exactly as a user request would. Wired "asyncRewake": true, so exit 2
# wakes Claude with stdout. Matcher is startup|resume only — clear|compact would
# double-fire. The passive framing (stay quiet if nothing/uncertain) lives in the
# note below, so /watt:help needs no special-casing — it just handles a ticket read.

set -uo pipefail

cat <<'EOF'
Watt: a session has begun. As a quiet background courtesy, surface any of the user's support tickets that changed in the last 3 days — handle it through /watt:help exactly as you would the request "any updates on my tickets in the last few days?", ending on a decision to open one or dismiss. This is unprompted, so keep it light: if nothing changed, there are no tickets, or the check can't run (e.g. the connection isn't ready), say nothing at all and do not prompt to connect or reconnect.
EOF

exit 2   # wake Claude with the note above (asyncRewake)
