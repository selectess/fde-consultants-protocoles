/* DeepSCR animated scientific loop — vanilla (the Framer Motion / Motion engine,
   without React, so it runs in the static site, is SEO-safe, and degrades
   gracefully). Drives every [data-dscr] block: 4-step loop, score, verdict,
   alternating ship/veto cases. Respects prefers-reduced-motion. */
(function () {
  var PHASES = [
    { key: "Hypothesis",    power: "Lead",             agent: "Architecte",          max: 25,
      desc: "State a claim a test could falsify — from intent (Vibe) + context. What does it claim to solve?" },
    { key: "Contradiction", power: "Researchers",      agent: "Sceptique",           max: 25,
      desc: "Proof-of-Contradiction: try to refute it — ≥3 failure modes, edge cases. Attack before shipping." },
    { key: "Verification",  power: "Builder",          agent: "Académique · Code Detective", max: 30,
      desc: "Confront with ground truth — tests, logs, file·line, state of the art. Evidence must resolve on disk." },
    { key: "Certification", power: "Certifier ⟂ veto", agent: "Consensus Guard", max: 20,
      desc: "Deterministic synthesis. Survives contradiction → certified. Score + veto → public hash-chained registry." }
  ];
  var CASES = {
    ship: { comps: [25, 25, 30, 12], note: "evidence verified on disk → certified, ship" },
    veto: { comps: [25, 25, 0, 12],  note: "cited files don't resolve → evidence = 0 → veto" }
  };

  function init(root) {
    var nodes = [].slice.call(root.querySelectorAll(".dscr-node"));
    var conns = [].slice.call(root.querySelectorAll(".dscr-conn"));
    var bars = [].slice.call(root.querySelectorAll(".dscr-bar"));
    var detail = root.querySelector(".dscr-detail");
    var caseEl = root.querySelector(".dscr-case");
    var scoreBox = root.querySelector(".dscr-score");
    var scoreVal = root.querySelector("[data-score]");
    var verdict = root.querySelector(".dscr-verdict");
    var loopnote = root.querySelector(".dscr-loopnote");
    var step = 0, cas = "ship", raf, disp = 0;

    function tween(to) {
      if (raf) cancelAnimationFrame(raf);
      var from = disp, t0 = performance.now(), d = 600;
      (function k(n) {
        var p = Math.min(1, (n - t0) / d), e = 1 - Math.pow(1 - p, 4);
        disp = Math.round(from + (to - from) * e);
        if (scoreVal) scoreVal.textContent = disp;
        if (p < 1) raf = requestAnimationFrame(k);
      })(t0);
    }
    function render() {
      var comps = CASES[cas].comps;
      var revealed = comps.map(function (c, i) { return i <= step ? c : 0; });
      var total = revealed.reduce(function (a, b) { return a + b; }, 0);
      nodes.forEach(function (nd, i) {
        nd.classList.toggle("active", i === step);
        nd.classList.toggle("done", i < step);
      });
      conns.forEach(function (c, i) { c.classList.toggle("on", i < step); });
      if (detail) {
        detail.style.opacity = 0;
        setTimeout(function () {
          var p = PHASES[step];
          detail.innerHTML = '<div class="dh"><b>' + p.key + '</b><span class="p">FDE: ' + p.power +
            '</span><span class="a">Deeposit: ' + p.agent + '</span></div><p>' + p.desc + '</p>';
          detail.style.opacity = 1;
        }, 170);
      }
      bars.forEach(function (b, i) {
        var fl = b.querySelector(".fl"), bv = b.querySelector("[data-bv]"), v = revealed[i], max = PHASES[i].max;
        if (fl) { fl.style.width = (v / max * 100) + "%"; fl.classList.toggle("zero", i === 2 && v === 0 && step >= 2); }
        if (bv) bv.textContent = v + " / " + max;
      });
      tween(total);
      var certified = step === 3 && total >= 85, vetoed = step === 3 && total < 85;
      if (verdict) {
        verdict.classList.toggle("hidden", step !== 3);
        verdict.classList.toggle("veto", vetoed);
        verdict.textContent = certified ? "✓ CERTIFIED ≥ 85" : (vetoed ? "✕ VETO · < 85" : "");
      }
      if (scoreBox) scoreBox.classList.toggle("veto", vetoed);
      if (caseEl) { caseEl.textContent = CASES[cas].note; caseEl.classList.toggle("veto", cas === "veto"); }
      if (loopnote) {
        loopnote.classList.toggle("veto", vetoed);
        loopnote.textContent = vetoed
          ? "↺ veto → re-routed to the weakest owner (back to Contradiction)"
          : "↻ the loop never trusts — it verifies";
      }
    }
    render();
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setInterval(function () {
        if (step >= 3) { cas = cas === "ship" ? "veto" : "ship"; step = 0; } else { step++; }
        render();
      }, 2500);
    }
  }

  function boot() {
    [].slice.call(document.querySelectorAll("[data-dscr]")).forEach(init);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
