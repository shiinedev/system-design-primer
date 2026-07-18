#!/usr/bin/env python3
"""Split the System Design Primer README.md into topic-based MDX pages for Fumadocs."""
import os, re, shutil

# repo root is two levels up from this script (docs-site/scripts/split-readme.py)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "README.md")
DOCS = os.path.join(ROOT, "docs-site", "content", "docs")
PUBLIC_IMAGES = os.path.join(ROOT, "docs-site", "public", "images")
GH_BASE = "https://github.com/shiinedev/system-design-primer/blob/master/"

# ---------------------------------------------------------------------------
# Page specification: (route_folder, file_slug, title, description, start, end)
# Lines are 1-indexed inclusive, referring to README.md line numbers.
# ---------------------------------------------------------------------------
PAGES = [
    # (folder, slug, title, description, start, end, drop_first, demote)
    ("", "index", "The System Design Primer",
     "Learn how to design large-scale systems and prep for the system design interview.",
     5, 88, True, False),

    ("getting-started", "study-guide", "Study guide",
     "Suggested topics to review based on your interview timeline.",
     182, 217, True, True),
    ("getting-started", "how-to-approach", "How to approach a system design interview question",
     "A step-by-step approach to tackling system design interview questions.",
     218, 286, True, True),

    ("interview-questions", "system-design-questions", "System design interview questions with solutions",
     "Common system design interview questions with sample discussions, code, and diagrams.",
     287, 352, True, True),
    ("interview-questions", "object-oriented-design-questions", "Object-oriented design interview questions with solutions",
     "Common object-oriented design interview questions with sample solutions.",
     353, 371, True, True),

    ("scalability", "start-here", "System design topics: start here",
     "New to system design? Start with these foundational lectures and articles.",
     372, 411, True, True),
    ("scalability", "performance-vs-scalability", "Performance vs scalability",
     "Understanding the difference between performance and scalability.",
     412, 425, True, True),
    ("scalability", "latency-vs-throughput", "Latency vs throughput",
     "Latency vs throughput and why you should aim for maximal throughput with acceptable latency.",
     426, 437, True, True),
    ("scalability", "availability-vs-consistency", "Availability vs consistency",
     "The CAP theorem and the trade-off between consistency and availability.",
     438, 472, True, True),
    ("scalability", "consistency-patterns", "Consistency patterns",
     "Weak, eventual, and strong consistency patterns.",
     473, 498, True, True),
    ("scalability", "availability-patterns", "Availability patterns",
     "Fail-over and replication patterns to support availability.",
     499, 580, True, True),

    ("networking", "domain-name-system", "Domain name system",
     "How DNS translates domain names to IP addresses.",
     581, 618, True, True),
    ("networking", "content-delivery-network", "Content delivery network",
     "How CDNs serve content from locations closer to the user. Push vs pull CDNs.",
     619, 659, True, True),
    ("networking", "load-balancer", "Load balancer",
     "Distributing incoming requests across servers. Layer 4 vs Layer 7, horizontal scaling.",
     660, 729, True, True),
    ("networking", "reverse-proxy", "Reverse proxy (web server)",
     "A reverse proxy centralizes internal services and provides a unified interface.",
     730, 772, True, True),
    ("networking", "application-layer", "Application layer",
     "Separating the web layer from the application layer. Microservices and service discovery.",
     773, 807, True, True),

    ("data", "database", "Database",
     "RDBMS scaling (replication, federation, sharding, denormalization, SQL tuning) and NoSQL.",
     808, 1131, True, True),
    ("data", "cache", "Cache",
     "Caching layers and strategies: client, CDN, web, database, application. Cache update patterns.",
     1132, 1323, True, True),
    ("data", "asynchronism", "Asynchronism",
     "Message queues, task queues, and back pressure to reduce request times.",
     1324, 1369, True, True),

    ("communication-security", "communication", "Communication",
     "TCP, UDP, RPC, and REST.",
     1370, 1559, True, True),
    ("communication-security", "security", "Security",
     "A brief security primer for system design.",
     1560, 1576, True, True),

    ("appendix", "appendix", "Appendix",
     "Powers of two, latency numbers, more interview questions, and real-world architectures.",
     1577, 1799, True, True),
    ("appendix", "credits", "Credits & contact",
     "Under development, credits, contact info, and license.",
     1800, 1839, False, False),
]

FOLDER_META = {
    "getting-started": ("Getting started",
        ["study-guide", "how-to-approach"]),
    "interview-questions": ("Interview questions",
        ["system-design-questions", "object-oriented-design-questions"]),
    "scalability": ("Scalability fundamentals",
        ["start-here", "performance-vs-scalability", "latency-vs-throughput",
         "availability-vs-consistency", "consistency-patterns", "availability-patterns"]),
    "networking": ("Networking & delivery",
        ["domain-name-system", "content-delivery-network", "load-balancer",
         "reverse-proxy", "application-layer"]),
    "data": ("Data",
        ["database", "cache", "asynchronism"]),
    "communication-security": ("Communication & security",
        ["communication", "security"]),
    "appendix": ("Appendix",
        ["appendix", "credits"]),
}

ROOT_META = {
    "title": "System Design Primer",
    "root": True,
    "pages": ["index", "getting-started", "interview-questions", "scalability",
              "networking", "data", "communication-security", "appendix"],
}

# ---------------------------------------------------------------------------
def slugify(text):
    """Replicate github-slugger for our heading set."""
    # strip markdown inline formatting
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower()
    # keep word chars, spaces, hyphens; drop everything else
    text = re.sub(r"[^\w\s-]", "", text)
    text = text.replace(" ", "-")
    return text

def route_for(folder, slug):
    if slug == "index":
        return "/docs"
    if folder:
        return f"/docs/{folder}/{slug}"
    return f"/docs/{slug}"

# ---------------------------------------------------------------------------
# Pass 1: build slug -> (route, is_primary) map across all pages.
# ---------------------------------------------------------------------------
lines = open(SRC, encoding="utf-8").read().split("\n")

def page_raw(start, end):
    return lines[start-1:end]

slug_map = {}   # slug -> (route, is_primary)
for folder, slug, title, desc, start, end, drop_first, demote in PAGES:
    route = route_for(folder, slug)
    body = page_raw(start, end)
    in_fence = False
    first_heading_seen = False
    for ln in body:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            hslug = slugify(m.group(2))
            is_primary = (not first_heading_seen) and drop_first
            first_heading_seen = True
            if hslug not in slug_map:
                slug_map[hslug] = (route, is_primary)

# The "Index of system design topics" section has no dedicated page (the sidebar
# replaces it), so point any links to it at the docs landing page.
slug_map.setdefault("index-of-system-design-topics", ("/docs", True))

# ---------------------------------------------------------------------------
# Text transforms (applied outside fenced code, and outside inline code spans)
# ---------------------------------------------------------------------------
INLINE_CODE = re.compile(r"`[^`]*`")

def rewrite_links_and_html(text, current_route):
    # markdown image/link targets: ](path)
    def repl_md(m):
        label_open, target = m.group(1), m.group(2).strip()
        return label_open + fix_target(target, current_route) + ")"
    text = re.sub(r"(\]\()([^)]+)\)", repl_md, text)
    # HTML src="..." / href="..."
    def repl_attr(m):
        attr, q, target = m.group(1), m.group(2), m.group(3)
        return f'{attr}={q}{fix_target(target, current_route)}{q}'
    text = re.sub(r'(src|href)=("|\')([^"\']+)(\2)', repl_attr, text)
    return text

def fix_target(target, current_route):
    t = target.strip()
    if t.startswith("http://") or t.startswith("https://") or t.startswith("mailto:"):
        return target
    if t.startswith("#"):
        slug = t[1:]
        if slug in slug_map:
            route, is_primary = slug_map[slug]
            if route == current_route:
                return t  # same page -> keep fragment
            if is_primary:
                return route
            return f"{route}#{slug}"
        return target  # unknown anchor: leave as-is
    if t.startswith("images/"):
        return "/" + t
    if t.startswith("./images/"):
        return "/" + t[2:]
    # repo-relative resource -> absolute GitHub link
    if re.match(r"^(solutions|resources|images|CONTRIBUTING|TRANSLATIONS|LICENSE|README)", t):
        return GH_BASE + t
    return target

def self_close_img(text):
    def repl(m):
        tag = m.group(0)
        if tag.rstrip().endswith("/>"):
            return tag
        return tag[:-1].rstrip() + " />"
    return re.sub(r"<img\b[^>]*>", repl, text)

def escape_braces(text):
    return text.replace("{", "&#123;").replace("}", "&#125;")

def quote_attrs(text):
    # add quotes to unquoted HTML attributes like <a href=http://...>
    return re.sub(r'\b(href|src)=(?![\"\'])([^\s>]+)', r'\1="\2"', text)

def transform_segment(seg, current_route):
    seg = quote_attrs(seg)
    seg = rewrite_links_and_html(seg, current_route)
    seg = self_close_img(seg)
    seg = escape_braces(seg)
    return seg

def transform_line(line, current_route):
    # protect inline code spans
    parts = []
    idx = 0
    for m in INLINE_CODE.finditer(line):
        parts.append(transform_segment(line[idx:m.start()], current_route))
        parts.append(m.group(0))  # code span verbatim
        idx = m.end()
    parts.append(transform_segment(line[idx:], current_route))
    return "".join(parts)

# ---------------------------------------------------------------------------
# Pass 2: emit MDX files
# ---------------------------------------------------------------------------
def demote_heading(line):
    m = re.match(r"^(#{2,6})(\s+.*)$", line)
    if m:
        return m.group(1)[1:] + m.group(2)  # remove one '#'
    return line

def build_page(folder, slug, title, desc, start, end, drop_first, demote):
    route = route_for(folder, slug)
    body = page_raw(start, end)
    out = []
    in_fence = False
    dropped = False
    for ln in body:
        fence_toggle = ln.lstrip().startswith("```")
        if fence_toggle:
            in_fence = not in_fence
            out.append(ln)
            continue
        if in_fence:
            out.append(ln)
            continue
        heading = re.match(r"^#{1,6}\s+", ln)
        if heading and not dropped and drop_first:
            dropped = True
            continue  # drop the section's own heading (goes to frontmatter title)
        if heading and demote:
            ln = demote_heading(ln)
        out.append(transform_line(ln, route))
    text = "\n".join(out).strip("\n")
    fm = f"---\ntitle: {yaml_str(title)}\ndescription: {yaml_str(desc)}\n---\n\n"
    return fm + text + "\n"

def yaml_str(s):
    if re.search(r"[:#\[\]{}&*!|>'\"%@`]", s):
        return '"' + s.replace('"', '\\"') + '"'
    return s

# clean docs dir
for f in os.listdir(DOCS):
    p = os.path.join(DOCS, f)
    if os.path.isdir(p):
        shutil.rmtree(p)
    else:
        os.remove(p)

for folder, slug, title, desc, start, end, drop_first, demote in PAGES:
    outdir = os.path.join(DOCS, folder) if folder else DOCS
    os.makedirs(outdir, exist_ok=True)
    content = build_page(folder, slug, title, desc, start, end, drop_first, demote)
    with open(os.path.join(outdir, f"{slug}.mdx"), "w", encoding="utf-8") as fh:
        fh.write(content)

# meta.json files
import json
with open(os.path.join(DOCS, "meta.json"), "w") as fh:
    json.dump(ROOT_META, fh, indent=2)
for folder, (ftitle, pages) in FOLDER_META.items():
    with open(os.path.join(DOCS, folder, "meta.json"), "w") as fh:
        json.dump({"title": ftitle, "pages": pages}, fh, indent=2)

# copy images
os.makedirs(PUBLIC_IMAGES, exist_ok=True)
for img in os.listdir(os.path.join(ROOT, "images")):
    shutil.copy2(os.path.join(ROOT, "images", img), os.path.join(PUBLIC_IMAGES, img))

print("Generated", len(PAGES), "pages.")
print("Slug map entries:", len(slug_map))
