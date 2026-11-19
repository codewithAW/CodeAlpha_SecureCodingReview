# Architecture
The React portfolio loads one reviewed JSON snapshot at startup. Hash-based routes work from static hosting. The portable build embeds the same JSON. Filters, counts, source comparisons and print output use that snapshot. Quiz answers stay in browser local storage.

The WebGL vertex shader interpolates between scattered positions and coordinates sampled from six canvas masks. Device size controls the point count. Pointer distance drives local displacement. The canvas observes visibility and reduced-motion preferences. A shield illustration is the non-WebGL fallback.

The Flask application is a separate process. Its session identifies the caller, SQLite stores users and records, and each protected handler enforces its own data boundary. Profiles use an explicit output projection. SQL values are bound parameters. Verified fixes are derived from named passing tests.

The review runner reads a fixed local source path, extracts actual excerpts, exercises SQLite and records scanner output. Baseline excerpts remain inert text. The frontend cannot invoke shell tools, run code or submit scan targets.
