#!/usr/bin/env python3
"""Generate the public FDE Assurance Registry page from the REAL chain.

Reads registry/index.json + each entry -> emits portal/landing/trust.html on the
shared design system (system.css) with the canonical nav. Reproducible; honest by
construction (states the real trust model, matching registry/README.md).
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
REG = ROOT / "registry"
OUT = ROOT / "portal" / "landing" / "trust.html"

idx = json.loads((REG / "index.json").read_text())
rows = []
for e in idx.get("entries", []):
    entry = json.loads((ROOT / e["path"]).read_text())
    score = e.get("trust_score")
    rows.append({
        "cert_id": html.escape(e.get("cert_id", "")),
        "claim": html.escape(entry.get("claim", "")),
        "score": "—" if score is None else str(score),
        "sha": e.get("sha256", ""),
        "at": html.escape((e.get("certified_at", "") or "")[:10]),
    })

rows_html = "\n".join(
    f"""        <tr>
          <td class="cid">{r['cert_id']}</td>
          <td>{r['claim']}</td>
          <td class="sc">{r['score']}</td>
          <td><code>{r['sha'][:16]}…</code></td>
          <td>{r['at']}</td>
        </tr>""" for r in rows
)

NAV = """<nav class="top"><div class="wrap navin">
  <a class="brand" href="index.html"><span class="mark">FDE</span> FDE&nbsp;Consultant</a>
  <div class="nlinks">
    <a href="protocols.html">Protocols</a><a href="docs.html">Docs</a><a href="pricing.html">Pricing</a>
    <a href="trust.html" class="active">Registry</a><a href="blog.html">Intelligence</a>
    <a href="https://github.com/selectess/fde-consultants-protocoles" target="_blank" rel="noopener">GitHub</a>
  </div>
  <a class="btn cta" href="docs.html#install">Install the Skill</a>
</div></nav>"""

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FDE Assurance Registry — public, verifiable certifications</title>
<meta name="description" content="Public, append-only log of FDE Assurance Score certifications, linked by a SHA-256 hash chain. Verify any entry with shasum — no account, no external service.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,ital,wght@6..72,0,400;6..72,0,500;6..72,1,400;6..72,1,500&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="system.css">
<style>
  .reg{{width:100%;border-collapse:collapse;margin-top:30px;border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:14px;background:#fffdf8}}
  .reg th{{background:var(--red);color:#fff;text-align:left;padding:12px 14px;font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase}}
  .reg td{{padding:12px 14px;border-top:1px solid var(--line);color:var(--muted);vertical-align:top}}
  .reg td.cid{{font-family:var(--mono);color:var(--ink);white-space:nowrap}}
  .reg td.sc{{font-family:var(--serif);font-size:20px;color:var(--green);text-align:center}}
  .reg code{{font-family:var(--mono);font-size:12px;background:var(--paper);padding:2px 6px;border-radius:5px;color:var(--clay-d)}}
  .note{{background:rgba(217,119,87,.07);border:1px solid rgba(217,119,87,.3);border-radius:12px;padding:16px 18px;color:var(--ink2);font-size:14px;margin-top:26px}}
  .reg-wrap{{overflow-x:auto}}
</style>
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
{NAV}
<header class="hero"><div class="wrap" style="max-width:880px">
  <span class="eyebrow">Publicly auditable</span>
  <h1 style="margin-top:16px">The FDE Assurance <em>Registry.</em></h1>
  <p class="lead" style="max-width:62ch">An append-only log of certified FDE engagements. Each entry references the SHA-256 of the previous one — a tamper-evident chain anyone can verify with <code class="mono">shasum</code>, no account and no external service.</p>
</div></header>

<section><div class="wrap">
  <span class="eyebrow" data-reveal>{len(rows)} certifications</span>
  <h2 data-reveal style="margin-top:12px">Every claim, <em>scored and chained.</em></h2>
  <div class="reg-wrap"><table class="reg" data-reveal>
    <thead><tr><th>Certification</th><th>Claim</th><th>Score</th><th>SHA-256</th><th>Date</th></tr></thead>
    <tbody>
{rows_html}
    </tbody>
  </table></div>

  <h2 data-reveal style="margin-top:54px;font-size:28px">Verify it yourself</h2>
  <pre class="code" data-reveal>git clone https://github.com/selectess/fde-consultants-protocoles
cd fde-consultants-protocoles

<span class="cm"># 1. re-hash each entry, compare to registry/index.json</span>
for f in registry/*.json; do shasum -a 256 "$f"; done

<span class="cm"># 2. run the executable gate (re-hash + prev_hash linkage)</span>
bash modex/verify.sh --registry</pre>

  <div class="note" data-reveal><b>Trust model, stated honestly.</b> The hash chain gives tamper-<em>evidence</em> relative to a root you have already witnessed — it does not, on its own, defend against the registry operator. Real tamper-<em>proofing</em> needs an external anchor (Sigstore Rekor, a signed git tag, or a public timestamp). Until that is wired in, this is a <em>publicly auditable</em> log, not a “tamper-proof” one. See <a href="https://github.com/selectess/fde-consultants-protocoles/blob/main/registry/README.md" style="color:var(--clay-d)">registry/README.md</a>.</div>

  <h2 data-reveal style="margin-top:54px;font-size:28px">Get the certifier</h2>
  <pre class="code" data-reveal><span class="cm"># install the FDE Consultant skill in any Claude Code client</span>
/plugin marketplace add selectess/fde-consultants-protocoles
/plugin install fde-consultant@fde-consultant</pre>
</div></section>

<section><div class="wrap"><div class="final" data-reveal>
  <span class="eyebrow" style="color:var(--clay)">Proof, not promises</span>
  <h2 style="margin:12px auto 0">Certify your own work.</h2>
  <p class="ssub" style="margin:14px auto 0">Install the Skill, run an engagement, and submit it to the registry.</p>
  <div class="hcta" style="justify-content:center;margin-top:24px"><a class="btn cta" href="docs.html#install">Install the Skill →</a><a class="btn ghost" href="protocols.html" style="background:transparent;color:var(--ivory);border-color:rgba(250,247,240,.25)">How it works</a></div>
</div></div></section>

<footer><div class="wrap foot">
  <span>FDE Consultant — {len(rows)} certification(s) · generated from registry/index.json</span>
  <span style="display:flex;gap:18px;flex-wrap:wrap"><a href="index.html">Home</a><a href="protocols.html">Protocols</a><a href="docs.html">Docs</a><a href="pricing.html">Pricing</a><a href="blog.html">Intelligence</a></span>
</div></footer>

<script type="module">
  try{{
    const {{ animate, inView }} = await import("https://cdn.jsdelivr.net/npm/motion@11/+esm");
    inView("[data-reveal]",(el)=>animate(el,{{opacity:[0,1],transform:["translateY(22px)","translateY(0)"]}},{{duration:.6,easing:[.22,1,.36,1]}}),{{margin:"-10% 0px"}});
  }}catch(e){{document.querySelectorAll('[data-reveal]').forEach(el=>{{el.style.opacity='1';el.style.transform='none';}});}}
</script>
</body>
</html>
"""

OUT.write_text(page, encoding="utf-8")
print(f"WROTE {OUT}  ({len(rows)} entries, {len(page)} bytes)")
