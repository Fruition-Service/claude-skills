# Attribution

This repository combines work from three sources. They carry different licences.

## 1. The skills — OneWave AI (MIT)

Every skill directory at the repo root is upstream work from
[OneWave-AI/claude-skills](https://github.com/OneWave-AI/claude-skills), licensed MIT
(© 2025 OneWave AI). See [LICENSE](LICENSE). We track them unmodified; this fork adds no skills
and edits none.

## 2. The site tooling — priyanshu14077 (unlicensed)

`scrape_pages.py`, `generate_site.py`, and `templates/` originate from
[priyanshu14077/claude-skills](https://github.com/priyanshu14077/claude-skills).

**That repository publishes no LICENSE file.** Under default copyright, no reuse rights are
granted. We have reproduced this tooling here on the assumption that a repo published openly and
described as a mirror was intended to be shared, but that assumption is not a licence.

**Action outstanding:** ask the author to add a licence, or to confirm reuse in writing. If they
decline, remove `scrape_pages.py`, `generate_site.py`, and `templates/` from this fork.

## 3. The scraped pages and generated site — OneWave AI marketing content

`scraped-pages/` contains 187 scraped copies of skill landing pages from
[onewave-ai.com](https://www.onewave-ai.com/resources/claude-skills). `site/` and `dist/` are
derived from them.

This is OneWave's marketing copy, not covered by the MIT licence on their code. It is reproduced
here for internal browsing.

**Do not enable GitHub Pages on this repository without clearing it with OneWave first.** Serving
`site/` publicly would republish their page content under a Fruition-branded origin, with canonical
tags pointing at our host — which reads as an attempt to outrank the original. That is the one use
of this repo that turns an internal convenience into a problem.

---

*Fork created 2026-08-31. Questions: Edward Zhang.*
