# Watt render contract

Use the **`visualize`** tool to render an inline visual **in the conversation** —
not the side-panel artifact, not raw HTML in a message — whenever you'd otherwise
explain in prose: trait-search results, a signal pool or stack, a profile, an
analysis, options to choose between. Prefer a rendered visual to a prose list or
a markdown table, and let the tool handle the rest.

When the visual asks the user to choose, render the options as the tool's
clickable controls so the pick comes back as the user's next message — not a
typed-out menu, not a form.

The visual is what the user reads. The composition behind it — the signal pool,
stack, or roster — is saved to a CSV file, governed by the record contract
(`context/record.md`); this contract owns rendering, that one owns the saved
record.
