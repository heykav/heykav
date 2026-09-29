<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg" />
  <img src="assets/banner.svg" width="100%" alt="KAVY — Krishna Anubhav. Engineer, SaaS founder and operator, MBA, now investment banking. Rigorous thinking. Human explanations." />
</picture>

<p>
<a href="https://github.com/heykav/vanna/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/heykav/vanna/tests.yml?branch=main&style=flat-square&label=vanna%20tests&color=00A84A" alt="vanna tests status" /></a>
<a href="https://github.com/heykav/quantdeck/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/heykav/quantdeck/ci.yml?branch=main&style=flat-square&label=quantdeck%20CI&color=00A84A" alt="quantdeck CI status" /></a>
<a href="https://github.com/heykav/microprice-rust/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/heykav/microprice-rust/ci.yml?branch=main&style=flat-square&label=microprice-rust%20CI&color=00A84A" alt="microprice-rust CI status" /></a>
</p>

<p align="center">
<a href="#about">About</a> ·
<a href="#recent-work">Recent work</a> ·
<a href="#selected-work">Selected work</a> ·
<a href="#patches-upstream">Patches</a> ·
<a href="#stack">Stack</a>
</p>

</div>

### About

I started as an engineer, ran a SaaS company, did an MBA, and now work in investment banking. The habit that stayed with me through all of it is not trusting a number until I have rebuilt the model that produced it.

I am based in India. Most evenings go to either an EBITDA bridge or a segfault, and the two have more in common than they look. Each one punishes an assumption you did not know you were making.

The question I keep returning to is whether a tool helps me understand a business or only makes its output look confident. Most finance software is built for the second. I would rather build for the first, even when the "financial model" turns out to be a Python script with opinions.

<br/>

### Recent work

- **microprice-rust**: research code for the micro-price estimator. It does not beat the naive mid-price on its own synthetic data, and the README says so. The real-data evaluation protocol is written before any result exists, and the run is still to come.
- **vanna**: fixed `covered_call`, which was returning only the short call and so behaved like a different strategy. It now holds the stock leg, with attribution and payoff charts to match.
- **fpga-sim-core**: the demo timeline is now labelled as scripted, the waveform output is valid VCD, and the allocation claim is backed by a test.

<br/>

### How the flagship work works

Three small diagrams of the mechanisms behind the projects above. They are drawn from each repo's code and docs as they stand on `main`, and anything schematic is labelled as illustrative.

**Micro-price.** The top of the book is reduced to a queue-imbalance and spread bucket. Transitions that leave the mid-price unchanged form `Q`, the average mid change from each state is `G1`, and `G*` is solved from `G* = G1 + Q G*` by fixed-point iteration. The estimate is the mid plus `G*` for the current state.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/microprice.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/diagrams/microprice-light.svg" />
  <img src="assets/diagrams/microprice.svg" width="100%" alt="Micro-price mechanism: book state bucketed by imbalance and spread, transitions counted into Q and G1, G* solved by fixed-point iteration, micro-price equals mid plus G* of the current state. Grid and offsets are illustrative." />
</picture>

**P&amp;L attribution.** A trade's P&amp;L is a full reprice at the end minus the start, then split into delta, gamma, theta, vega, vanna and volga using Greeks from the start of the period. What those six terms miss is drawn and reported as its own residual bar. Bar heights in the diagram are illustrative.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/vanna-attribution.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/diagrams/vanna-attribution-light.svg" />
  <img src="assets/diagrams/vanna-attribution.svg" width="100%" alt="Schematic waterfall of vanna P&amp;L attribution: delta, gamma, theta, vega, vanna and volga terms, a separate hatched residual bar, and the total. Bar heights are illustrative." />
</picture>

**Tick-to-trade path.** A packet is modelled through block decode, MAC framing, an ITCH 5.0 parser, an order book, an order-flow imbalance pipeline and a PCIe DMA model. This is a cycle-modelled simulation, not hardware, and its timing is simulated: the demo's cycles come from a scripted stimulus timeline.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/fpga-tick-to-trade.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/diagrams/fpga-tick-to-trade-light.svg" />
  <img src="assets/diagrams/fpga-tick-to-trade.svg" width="100%" alt="fpga-sim-core tick-to-trade path, a cycle-modelled simulation and not hardware: PCS block decode, MAC framer, ITCH parser, order book, OFI, DMA. Timing is simulated." />
</picture>

<br/>

### Selected work

<!-- AUTO:projects:start -->
<table width="100%">
<tr>
<td width="33%" valign="top">

**[photoface](https://github.com/heykav/photoface)**

A desktop app that finds faces in a photo library, clusters them, and lets you correct the result. Detection uses YuNet and embeddings use SFace, clustered in a greedy online pass and then re-clustered with average linkage. When you fix a face by hand, that assignment is pinned and the algorithm stops revisiting it.

`Python` `PySide6` `OpenCV`

</td>
<td width="33%" valign="top">

**[pe-financial-calculator](https://github.com/heykav/pe-financial-calculator)**

LBO, DCF and deal-analysis calculators for investment banking and private equity work. I built it to underwrite with, so a sensitivity table that misleads is a bug in this project, and I want to hear about it.

`JavaScript` `HTML/CSS`

</td>
<td width="33%" valign="top">

**[fpga-sim-core](https://github.com/heykav/fpga-sim-core)**

A C++20 simulator of an FPGA-style tick-to-trade path: a block codec with CRC, an ITCH 5.0 parser, a five-level order book, a PCIe DMA model and VCD waveform output. Its timing comes from a scripted stimulus rather than a measured pipeline, and the demo labels it that way. The paths covered by its allocation test perform no heap allocation.

`C++` `CMake`

</td>
</tr>
<tr>
<td width="33%" valign="top">

**[vanna](https://github.com/heykav/vanna)**

Options pricing and P&L attribution in Python. It prices with Black-Scholes and a binomial tree for early exercise, then splits each trade's P&L into delta, gamma, theta, vega, vanna and volga using a Taylor expansion. What the Greeks do not explain is reported as residual instead of being absorbed into a bucket. Backtests run on simulated price paths only.

`Python` `PySide6` `NumPy`

</td>
<td width="33%" valign="top">

**[microprice-rust](https://github.com/heykav/microprice-rust)**

A Rust implementation of the micro-price estimator from Stoikov (2018): a Markov chain over queue-imbalance and spread states that estimates the next expected mid-price. It is research code. On its own synthetic data it does not beat the naive mid-price, and the README shows the numbers. The evaluation protocol for real quote data is written and has not been run yet.

`Rust` `Market Microstructure`

</td>
<td width="33%" valign="top">

**[quantdeck](https://github.com/heykav/quantdeck)**

Event-driven backtesting for Python that needs a virtual environment and nothing else. It began as a fix for LiuAlgoTrader, which required a Postgres server just to backtest a moving average. Backtests and live trading share the same `Strategy` class, so changing the data feed does not mean rewriting the logic.

`Python` `Backtesting`

</td>
</tr>
</table>
<!-- AUTO:projects:end -->

<br/>

### Patches upstream

These are bugs I found by installing each library fresh against current dependencies and checking the numbers by hand, rather than by reading issue trackers. Each one has either been merged or is waiting on review.

<details>
<summary><strong>Patches to quant and finance libraries</strong>, including QuantLib, Qlib, zipline and Riskfolio-Lib. Expand for the list.</summary>

<!-- AUTO:patches:start -->
[**QuantLib**](https://github.com/lballabio/QuantLib/pull/2779) — the C++ quantitative finance library had a `NaN` in its Gauss-Laguerre quadrature. Past order ~200, one of the weights underflows to exactly `0.0`, and `inf × 0` is `NaN` in IEEE 754. The fix re-derives the weight in log-space so the underflow no longer occurs. It is tested against the real consumer (`AnalyticHestonEngine`) and was independently re-derived in NumPy as a check.

[**edgartools**](https://github.com/dgunning/edgartools/pull/1318) — a much smaller fix. The quickstart stated Python 3.8 while `pyproject.toml` required 3.10, and the docs recommended a `cash_flow_statement()` alias that is deprecated for removal in v6.0. No math, only documentation that gave new users incorrect information. Merged.

[**ever-gauzy**](https://github.com/ever-co/ever-gauzy/pull/10225) — a null-prototype object, a pattern used to avoid prototype-pollution bugs, crashed the utility function written to guard against prototype pollution. `Object.create(null)` has no `.constructor` to read `.name` from. The fix is one `getPrototypeOf` check. Merged.

[**ever-gauzy**](https://github.com/ever-co/ever-gauzy/pull/10209) — the project's security-disclosure badge pointed at a domain that no longer resolves (DNS `SERVFAIL`, not a 404, which most link-checkers miss). The broken link was on the line explaining how to report a security issue, so it seemed worth fixing quickly. Merged.

[**Riskfolio-Lib**](https://github.com/dcajasn/Riskfolio-Lib/pull/258) — the constructor defined its own `returns` setter, including a type check, then bypassed it with `self._returns = returns`, so no validation ran. A single `NaN` in the input data does not fail at construction. It fails four stack frames deep inside `scipy.linalg.eigh`, with a message that has nothing to do with the actual data.

[**Riskfolio-Lib**](https://github.com/dcajasn/Riskfolio-Lib/pull/257) — `Axes.plot_date` and `matplotlib.cm.get_cmap` were both removed in Matplotlib 3.11, but `requirements.txt` still says `>=3.9.2`. Anyone on a current install hits an `AttributeError` when plotting a portfolio.

[**trade-frame**](https://github.com/rburkholder/trade-frame/pull/9) — 37 images in the README that were never images: `![text](path)` pointing at `.h` files and directories, which render as broken icons. Two of the targets had also been renamed `.h` → `.hpp` years earlier and the doc was never updated.

[**trade-frame**](https://github.com/rburkholder/trade-frame/pull/8) — asked where the meaning of an IQFeed trade-condition code comes from. Answer: nowhere in the repo, on purpose. IQFeed publishes the code table live over the same socket connection, so a hardcoded copy would go stale. Documented that mechanism instead of adding a table.

[**matching-engine**](https://github.com/AsthaMishra/matching-engine/pull/2) — an out-of-range price and a malformed one were rejected with the identical error reason, so when debugging real order flow the log gave no way to tell which one had happened.

[**py_lets_be_rational**](https://github.com/vollib/py_lets_be_rational/pull/10) — no `LICENSE` file, which blocks `conda-forge` packaging for everyone downstream.

[**cody-special**](https://github.com/vollib/cody-special/pull/2) — `erf_cody` and `normaldistribution` were split into their own files, and the `@numba.njit` decoration that made them fast was not carried over.

[**jev-ultrafast**](https://github.com/browser-use/jev-ultrafast/pull/56) — the agent's browser target opens on `about:blank`, which is already `readyState == 'complete'` before the real navigation starts. The first poll after `Page.navigate` could read that stale state and give the policy a page that never loaded. The run then terminates as `BLOCKED` in under a second, which looks like the agent failing when the harness never observed anything real.

[**awesome-systematic-trading**](https://github.com/wangzhe3224/awesome-systematic-trading/pull/174) — checked all ~650 links in the list against the GitHub API and actual DNS resolution, not just an HTTP status code (which often gives false positives when sites block bots). Six repos were genuinely gone. No replacements were guessed for the ones without a verified successor.

[**microsoft/qlib**](https://github.com/microsoft/qlib/pull/2357) — Microsoft's quant research platform (48k+ stars) threw a `DeprecationWarning` on `import qlib`, because a module-level constant was built with `pd.Timedelta("1day")` instead of the explicit-unit form. Same value, no warning, one-line fix.

[**domokane/FinancePy**](https://github.com/domokane/FinancePy/pull/276) — `np.any(volatility) < 0.0`. `np.any()` on a non-empty array is already a bool before it meets the `< 0.0`, so the negative-volatility guard on FX option greeks could never fire. The sibling `delta()` method got this right (`np.any(v < 0.0)`); this one did not. Found by asking why two methods on the same class disagreed about how to validate the same input.

[**pysystemtrade**](https://github.com/pst-group/pysystemtrade/pull/1663) — two collection-breaking bugs unrelated to each other. One: a wildcard import three layers deep replaced `datetime` the class with `datetime` the module, so `datetime.strptime(...)` failed with an error that looks like a typo but is a namespace collision, hard to spot from the file that crashed. Two: an unescaped `\n` inside a docstring was interpreted as a real newline at parse time, which Python 3.12's doctest parser treated as an indentation problem.

[**ranaroussi/quantstats**](https://github.com/ranaroussi/quantstats/pull/548) — `cagr()` computed `abs(total + 1.0) ** (1/years) - 1`. With `compounded=False`, summed returns can go below −100%, and `abs()` flips negative terminal wealth positive, turning a −240% loss into a reported **+40% CAGR**. Confirmed and fixed directly by the maintainer in v0.0.82: "this release exists because of these reports." (fixed upstream in v0.0.82).

[**cuemacro/findatapy**](https://github.com/cuemacro/findatapy/pull/59) — fix: calculate_log_returns raises TypeError instead of computing log returns (open).

[**jealous/stockstats**](https://github.com/jealous/stockstats/pull/206) — Fix VWMA producing NaN when rolling volume sum is zero (merged).

[**man-group/ArcticDB**](https://github.com/man-group/ArcticDB/pull/3442) — Fix LibraryOptions/EnterpriseLibraryOptions.__eq__ crashing on non-matching types (open).

[**alkaline-ml/pmdarima**](https://github.com/alkaline-ml/pmdarima/pull/623) — Fix: pmdarima.preprocessing.tests package never installed by meson build (open).

[**ranaroussi/yfinance**](https://github.com/ranaroussi/yfinance/pull/2977) — Fix dividends/splits/capital_gains returning None instead of empty Series on price fetch failure (open).

[**dcajasn/Riskfolio-Lib**](https://github.com/dcajasn/Riskfolio-Lib/pull/260) — Fix wrong asset column in All Assets relative constraints (open).

[**cvxgrp/cvxportfolio**](https://github.com/cvxgrp/cvxportfolio/pull/208) — Fix CSV loader to recognize non-nanosecond datetime dtypes (open).

[**convexfi/riskparity.py**](https://github.com/convexfi/riskparity.py/pull/37) — Fix default risk_concentration not being scale-invariant (open).

[**stefan-jansen/zipline-reloaded**](https://github.com/stefan-jansen/zipline-reloaded/pull/334) — BUG: fix TypeError ingesting csvdir bundles with splits/dividends on pandas 3.0 (open).

[**cuemacro/finmarketpy**](https://github.com/cuemacro/finmarketpy/pull/83) — Fix short-only TechIndicator producing +1 signals instead of -1 (open).

[**rsheftel/pandas_market_calendars**](https://github.com/rsheftel/pandas_market_calendars/pull/487) — Fix timezone-dependent failure in test_valid_days_tz_aware (closed).

[**matplotlib/mplfinance**](https://github.com/matplotlib/mplfinance/pull/703) — Fix kwarg_help() crash on current pandas (trailing-comma .loc indexing) (open).

[**stefan-jansen/empyrical-reloaded**](https://github.com/stefan-jansen/empyrical-reloaded/pull/55) — Fix rolling-window empty-index dtype, concat sort warning, scipy test regex (open).

[**stefan-jansen/pyfolio-reloaded**](https://github.com/stefan-jansen/pyfolio-reloaded/pull/69) — Fix deprecated positional Series indexing and dtype upcast warnings (open).

[**bukosabino/ta**](https://github.com/bukosabino/ta/pull/371) — Fix TSI tests: check_less_precise removed from pandas (open).

[**pmorissette/bt**](https://github.com/pmorissette/bt/pull/576) — Fix chained-assignment pattern in positions/outlays/get_transactions (merged).

[**bashtage/arch**](https://github.com/bashtage/arch/pull/865) — TST: actually seed TestForecasting fixtures (merged).

[**wilsonfreitas/awesome-quant**](https://github.com/wilsonfreitas/awesome-quant/pull/707) — Add vanna to Financial Instruments & Pricing (open).

[**NandhaKishorM/laya**](https://github.com/NandhaKishorM/laya/pull/103) — Fix single-option choice question crash in DecisionModel.forward (merged).

[**PyPortfolio/PyPortfolioOpt**](https://github.com/PyPortfolio/PyPortfolioOpt/pull/764) — Add return_raw option to BlackLittermanModel.bl_weights (open).

[**wangzhe3224/awesome-systematic-trading**](https://github.com/wangzhe3224/awesome-systematic-trading/pull/175) — Add vanna to Pricing (open).
<!-- AUTO:patches:end -->

</details>

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
  <img src="assets/stats.svg" width="100%" alt="Krishna Anubhav GitHub signal: 6 projects shipped, on GitHub since 2022, based in India, open-source patches: QuantLib &amp; 37 more; language mix across own repos is Rust 38%, Python 36%, HTML 12%, JavaScript 7%" />
</picture>
<!-- AUTO:statsalt:end -->

<br/><br/>

<div align="center">

**[GitHub](https://github.com/heykav)** · **[Website](https://krishnaanubhav.com)** · **[X](https://x.com/heykav)**

</div>
