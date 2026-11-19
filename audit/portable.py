"""Inline the built app for a double-clickable offline review next to its artifacts."""
import json
import re
from pathlib import Path
root = Path(__file__).resolve().parents[1] / "frontend/dist"
html = (root/"index.html").read_text(encoding="utf-8")
script = re.search(r'<script[^>]+src="([^"]+)"[^>]*></script>',html)
style = re.search(r'<link[^>]+href="([^"]+\.css)"[^>]*>',html)
assert script and style
js = (root/script[1]).read_text(encoding="utf-8").replace("</script","<\\/script")
css = (root/style[1]).read_text(encoding="utf-8")
data = json.dumps(json.loads((root/"artifacts/audit.json").read_text(encoding="utf-8"))).replace("<","\\u003c")
html = html.replace(script[0],"").replace(style[0],"<style>"+css+"</style>")
html = html.replace("</body>",'<script id="embedded-audit" type="application/json">'+data+'</script><script type="module">'+js+'</script></body>')
(root/"Open-CodeGuard.html").write_text(html,encoding="utf-8")
