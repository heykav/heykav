<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg" />
  <img src="assets/banner.svg" width="100%" alt="Krishna Anubhav. Finance, engineering and quantitative systems. Engineer, then SaaS founder and operator, then MBA, now investment banking. I spent years building businesses; now I am learning how investors value them." />
</picture>

<p align="center">
<a href="#about">About</a> ·
<a href="#selected-work">Selected work</a> ·
<a href="#patches-upstream">Patches upstream</a> ·
<a href="#how-i-work">How I work</a> ·
<a href="#contact">Contact</a>
</p>

</div>

### About

I started as an engineer, ran a SaaS company, did an MBA, and now work in investment banking. I am based in India. The habit that stayed with me through all of it is not trusting a number until I have rebuilt the model that produced it.

Most evenings go to either an EBITDA bridge or a segfault, and the two have more in common than they look: each one punishes an assumption you did not know you were making.

The question I keep asking of a tool, my own included, is whether it helps me understand a business or only makes its output look confident. The projects below are my attempts at the first kind. Each README says what the code does not do, and where a result is negative, it says so.

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/surface.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/surface-light.svg" />
  <img src="assets/surface.svg" width="100%" alt="An animated 3D implied-volatility surface swaying in perspective: volatility across moneyness and maturity, with a smile that flattens as maturity grows. Illustrative, generated from a simple parametric smile, not market data." />
</picture>

<br/>

### Selected work

<!-- AUTO:projects:start -->
<p align="center">
<a href="https://github.com/heykav/vanna"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/cards/vanna.svg" /><source media="(prefers-color-scheme: light)" srcset="assets/cards/vanna-light.svg" /><img src="assets/cards/vanna.svg" width="49%" alt="vanna: Options pricing and P&amp;L attribution: Black-Scholes and a binomial tree, with each trade&#x27;s P&amp;L split into Greeks and an honest residual. Backtests run on simulated prices only." /></picture></a>
<a href="https://github.com/heykav/pe-financial-calculator"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/cards/pe-financial-calculator.svg" /><source media="(prefers-color-scheme: light)" srcset="assets/cards/pe-financial-calculator-light.svg" /><img src="assets/cards/pe-financial-calculator.svg" width="49%" alt="pe-financial-calculator: Rivet, a browser-based LBO and DCF calculator for a first-pass look at a deal. Illustrative: gross returns, no taxes, fees or three-statement model." /></picture></a>
<a href="https://github.com/heykav/microprice-rust"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/cards/microprice-rust.svg" /><source media="(prefers-color-scheme: light)" srcset="assets/cards/microprice-rust-light.svg" /><img src="assets/cards/microprice-rust.svg" width="49%" alt="microprice-rust: A Rust micro-price estimator (a Markov chain over queue imbalance). Research code on synthetic data only: it does not beat the naive mid-price, and the README shows the numbers." /></picture></a>
<a href="https://github.com/heykav/quantdeck"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/cards/quantdeck.svg" /><source media="(prefers-color-scheme: light)" srcset="assets/cards/quantdeck-light.svg" /><img src="assets/cards/quantdeck.svg" width="49%" alt="quantdeck: Event-driven backtesting in Python, market orders only, filled at the next bar&#x27;s open plus slippage. Runs offline on CSV files. Backtest only: no live or paper trading." /></picture></a>
<a href="https://github.com/heykav/fpga-sim-core"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/cards/fpga-sim-core.svg" /><source media="(prefers-color-scheme: light)" srcset="assets/cards/fpga-sim-core-light.svg" /><img src="assets/cards/fpga-sim-core.svg" width="49%" alt="fpga-sim-core: A C++20 cycle model of an FPGA-style tick-to-trade path. Latency is counted in simulated cycles on synthetic data, so it is not a hardware or FPGA measurement." /></picture></a>
<a href="https://github.com/heykav/photoface"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/cards/photoface.svg" /><source media="(prefers-color-scheme: light)" srcset="assets/cards/photoface-light.svg" /><img src="assets/cards/photoface.svg" width="49%" alt="photoface: A local desktop app that finds, clusters and lets you correct faces in a photo library. A face you fix by hand is pinned and never moved again." /></picture></a>
</p>
<!-- AUTO:projects:end -->

#### How three of them work

Drawn from each repo's code and docs as they stand on `main`. Anything schematic is labelled as illustrative.

**P&amp;L attribution in vanna.** A trade's P&amp;L is a full reprice at the end minus the start. It is split into delta, gamma, theta, vega, vanna and volga terms using Greeks from the start of the period; with a dividend yield, a dividend term is added to both sides. Whatever those terms miss is its own residual bar. Bar heights are illustrative.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/vanna-attribution.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/diagrams/vanna-attribution-light.svg" />
  <img src="assets/diagrams/vanna-attribution.svg" width="100%" alt="Schematic waterfall of vanna P&amp;L attribution: delta, gamma, theta, vega, vanna and volga terms, a separate hatched residual bar, and the total. Drawn for zero dividend yield. Bar heights are illustrative." />
</picture>

**The micro-price in microprice-rust.** The top of the book is reduced to a queue-imbalance and spread bucket. Transitions that leave the mid-price unchanged form `Q`, the average mid change from each state is `G1`, and `G*` is solved from `G* = G1 + Q G*` by fixed-point iteration. The estimate is the mid plus `G*` for the current state.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/microprice.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/diagrams/microprice-light.svg" />
  <img src="assets/diagrams/microprice.svg" width="100%" alt="Micro-price mechanism in four steps: book state bucketed by imbalance and spread, transitions counted into Q and G1, G* solved by fixed-point iteration, micro-price equals mid plus G* of the current state. Grid and offsets are illustrative." />
</picture>

**The tick-to-trade path in fpga-sim-core.** A packet is modelled through block decode, MAC framing, an ITCH 5.0 parser, an order book, an order-flow imbalance pipeline and a PCIe DMA model. This is a cycle-modelled simulation, not hardware: latency is counted in simulated cycles over a synthetic ITCH stream, using documented stage-latency parameters. The PCS stage is 64b/66b-style framing, not IEEE 802.3 conformant, and the parser handles ITCH add, execute and cancel messages only.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/fpga-tick-to-trade.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/diagrams/fpga-tick-to-trade-light.svg" />
  <img src="assets/diagrams/fpga-tick-to-trade.svg" width="100%" alt="fpga-sim-core tick-to-trade path, a cycle-modelled simulation and not hardware: PCS block decode, MAC framer, ITCH parser, order book, order-flow imbalance, DMA, driven by a discrete cycle counter that writes a VCD trace. Timing is simulated." />
</picture>

<br/>

### Patches upstream

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/merged-wall.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/merged-wall-light.svg" />
  <img src="assets/merged-wall.svg" width="100%" alt="Projects that have merged one of my pull requests, drifting past in two rows." />
</picture>

These are pull requests I have opened on other people's projects. Most are bug, documentation or packaging fixes; a few are enhancements or list additions, two of which add my own vanna to a curated list.

<!-- AUTO:patchsummary:start -->
As of 2026-10-26 there are 48: 24 merged, 17 open and 7 closed without merging.
<!-- AUTO:patchsummary:end -->

Open pull requests are waiting on review and are not shipped work. Counts and statuses are read from GitHub by `scripts/update_profile.py`, not written by hand.

<details>
<summary><strong>The full list, grouped by status</strong>, including QuantLib, Qlib, zipline and Riskfolio-Lib.</summary>

<!-- AUTO:patches:start -->
#### Merged (24)

[**QuantLib**](https://github.com/lballabio/QuantLib/pull/2779) — the C++ quantitative finance library had a `NaN` in its Gauss-Laguerre quadrature. Past order ~200, one of the weights underflows to exactly `0.0`, and `inf × 0` is `NaN` in IEEE 754. The fix re-derives the weight in log-space so the underflow no longer occurs. It is tested against the real consumer (`AnalyticHestonEngine`) and was independently re-derived in NumPy as a check.

[**edgartools**](https://github.com/dgunning/edgartools/pull/1318) — a much smaller fix. The quickstart stated Python 3.8 while `pyproject.toml` required 3.10, and it listed `cash_flow_statement()` twice, which hid that `cashflow_statement()` is the deprecated alias (removal planned for v6.0) and `cash_flow_statement()` is the recommended name. No math, only documentation that gave new users incorrect information.

[**ever-gauzy**](https://github.com/ever-co/ever-gauzy/pull/10225) — a null-prototype object, a pattern used to avoid prototype-pollution bugs, crashed the utility function written to guard against prototype pollution. `Object.create(null)` has no `.constructor` to read `.name` from. The fix is one `getPrototypeOf` check.

[**ever-gauzy**](https://github.com/ever-co/ever-gauzy/pull/10209) — the project's security-disclosure badge pointed at a domain that no longer resolves (DNS `NXDOMAIN`, not a 404, which most link-checkers miss). The broken link was on the line explaining how to report a security issue, so it seemed worth fixing quickly.

[**Riskfolio-Lib**](https://github.com/dcajasn/Riskfolio-Lib/pull/257) — `Axes.plot_date` and `matplotlib.cm.get_cmap` were both removed in Matplotlib 3.11, but `requirements.txt` still says `>=3.9.2`. Anyone on a current install hits an `AttributeError` when plotting a portfolio.

[**trade-frame**](https://github.com/rburkholder/trade-frame/pull/9) — 37 images in the README that were never images: `![text](path)` pointing at `.h` files and directories, which render as broken icons. Two of the targets had also been renamed `.h` → `.hpp` years earlier and the doc was never updated.

[**trade-frame**](https://github.com/rburkholder/trade-frame/pull/8) — asked where the meaning of an IQFeed trade-condition code comes from. Answer: nowhere in the repo, on purpose. IQFeed publishes the code table live over the same socket connection, so a hardcoded copy would go stale. Documented that mechanism instead of adding a table.

[**domokane/FinancePy**](https://github.com/domokane/FinancePy/pull/276) — `np.any(volatility) < 0.0`. `np.any()` on a non-empty array is already a bool before it meets the `< 0.0`, so the negative-volatility guard on FX option greeks could never fire. The sibling `delta()` method got this right (`np.any(v < 0.0)`); this one did not. Found by asking why two methods on the same class disagreed about how to validate the same input.

[**pmorissette/ffn**](https://github.com/pmorissette/ffn/pull/405) — Fix rescale for DataFrames with axis=1.

[**skfolio/skfolio**](https://github.com/skfolio/skfolio/pull/404) — fix(portfolio): slice sample_weight per window in rolling_measure.

[**markedjs/marked**](https://github.com/markedjs/marked/pull/4127) — fix: keep a line starting with # but no space in the list item.

[**starship/starship**](https://github.com/starship/starship/pull/7770) — fix(utils): fix humanize_int rounding across unit boundaries.

[**JerBouma/FinanceToolkit**](https://github.com/JerBouma/FinanceToolkit/pull/257) — fix: currency validation in format_portfolio_dataset only checks max string length.

[**jealous/stockstats**](https://github.com/jealous/stockstats/pull/206) — Fix VWMA producing NaN when rolling volume sum is zero.

[**man-group/ArcticDB**](https://github.com/man-group/ArcticDB/pull/3442) — Fix LibraryOptions/EnterpriseLibraryOptions.__eq__ crashing on non-matching types.

[**ranaroussi/yfinance**](https://github.com/ranaroussi/yfinance/pull/2977) — Fix dividends/splits/capital_gains returning None instead of empty Series on price fetch failure.

[**dcajasn/Riskfolio-Lib**](https://github.com/dcajasn/Riskfolio-Lib/pull/260) — Fix wrong asset column in All Assets relative constraints.

[**stefan-jansen/zipline-reloaded**](https://github.com/stefan-jansen/zipline-reloaded/pull/334) — BUG: Preserve csvdir metadata dtypes when concatenating empty frames.

[**stefan-jansen/pyfolio-reloaded**](https://github.com/stefan-jansen/pyfolio-reloaded/pull/69) — Fix deprecated positional Series indexing and dtype upcast warnings.

[**pmorissette/bt**](https://github.com/pmorissette/bt/pull/576) — Fix chained-assignment pattern in positions/outlays/get_transactions.

[**bashtage/arch**](https://github.com/bashtage/arch/pull/865) — TST: actually seed TestForecasting fixtures.

[**wilsonfreitas/awesome-quant**](https://github.com/wilsonfreitas/awesome-quant/pull/707) — Add vanna to Financial Instruments & Pricing.

[**NandhaKishorM/laya**](https://github.com/NandhaKishorM/laya/pull/103) — Fix single-option choice question crash in DecisionModel.forward.

[**wangzhe3224/awesome-systematic-trading**](https://github.com/wangzhe3224/awesome-systematic-trading/pull/175) — Add vanna to Pricing.

#### Open, awaiting review (17)

[**matching-engine**](https://github.com/AsthaMishra/matching-engine/pull/2) — an out-of-range price and a malformed one were rejected with the identical error reason, so when debugging real order flow the log gave no way to tell which one had happened.

[**py_lets_be_rational**](https://github.com/vollib/py_lets_be_rational/pull/10) — no `LICENSE` file, which blocks `conda-forge` packaging for everyone downstream.

[**cody-special**](https://github.com/vollib/cody-special/pull/2) — `erf_cody` and `normaldistribution` were split into their own files, and the `@numba.njit` decoration that made them fast was not carried over.

[**jev-ultrafast**](https://github.com/browser-use/jev-ultrafast/pull/56) — the agent's browser target opens on `about:blank`, which is already `readyState == 'complete'` before the real navigation starts. The first poll after `Page.navigate` could read that stale state and give the policy a page that never loaded. The run then terminates as `BLOCKED` in under a second, which looks like the agent failing when the harness never observed anything real.

[**awesome-systematic-trading**](https://github.com/wangzhe3224/awesome-systematic-trading/pull/174) — checked all ~650 links in the list against the GitHub API and actual DNS resolution, not just an HTTP status code (which often gives false positives when sites block bots). Seven repos were genuinely gone. No replacements were guessed for the ones without a verified successor.

[**microsoft/qlib**](https://github.com/microsoft/qlib/pull/2357) — Microsoft's quant research platform threw a `DeprecationWarning` on `import qlib`, because a module-level constant was built with `pd.Timedelta("1day")` instead of the explicit-unit form. Same value, no warning, one-line fix.

[**pydata/pandas-datareader**](https://github.com/pydata/pandas-datareader/pull/1034) — Fix EconDB reader crash on pandas 3.

[**pytoolz/toolz**](https://github.com/pytoolz/toolz/pull/649) — Don't fail compose signature when last function has no signature.

[**dateutil/dateutil**](https://github.com/dateutil/dateutil/pull/1598) — Fix rrule slicing with negative start or stop.

[**cuemacro/findatapy**](https://github.com/cuemacro/findatapy/pull/59) — fix: calculate_log_returns raises TypeError instead of computing log returns.

[**alkaline-ml/pmdarima**](https://github.com/alkaline-ml/pmdarima/pull/623) — Fix: pmdarima.preprocessing.tests package never installed by meson build.

[**cvxgrp/cvxportfolio**](https://github.com/cvxgrp/cvxportfolio/pull/208) — Fix CSV loader to recognize non-nanosecond datetime dtypes.

[**convexfi/riskparity.py**](https://github.com/convexfi/riskparity.py/pull/37) — Fix default risk_concentration not being scale-invariant.

[**cuemacro/finmarketpy**](https://github.com/cuemacro/finmarketpy/pull/83) — Fix short-only TechIndicator producing +1 signals instead of -1.

[**matplotlib/mplfinance**](https://github.com/matplotlib/mplfinance/pull/703) — Fix kwarg_help() crash on current pandas (trailing-comma .loc indexing).

[**bukosabino/ta**](https://github.com/bukosabino/ta/pull/371) — Fix TSI tests: check_less_precise removed from pandas.

[**PyPortfolio/PyPortfolioOpt**](https://github.com/PyPortfolio/PyPortfolioOpt/pull/764) — Add return_raw option to BlackLittermanModel.bl_weights.

#### Closed without merging (7)

[**Riskfolio-Lib**](https://github.com/dcajasn/Riskfolio-Lib/pull/258) — the constructor defined its own `returns` setter, including a type check, then bypassed it with `self._returns = returns`, so no validation ran. A single `NaN` in the input data does not fail at construction. It fails four stack frames deep inside `scipy.linalg.eigh`, with a message that has nothing to do with the actual data.

[**pysystemtrade**](https://github.com/pst-group/pysystemtrade/pull/1663) — two collection-breaking bugs unrelated to each other. One: a wildcard import three layers deep replaced `datetime` the class with `datetime` the module, so `datetime.strptime(...)` failed with an error that looks like a typo but is a namespace collision, hard to spot from the file that crashed. Two: an unescaped `\n` inside a docstring was interpreted as a real newline at parse time, which Python 3.12's doctest parser treated as an indentation problem.

[**ranaroussi/quantstats**](https://github.com/ranaroussi/quantstats/pull/548) — `cagr()` computed `abs(total + 1.0) ** (1/years) - 1`. With `compounded=False`, summed returns can go below −100%, and `abs()` flips negative terminal wealth positive, turning a −240% loss into a reported **+40% CAGR**. The maintainer shipped the fix directly in v0.0.82 rather than merging the PR, and wrote that "this release exists because of these reports."

[**mde/ejs**](https://github.com/mde/ejs/pull/821) — Fix ejs --version printing "undefined".

[**tj/commander.js**](https://github.com/tj/commander.js/pull/2643) — Fix crash in Option.attributeName() on doubled/trailing hyphen in option flags.

[**rsheftel/pandas_market_calendars**](https://github.com/rsheftel/pandas_market_calendars/pull/487) — Fix timezone-dependent failure in test_valid_days_tz_aware.

[**stefan-jansen/empyrical-reloaded**](https://github.com/stefan-jansen/empyrical-reloaded/pull/55) — Fix rolling-window empty-index dtype, concat sort warning, scipy test regex.
<!-- AUTO:patches:end -->

</details>

<!-- AUTO:statsalt:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/stats.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/stats-light.svg" />
  <img src="assets/stats.svg" width="100%" alt="Krishna Anubhav on GitHub: 8 original public repos; 48 pull requests opened on other projects, 24 merged, 17 open and 7 closed without merging; on GitHub since 2022; language mix across own repos by bytes: Python 38%, Rust 30%, TypeScript 8%, JavaScript 8%" />
</picture>
<!-- AUTO:statsalt:end -->

<br/>

### How I work

Changes are tested before they are merged, and claims in the READMEs are checked against the code, so a claim that does not hold gets corrected rather than kept.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/workflow.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/workflow-light.svg" />
  <img src="assets/workflow.svg" width="100%" alt="Five steps for every upstream fix: reproduce the bug, make the smallest fix, add a test that fails before and passes after, open a pull request in plain words, and leave the decision to the maintainer." />
</picture>

<br/>

### Contact

**[Website](https://krishnaanubhav.com)** · **[LinkedIn](https://www.linkedin.com/in/krishnaanubhav)** · **[X](https://x.com/heykav)** · **[GitHub](https://github.com/heykav)**
