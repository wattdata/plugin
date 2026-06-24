# Watt plugin — capability index

What the Watt plugin can do, by surface — the map for answering "what can I do
with Watt?", "is Watt good for *Y*?", "what handles *Z*?".

**The Signal Graph's *contents* are not indexed here.** It holds hundreds of
thousands of signals and changes over time — too large to catalog statically, and the only honest way
to know what it holds for a given idea is to **probe it live**. That is exactly
what `/watt:explore` is for: it discovers the graph's shape by exploring it, one
grounded question at a time. So "what does Watt have on *X*?" is answered by
*running* explore, not by reading a list.

## Commands — what the user invokes

| Command | What it does | Answers questions like |
|---|---|---|
| `/watt:quickstart` | Guided first-run setup and orientation: connects Watt to the Signal Graph, gets the Claude settings right, then points to the three ways in (audience · explore · help). | "how does Watt work?", "I just installed this — where do I start?" |
| `/watt:explore` | **Interactive graph exploration.** Probe what the graph actually holds for an idea about people, one concrete question per turn — discover the signals behind it, how big and fresh each is, and what's adjacent. Read-only: never builds, sizes, or exports. | "what does Watt have on *X*?", "is Watt good for *Y*?", "what else relates to *N*?", "how could I reach *Z*?" |
| `/watt:audience` | The audience-lifecycle front door — routes to build / profile / read / export. Carries an explore session's kept signals straight in; takes an owned list (customers, leads) as a build anchor too. | "build me an audience of …", "match my customer list", "find more like my customers", "who's in this audience?", "an audience profile for my client", "export it to an ad platform" |
| `/watt:help` | **Get unstuck with Watt.** Answers what you can do and how (from the docs), tells you what's changed and whether you're current, points you to the right surface, or reaches the team (bug · signal request · feature request · human). Answers first; files fast once the need is clear. For what data exists, it points to `/watt:explore`. | "what can Watt do", "how do I build an audience", "why is X failing", "something's broken", "I need a signal for *Y*", "I need a human", "what's new", "what have I filed / status of WATT-212" |

**Getting connected.** Watt runs on its **Signal Graph connector**, enabled once per host. `/watt:quickstart` confirms it and walks a new user through enabling it — including the admin route when a team or org plan has it locked; it owns the connect path and the recovery docs.

## Audience steps — reached by routing under `/watt:audience` (not separate commands)

- **generate** — build a person audience, anchored on what the user has in hand. **From a description**: discover the signals behind the brief, score them, and compose to the objective — a target size band, the maximum credible reach, or the highest-intent few — or partition the audience into its top groups, or cross the employment graph to a B2B set. **From an owned list** (customers, leads): match it tight, expand it to the widest identity match (households via addresses), score and rank it against signals ("who's hot"), or learn what defines it and hand back the signals to build from. Produces a signal stack + measured reach, or a roster of entity IDs; no export. (Profiling a market — "how many / who's in" — lives in *analyze*, where the headcount is the answer.)
- **analyze** — read who an audience reaches, as aggregates over a deterministic sample (its own signals by share, the traits that define it by lift, skews, freshness); writes a shareable report file on request. Three ways in: a plain-English brief, signals already in hand, or a list of people. Never individual records.
- **activate** — export a built audience as a platform-ready file (Meta, Google, and Reddit), behind an explicit platform/scale/identifier confirmation.

## What `/watt:help` does (one skill, not separate commands)

`/watt:help` answers how-to and "what can Watt do" questions from this index and the live docs, tells you what's changed and whether you're current (from the plugin changelog), and is the channel to the team — draft → confirm → file a bug, signal request, feature request, or human-help, and check or list what's been filed. It answers first and files fast once the need is clear. It never probes the graph itself: a "do you have data on X" question points to `/watt:explore`. Self-contained — it runs on any surface, needing nothing else loaded.

Signal discovery, scoring, the build strategies, list resolution, the aggregate read, and the file writer all run as internal workers behind these surfaces — never user-invoked, never named to the user. The capabilities they power are the ones above.

## What Watt can't do (so "is Watt good for *Y*?" stays honest)

- **US only.** Non-US asks are out of scope.
- **Person audiences, adults only.** Ideas about minors pivot to parents/guardians of that age range.
- **Employer / job-title as a *defining* target isn't supported** — redirect to interest, demographic, or location framing. (Employment-domain signals may still surface as *description* of what the graph holds.)
- **B2B is reached only by anchoring on people** and crossing to their employers — there's no standalone business targeting.
