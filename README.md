<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg" />
  <img src="assets/banner.svg" width="100%" alt="KAVY — Krishna Anubhav. Engineer, SaaS founder and operator, MBA, now investment banking. Rigorous thinking. Human explanations." />
</picture>

</div>

### The short version

Engineer → SaaS founder/operator → MBA → investment banking. Somewhere in
there I picked up the habit of not trusting a number until I've rebuilt the
model myself — which, if I'm honest, is really just an excuse to keep
writing code for a living after finance told me to stop.

Based in India. On a given night I am equally likely to be arguing with an
EBITDA bridge in a spreadsheet or with a segfault in a terminal, and
neither argument is going noticeably better than the other.

A DCF and a `git rebase` have more in common than people think: both are
just you insisting, with great confidence, that the past can be tidied up
into a story that leads cleanly to the number you already believe.

**The question I keep asking:** does the tool actually help me *understand*
the business, or does it just make the output look confident? Most finance
software optimizes for the second one. I'd rather build the first — even
if that means the "financial model" is a Python script with opinions.

<br/>

### What I've actually shipped

<!-- AUTO:projects:start -->
<table width="100%">
<tr>
<td width="33%" valign="top">

**[photoface](https://github.com/heykav/photoface)**

Face detection (YuNet) + embeddings (SFace), clustered with a greedy online pass and then a proper average-linkage recluster — and once you manually correct a face, it's *pinned*: the algorithm is no longer allowed to have opinions about that one.

`Python` `PySide6` `OpenCV`

</td>
<td width="33%" valign="top">

**[pe-financial-calculator](https://github.com/heykav/pe-financial-calculator)**

LBO modeling, DCF analysis, deal-analysis tooling — the thing I actually underwrite with, not a portfolio-piece demo. If a sensitivity table lies to you, it's this one's fault, and I'd want to know.

`JavaScript` `HTML/CSS`

</td>
<td width="33%" valign="top">

**[fpga-sim-core](https://github.com/heykav/fpga-sim-core)**

Cycle-accurate FPGA datapath sim: deterministic callback scheduling, PCS encode/decode, a five-level order book, zero heap allocation on the hot path — because "close enough" isn't a real answer at the clock-cycle level.

`C++` `CMake`

</td>
</tr>
<tr>
<td width="33%" valign="top">

**[vanna](https://github.com/heykav/vanna)**

Named after the real second-order Greek. Prices options from first principles (Black-Scholes, a binomial tree for early exercise) instead of bucketing historical fills, then decomposes every trade's P&L into delta/gamma/theta/vega/vanna/volga via a Taylor expansion — with the leftover reported honestly as residual, not hidden in whichever bucket makes the total look clean.

`Python` `PySide6` `NumPy`

</td>
<td width="33%" valign="top">

**[microprice-rust](https://github.com/heykav/microprice-rust)**

The mid-price lies to you the instant the book is imbalanced; the micro-price is what you get when you stop pretending the best bid and best ask are equally likely to trade next. Implemented as the actual Markov chain over the queue-imbalance state space — not a smoothed heuristic — because an estimator you'll trade on should survive being asked why it said what it said.

`Rust` `Market Microstructure`

</td>
<td width="33%" valign="top">

**[quantdeck](https://github.com/heykav/quantdeck)**

Grew out of a fix for LiuAlgoTrader (abandoned since 2023, still north of 900 stars) that wanted a Postgres server just to backtest a moving average. This needs a venv and nothing else. The backtest engine and the live-trading path share the exact same `Strategy` class on purpose, so swapping the data feed — not rewriting your logic — is what happens when you're ready to stop paper trading.

`Python` `Backtesting`

</td>
</tr>
</table>
<!-- AUTO:projects:end -->

<br/>

### Patches upstream

<!-- AUTO:patches:start -->
[**QuantLib**](https://github.com/lballabio/QuantLib/pull/2779) — the C++ library half of quant finance is quietly built on — had a `NaN` hiding in its Gauss-Laguerre quadrature: past order ~200, one of the weights underflows to exactly `0.0`, and `inf × 0` in IEEE 754 is `NaN`, no questions asked. The fix isn't "add an epsilon and pray," it's re-deriving the weight in log-space so the underflow never has anywhere to hide — tested against the real consumer (`AnalyticHestonEngine`) and independently re-derived in NumPy just to be sure I wasn't fooling myself.

[**edgartools**](https://github.com/dgunning/edgartools/pull/1318) — much smaller, and I'll say so: the quickstart claimed Python 3.8 while `pyproject.toml` actually required 3.10, and its own docs quietly recommended a `cash_flow_statement()` alias that's deprecated for removal in v6.0. No math, just paying enough attention to notice the docs were lying to new users — merged.

One of these is a rigor problem, the other is a reading-comprehension problem. Both count.

[**ever-gauzy**](https://github.com/ever-co/ever-gauzy/pull/10225) — a null-prototype object — the exact defensive pattern you'd reach for specifically to dodge prototype-pollution bugs — crashed the utility function written to guard against prototype pollution. `Object.create(null)` has no `.constructor` to read `.name` off of; the fix is one `getPrototypeOf` check. Merged.

[**ever-gauzy**](https://github.com/ever-co/ever-gauzy/pull/10209) — their own security-disclosure badge pointed at a domain that no longer resolves (DNS `SERVFAIL`, not a 404 — the kind of dead link most link-checkers miss). The irony of a broken link on the "here's how to report a security issue" line felt worth fixing quickly. Merged.

[**Riskfolio-Lib**](https://github.com/dcajasn/Riskfolio-Lib/pull/258) — the constructor built its own `returns` setter — type check and all — then routed around it entirely: `self._returns = returns`, no validation, ever. A single `NaN` anywhere in your input data doesn't fail at construction; it fails four stack frames deep inside `scipy.linalg.eigh`, with a message that has nothing to do with your actual data.

[**Riskfolio-Lib**](https://github.com/dcajasn/Riskfolio-Lib/pull/257) — `Axes.plot_date` and `matplotlib.cm.get_cmap` were both quietly removed in Matplotlib 3.11. `requirements.txt` still says `>=3.9.2`. Anyone on a current install can't plot a portfolio without hitting an `AttributeError` first.

[**trade-frame**](https://github.com/rburkholder/trade-frame/pull/9) — 37 images in the README that were never images — `![text](path)` pointing at `.h` files and directories, rendering as broken-icon confetti through the project's own pitch. Two of the targets had also been renamed `.h` → `.hpp` years earlier and nobody had updated the doc since.

[**trade-frame**](https://github.com/rburkholder/trade-frame/pull/8) — asked where the meaning of an IQFeed trade-condition code comes from. Answer: nowhere in the repo, on purpose — IQFeed publishes the code table live over the same socket connection, so hardcoding it would just go stale. Documented the actual mechanism instead of inventing a table that would be wrong by next quarter.

[**matching-engine**](https://github.com/AsthaMishra/matching-engine/pull/2) — an out-of-range price and a genuinely malformed one got rejected with the identical error reason — fine, until you're debugging real order flow at 2am and the log gives you no way to tell which one actually happened.

[**py_lets_be_rational**](https://github.com/vollib/py_lets_be_rational/pull/10) — no `LICENSE` file, which is a small thing right up until it silently blocks `conda-forge` packaging for everyone downstream.

[**cody-special**](https://github.com/vollib/cody-special/pull/2) — `erf_cody` and `normaldistribution` got split into their own files at some point, and the `@numba.njit` decoration that made them fast didn't make the move with them.

[**jev-ultrafast**](https://github.com/browser-use/jev-ultrafast/pull/56) — the agent's own browser target opens on `about:blank`, which is already `readyState == 'complete'` before the real navigation even starts — so the very first poll after `Page.navigate` could read that stale state and hand the policy a page that never loaded. It terminates the run as `BLOCKED` in under a second, which looks exactly like the agent failing when the harness never actually observed anything real.

[**awesome-systematic-trading**](https://github.com/wangzhe3224/awesome-systematic-trading/pull/174) — checked all ~650 links in the list against the GitHub API and actual DNS resolution, not just an HTTP status code (which false-positives constantly on ordinary bot-blocking). Six repos were genuinely gone; no guessed replacements went in for the ones without a verified successor.

[**wangzhe3224/awesome-systematic-trading**](https://github.com/wangzhe3224/awesome-systematic-trading/pull/175) — Add vanna to Pricing (open).
<!-- AUTO:patches:end -->

<br/>

### Stack

<p>
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/C++-00599C?style=flat-square&logo=cplusplus&logoColor=white" alt="C++" />
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black" alt="JavaScript" />
<img src="https://img.shields.io/badge/Qt%20%2F%20PySide6-41CD52?style=flat-square&logo=qt&logoColor=white" alt="Qt / PySide6" />
<img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white" alt="OpenCV" />
<img src="https://img.shields.io/badge/CMake-064F8C?style=flat-square&logo=cmake&logoColor=white" alt="CMake" />
<img src="https://img.shields.io/badge/Excel%20%2F%20VBA-217346?style=flat-square&logo=microsoftexcel&logoColor=white" alt="Excel / VBA" />
<img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white" alt="Git" />
</p>

<br/>

<!-- AUTO:statsalt:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/stats.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/stats-light.svg" />
  <img src="assets/stats.svg" width="100%" alt="Krishna Anubhav GitHub signal: 6 projects shipped, on GitHub since 2022, based in India, open-source patches: QuantLib &amp; 13 more; language mix across own repos is Rust 38%, Python 36%, HTML 12%, JavaScript 7%" />
</picture>
<!-- AUTO:statsalt:end -->

<br/><br/>

<div align="center">

**[GitHub](https://github.com/heykav)** · **[Website](https://krishnaanubhav.com)** · **[X](https://x.com/heykav)**

</div>
