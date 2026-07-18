# System Design Primer — docs site

A [Fumadocs](https://fumadocs.dev) (Next.js) documentation site that presents the
content of the repository's top-level `README.md` as short, focused pages grouped
by topic, instead of one very long page.

## Develop

```bash
cd docs-site
npm install
npm run dev      # http://localhost:3000
```

Other scripts:

```bash
npm run build    # production build
npm run start    # serve the production build
```

## How the content is organised

The pages live in `content/docs/`, one `.mdx` file per topic, grouped into
folders whose order and titles come from `meta.json`:

| Folder | Pages |
| --- | --- |
| _(root)_ | Intro / motivation |
| `getting-started/` | Study guide · How to approach the interview |
| `interview-questions/` | System design Q&A · Object-oriented design Q&A |
| `scalability/` | Start here · Performance vs scalability · Latency vs throughput · Availability vs consistency · Consistency patterns · Availability patterns |
| `networking/` | DNS · CDN · Load balancer · Reverse proxy · Application layer |
| `data/` | Database · Cache · Asynchronism |
| `communication-security/` | Communication · Security |
| `appendix/` | Appendix · Credits & contact |

Images referenced by the docs are copied into `public/images/`.

## Regenerating from the README

The pages are generated from the repository root `README.md` by
`scripts/split-readme.py`. It splits the README by section, rewrites in-page
anchor links into cross-page links, points repository-relative links at GitHub,
and fixes up HTML so it is valid MDX.

```bash
python3 scripts/split-readme.py
```

> **Note:** the script maps README sections to pages using line ranges, so if the
> upstream `README.md` changes substantially, the ranges in the `PAGES` table at
> the top of the script need to be updated to match.
