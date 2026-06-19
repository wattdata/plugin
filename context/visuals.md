# Watt render contract

Two jobs, two mechanisms — keep them separate.

**Choices use Interactive inputs.** The closing decision every interactive beat
ends on — and any pick along the way — is offered through **Interactive inputs**,
Claude's native clickable options (multiple-choice, multi-select, ranking).
They're reliable and built for exactly this, and a typed answer always wins. Lead
with them for every choice; never route a decision through the `visualize`
renderer — it can be unavailable, and a choice must not depend on it.

**Rich data uses the `visualize` tool.** Trait-search results, a signal pool or
stack, a profile, an analysis — render them as an inline visual in the
conversation (not the side-panel artifact, not raw HTML in a message) whenever
you'd otherwise explain in prose, and prefer it to a prose list or a markdown
table. It's the nicer path, not a guaranteed one: when it can't render, fall back
to clean prose — never block on it. A display that also asks a question pairs the
two — show the data with `visualize`, collect the pick with Interactive inputs.

The rendered output is what the user reads. The composition behind it — the
signal pool, stack, or roster — is saved to a CSV file, governed by the record
contract (`context/record.md`); this contract owns rendering, that one owns the
saved record.
