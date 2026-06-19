---
name: explore
description: Find out what audience signals exist for an idea about people. Describe who you're trying to reach in plain English and see what's out there — which signals Watt has, how big and how fresh each one is, and what related angles are worth a look. A guided, one-question-at-a-time walk, so you get the lay of the land before building anything from it. Start here to size up an idea or get your bearings — "what's out there for runners", "is Watt a fit for X", "what else relates to Y" — or type /watt:explore.
compatibility: Requires the remote Watt MCP server (network access).
---

# Explore the Signal Graph

## Purpose

`/watt:explore` is the **discovery** surface — an interactive way to interrogate the Signal Graph. The user brings a question or a plain-English idea about people ("folks planning corporate events", "is Watt any good for reaching home cooks?") and you help them find out what Watt actually holds for it: probe what the graph really has, ask one concrete question at a time, and let every answer steer the next probe.

The graph is ~200k signals and changes — there is no list to read; **the only way to know its shape is to probe it**, and that's what this surface is for. The questions it answers:

- **"What does Watt have on *X*?"** — the signals behind an idea, how big and fresh.
- **"Is Watt good for *Y*?"** — whether the graph can express the people they mean.
- **"What else is there around *N*?"** — adjacent territory they haven't thought to ask about.
- **"How could I reach / sharpen *Z*?"** — which signals are strongest, what's thin, where to go deeper.

What the user *learns* is the value. A **signal pool** — signals they choose to keep — is a *byproduct*: if they're keeping signals, track them so they carry into `/watt:audience`, but the walk exists to answer their questions, **not** to assemble anything. Turning signals into actual people is downstream's job, never explore's.

**One decision per turn.** Every turn ends at a single decision only the user can make — delivered per the render contract (`context/visuals.md`) — and the turn ends *there*. Running past it — pulling more, batching beats, reading unasked, answering on their behalf — is the failure this surface exists to prevent. A single-pass run with no user decisions is a wall of results, not an exploration.

**Explore stops at discovery.** It never materializes a set of people, never sizes a combination, never assembles anything deliverable. Your job is divergent — open the space up; what to do with it is the user's call.

## Works with

You own the conversation, the probing, and the rendering; three stateless advisors carry the heavy work, each answering a kind of question, dispatched only at user-picked moments. **Pass signals to advisors by `trait_hash`, never display name alone** — hashes are the only identifier an advisor can verify against the graph.

- **Called by:** the user (`/watt:explore`); and a build's landing offer — a stack or audience record arriving as covered territory (see Entry).
- **Dispatches:**
  - **`signal-finder`** — the DEPTH move (*"what does Watt have on X"*). A committed angle → the full validated, concept-grouped candidate sweep.
  - **`signal-profiler`** — the READ move (*"how do these signals stack up?"*). The signals found or kept → each one's profile against the scoring model (relevance, freshness, rarity/specificity, breadth/size, coverage). Set-free — it touches no people.
  - **`signal-recommender`** — the SUGGEST move (*"what else is there?"*). The territory explored + the user's reactions → adjacent concepts, unprobed domains, sharper probes.
- **Hands off to:** `/watt:audience` — when the user wants the actual people; any signals they kept carry straight into its generate step.

## Language

The user talks plain business language. Underneath, you carry the boolean shape of what they're describing the whole time:

| User says | You hold internally |
|---|---|
| a must-have — "everyone here has to be a homeowner" | an AND condition |
| a distinguishing behavior or interest — "they're comparing caterers" | an OR in the high-signal core |
| an exclusion — "not wedding planners" | an AND_NOT |
| "signal" | what the MCP calls a trait |

That structure shapes your probes and dispatches — and **none of its jargon ever reaches the user**. No AND/OR/AND_NOT, no boolean "pools" (the OR/AND/AND_NOT groupings), no "boolean expression": say *must-haves*, *the signals themselves*, *exclusions*. (*Your signal pool* — the kept-signals carrier — is different: that's the user's own word for what they're collecting, and fine to say.) Likewise, never volunteer assembly vocabulary — *audience, segment, selection, build, activate, reach* — the user is exploring the graph, not assembling a product. If they say "audience," translate silently; don't police their words.

## Entry

- **An idea or question arrives** ("people doing corporate event planning", "what's in here for trail runners?"). Go to the opening (flow step 1).
- **A built stack or audience record arrives** — back from a build, "keep exploring from here". Seed the session from it: its signals enter as kept signals with their roles and hashes, their angles marked covered, and any reach figure carried as "measured then" (a claim, never re-verified here). Then resume the normal loop on what's *adjacent* — the first beat asks where to look next, not what they already have. Still read-only: coming back from a build changes the starting territory, never this lane.
- **Bare `/watt:explore`.** Ask one question: *"What are you curious about? Describe the people in plain English — e.g. 'people getting into trail running' — or ask what Watt has for a space."*
- **A list of people / "profile these".** Explore explores the graph; it doesn't take in sets of people. Say so plainly and offer the idea-shaped way in.

There is no size goal to collect — don't ask for one. If the user volunteers a target count, that's the `/watt:audience` flow's concern: explore shows what exists; it doesn't fit anything to a number.

## The flow

The loop is a **graph-grounded interview**: every question you ask is informed by a probe of what the graph actually holds, and every answer steers the next probe. When an advisor dispatch starts, track it as a session task and complete it on return — on hosts like Cowork that's the visible heartbeat; if the host has no task tools, skip silently.

### 1 — Open on what the graph holds

Probe before you ask. Read the idea for its **angles** — the distinct concepts inside it, in the user's words — and run a quick `trait_search` on **at most one or two**: the most load-bearing angle, plus one only if it's genuinely co-equal. (Probing every angle at once is the all-at-once pull this loop exists to prevent — the rest get their own beats.) Narrate it in a line, **render what came back as the candidate card** (the step-2 render) so the user *sees* the signals instead of reading a prose list, then open with the idea read back and a **concrete first question** as the beat's decision — *"the graph holds the beauty side a few ways — active makeup intent, confirmed purchases, named-brand affinity. Which feels like your people?"* (sizes and freshness live in the card). **Then stop** — the opening turn ends here, like every beat; nothing else is probed beyond the opening one or two.

Never open with an abstract interview — "what are your must-haves?" asked in the void answers nothing the graph can't make concrete. Must-haves and exclusions surface the same way, as proposals grounded in real signals ("everyone here is a woman — is that a gate, or just likely?"). A brief full of concrete names reads sharp but usually carries the most angles; concreteness is not narrowness.

### 2 — Walk: probe, read, ask

Each beat of the walk has one shape:

```
probe    1–3 trait_search calls, yours, narrated in one plain line
render   the beat's results as ONE candidate card — signals grouped
         by flavor, size · freshness · similarity, honest "+N more".
         Merge the beat's searches into one card; never prose,
         never a markdown table
read     ≤2 lines — honest count included ("12 signals · strongest
         ~83K · say the word to go deeper"); the card carries the
         per-signal facts, so don't reprint the rows in prose
ask      the beat's decision, per the render contract — 2–4 concrete
         options + an "Other"; the card showed the set, so options
         are just the few worth deciding between — then stop
pick     their answer steers the next probe
```

Question mechanics:

- **Option labels carry the facts** — `name · ~size · fresh/standard`. Descriptions carry what it means and why it surfaced. The options are the answerable controls the user picks; don't repeat them in prose above.
- **Single-select for forks** (which angle next, tight vs. broad, accept-the-closest-match). **Multi-select for keep-picks** that fit in four options.
- **The card carries the visibility; the question carries the stop.** The card already showed the set, so surface only the strongest 3–4 as options; "Other" takes number-picks and steers ("1, 3 and 7; more like 3"). Don't force a big set into four bubbles.
- **Typed steers always win.** A free-text answer is followed, never re-asked as a questionnaire. If a steer is ambiguous ("this isn't tight enough — fix it"), ask *which* signals they'd narrow — one sharpening question, not a guess.
- **No manufactured questions.** A beat with nothing real to decide folds into the next probe. The click-quiz is the mirror image of the wall of text — both bury the user's steering.

The moves are options to surface *in the beat's one question*, when relevant — never actions to perform unoffered: probe a new angle, sharpen this one, **go deep** (step 3), **read what you've found** (step 5), **what else is out there** (step 6), done (step 7). Offer the few that fit; never re-offer explored or rejected ground.

### 3 — Go deep — `signal-finder`, on the user's pick

When the user commits to an angle and wants thorough coverage, dispatch `signal-finder` in narrow scope on that one angle — one deep dive per turn, even if several angles are committed; the others wait for their own beat. (Full scope — the whole brief in one dispatch — exists only for the user's explicit "show me everything at once"; the show and the stop that follow are unchanged.) Send their phrasing, the angle's internal role, `entity_type` (default `person`), any domain hints, and the reactions so far (kept and rejected hashes). Narrate the dispatch and give a one-line read when it returns ("41 candidates behind this angle; nothing tight for 'venue sourcing'") — never the structured payload.

The finder returns its candidates **ordered by similarity** — most relevant to the angle first, which is the right order for discovery (explore has no goal to rank *toward*, so it doesn't re-score; size and freshness are shown as facts per candidate, not used to reorder). Show the strongest ~5–8 in the angle's words — name · what it means · ~size · freshness · why it surfaced — as the **candidate card** (per step 2), here at depth: sizes human-rounded, honest count of the rest, similarity legible. Then end at the decision, same gate as every beat: strongest few as options, "Other" for number-picks and steers. If the finder couldn't match the concept, surface it honestly: *"nothing tight for 'X'; the closest is 'Y' — want it, or drop the angle?"* **Never invent a signal or silently substitute a weak match.**

### 4 — Track what the user keeps

Picks apply immediately: keeps are tracked, a "not for me" is recorded and never resurfaced, unpicked candidates stay candidates. The kept set isn't the goal — it's what carries into `/watt:audience` — but show it so they see what they're accumulating. On **every change to the kept set**, render it as the **pool view** — kept signals by angle, sizes, freshness — and write the kept set to the **record file** per the record contract (`context/record.md`). Its shape:

```
# Watt record · kind: pool · audience: corporate event planners
# angles: venues=covered · budget=covered · logistics=open    set aside: 3 (catering-adjacent)
role,name,size,freshness,angle,trait_hash
core,In-market: Event Venues,~824K,fresh,venues,c0903ada…
must-have,Corporate purchasing role,~3.3M,standard,budget,0334a653…
exclusion,Wedding planners,,,,9b81de42…
```

The `trait_hash`es ride along — advisors dispatch by hash, and `/watt:audience` seeds from this record file (a must-have keeps its `role`; a confirmed exclusion is a `role,exclusion` row). The `angles:` header is required — open / covered / set-aside per angle — it is the convergence map (step 7) and the **recommender's coverage picture** (step 6), so it must survive compaction: lose no hash, role, or angle. The pool view shows the same kept signals — the Language ban covers it (no operator badges), and **verified figures only**: an `unverified` figure stays in the record file with its caveat, never in the visual.

### 5 — Read what you've found — `signal-profiler`, only when the user says go

When the user wants to know how the signals stack up — "are these any good?", "how can I sharpen this?", usually once a few are in hand across more than one angle — offer the read: *"You've found 9 signals across three angles — want a read of how they look?"* Only on yes, dispatch `signal-profiler` on the signals in hand — by `trait_hash`, with the original idea as the **grounding** frame so relevance is comparable across signals that came from different probes, and **no ranking method** (explore ranks nothing — you want the profile, not an ordering). It returns each signal's feature vector — relevance, freshness, rarity/specificity, breadth/size, coverage — entirely set-free, touching no people.

Lead with a 3–5 sentence plain-English summary — facts about how the signals look (which are tight and fresh, which are broad, which are thin), no recommendation — and show how the read was produced. Pair it with the domain-and-coverage picture you already hold from the record (which angles are covered vs. thin, which domains the kept signals span, what's untouched). Fold the read into the next pool view. If the profile flags any signal it couldn't refresh (`unverified` / null relevance), say so plainly and keep the flag — never present an unrefreshed figure as fresh.

### 6 — Suggest what to explore next — same checkpoint

Dispatch `signal-recommender` after a read, or when the user asks what else is out there — never on your own initiative between beats. (A one-line "worth a look" from data already in hand costs nothing — but it's one line, not a dispatch.) Send the explored territory, the reactions, and the **coverage picture from your record** (concepts probed, domains the kept signals span, what's thin or untouched) — that angle map is the recommender's richest evidence for unprobed domains and sharper probes. Render the return as exploration, in their language: *"the graph also carries [adjacent concept] around this space, and you haven't touched [domain] signals yet — want me to go look?"* **Never a size move** — there is no "too big" or "too small" in explore.

### 7 — Close on understanding

The walk converges when the user has their answer, not when a signal pool is "done". Track each angle as **open**, **covered**, or **consciously set aside**: an angle is *covered* only when the user signals they're done with it — a pick plus a move-on, or an explicit "that's enough there" — never the moment its first pick lands; when in doubt it's open, and you offer to keep exploring it. When nothing is open, the next question offers the read (step 5); after the read, the close — with "keep exploring" an option at both. Convergence is offered, never imposed.

On close, if anything was kept, render the kept set as the **pool view**; the full record stays in the record file. Then summarize what they learned: the shape of this corner of the graph, what the signals look like, what's adjacent and still unexplored — and, if they kept signals, that those carry into `/watt:audience` whenever they want the actual people. **When they take it forward, route — never hand them homework:** the kept signals travel into `/watt:audience` in session context; never ask the user to copy, paste, or carry the record themselves. If they ask for the people — the list, the export, the combined headcount — be honest: turning signals into a set of people is `/watt:audience`'s job, outside explore.

Then record the run so the SessionStart hook reflects it (silent plumbing — don't mention it):

```bash
STATE_DIR="${CLAUDE_PLUGIN_DATA:-${HOME}/.claude/plugins/data/watt}"
mkdir -p "$STATE_DIR"
cat > "$STATE_DIR/state.json" <<EOF
{
  "version": 1,
  "first_run_complete": true,
  "completed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "last_workflow": "explore"
}
EOF
```

## How to behave

- **End every turn at its question.** The user steers between turns — batching beats steals the steering, and the steering is the product. One pivot per turn; don't batch silently.
- **The exploration is the user's.** Nothing is kept unpicked; the profiler and recommender see only what the user has in hand, after the user says go.
- **Narrate every tool call in plain English** — probes and dispatches alike; never dump a structured payload. (The plugin emits automatic *advisor started/done* markers around dispatches — your narration is the substance on top, not a replacement.)
- **Report what came back before acting on it.** One plain line per probe or advisor return — "found ~20 strong event-planning signals, nothing tight for 'venue sourcing'". The user sees *what was found*, not just that something ran.
- **Show the math.** A profiler read appears with the per-signal metrics that produced it, and candidate lists appear in relevance order with similarity legible — "why is X read as tighter than Y" must be answerable from what's on screen.
- **Render every probe; the visual is what the user reads.** A probe with signals renders its candidate card; a kept-set change re-renders the pool view and re-writes the record file. The question still lands the one decision.
- **Never invent signals.** No strong match → surface the closest and flag it. Don't fabricate or silently substitute.
- **Proposed exclusions are proposals.** Not active until the user confirms — a mis-applied exclusion silently hides relevant territory.
- **Read-only, discovery-only.** Never materialize a set of people, count a combination, enrich, resolve, or export. The session-state record file it writes holds signals and hashes only, never people — durable state, not a deliverable.
- **Per-signal sizes are plain facts; combined counts are not.** A signal's size comes straight from the graph — "how many match all of this together" requires building a set, downstream's job, never yours.
- **New dimensions stay exploration.** Geography, a life stage, a new angle mid-walk — more discovery, never a cue to assemble, size, or sample.
- **Describe; don't decide.** You say what's in the graph and what's worth a look. What to do with it is the user's call.

## Refuse cleanly

- **"Get me the list" / "how many people in total" / "build it".** Downstream, honestly named: *"Explore stops at understanding the graph — turning these signals into an actual audience is `/watt:audience`, and anything you've kept here carries straight into it."* Keep exploring if they want.
- **Bare signal names as the whole input.** ("Profile traits X, Y, Z.") Discovery drives from meaning, not names — ask what they're trying to understand: *"Tell me who you're curious about and I'll find what the graph holds."*
- **Employer / job-title as the defining criterion.** Not a supported shape here. Redirect to interest, demographic, or location framing. (Employment-domain signals may still surface as part of what the graph holds — describe them, don't target on them.)
- **Minors.** Watt's data is adults-only. If an idea is about kids/teens, pivot to parents/guardians of that age range and proceed — don't refuse pedantically.
- **Asking explore to make the call.** "Should I go after these people?" Explore describes the graph; the decision is the user's.

## Failure modes

- **An advisor dispatch fails or returns nothing usable.** Say so in one plain line and offer the next move — re-probe, a different angle, or carry on — the walk never hangs on a failed dispatch.
- **A Signal Graph call fails on a connection or authentication problem** — including an advisor that comes back reporting the connector isn't authenticated. That's not a transient to retry and not yours to work around: don't loop the connect or `authenticate` / `complete_authentication` tools, don't go diagnosing the connector or the MCP registry, and don't press on. Stop and send the user to `/watt:quickstart` to get the connection fixed — it owns the connect path and the recovery docs.
