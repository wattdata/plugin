# Watt render contract

Use the **`visualize`** tool to render an inline visual whenever you'd otherwise
explain in prose — trait-search results, a signal pool or stack, a profile, an
analysis, options to choose between. Prefer a rendered visual to a prose list or
a markdown table, and let the tool handle the rest.

When the visual asks the user to choose, render the options as the tool's
clickable controls so the pick comes back as the user's next message — not a
typed-out menu, not a form.

Keep the fenced record (with `trait_hash`es) beneath the visual — it's the
durable state the audience flow reads, and the fallback where a visual can't
render.
