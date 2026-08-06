# VTC Build System

A minimal build step that sits **on top of** the existing VTC compiler.
It doesn't change anything in `compiler/` — it just calls
`Compiler.compile_safe()` for each page and stitches the result into a
plain `dist/` folder any browser can open directly.

## The idea

A "page" is one `.vtc` file that can mix three sections: HTML markup, CSS,
and VTC intent statements — the actual language, unchanged.

```vtc
---html---
<button id="signup">Sign up</button>

---css---
#signup { padding: 10px 22px; border-radius: 6px; }

---vtc---
(button_element=signup)
(event_listener=click)
(action=registerUser)
```

The build step splits this into three raw text blobs (`build/sections.py`
— simple marker-based splitting, no real parsing), hands the `---vtc---`
part to the *real* compiler exactly as before, and writes out:

```
dist/home.html   <- your HTML, wrapped in a minimal document,
                    with <link>/<script> tags added automatically
dist/home.css    <- your CSS, copied as-is
dist/home.js     <- the JavaScript the VTC compiler generated
```

Open `dist/home.html` in a browser and it works — no build tooling, no
bundler, nothing else required at runtime.

Old-style `.vtc` files with no `---html---`/`---css---`/`---vtc---`
markers still work unchanged — the whole file is treated as VTC, same as
before. You can drop any existing file from `examples/` into `pages/` and
it'll build fine (just with an empty `<body>`, since it has no HTML
section).

## Folder layout

```
pages/          your source .vtc page files (put home.vtc etc. here)
dist/           build output (generated — safe to delete anytime)
build/
  sections.py   splits a page file into html/css/vtc text
  build.py      build_all() / build_page() — the actual compile step
  watch.py      watch() — rebuilds on file change (no dependencies)
  serve.py      serve() — serves dist/ over HTTP (stdlib only)
  cli.py        command-line entry point
```

## Usage

From the project root:

```bash
# Compile every pages/*.vtc into dist/ once
python3 -m build.cli build

# Rebuild automatically whenever a .vtc file under pages/ changes
python3 -m build.cli watch

# Serve dist/ at http://127.0.0.1:8080 (in a second terminal)
python3 -m build.cli serve
python3 -m build.cli serve 3000     # custom port
```

Typical dev loop: run `watch` in one terminal, `serve` in another, edit
`pages/home.vtc`, refresh the browser.

### From Python

```python
from build.build import build_all, build_page
from pathlib import Path

results = build_all()                          # every pages/*.vtc -> dist/
result = build_page(Path("pages/home.vtc"))     # just one page

if not result.success:
    print(result.error)   # same friendly Intent Error text the compiler produces
```

## Errors

If a page's `---vtc---` section has an error, `build` reports it and skips
that page (other pages still build):

```
[build] home.vtc -> home.css, home.js, home.html
[build] broken.vtc FAILED: line 2: (action)
requires
(event_listener)
before
(action)
```

This is the exact same `IntentError` message the compiler always produced
— the build system doesn't add its own error formatting on top, it just
prints what `compile_safe()` returned.

## What this deliberately does not do

- No bundler, no minifier, no source maps, no dependency graph between
  pages. Each `.vtc` page is independent.
- No new syntax inside the VTC section — `---vtc---` content is handed to
  the unmodified `compiler.Compiler` byte-for-byte.
- `watch()` polls file mtimes every 0.5s instead of using OS file-change
  events, to avoid adding a `watchdog`-style dependency. Fine for local
  dev; not meant for production.
- `serve()` is `http.server.SimpleHTTPRequestHandler` with zero
  configuration — for local preview, not for deploying `dist/` in
  production (just upload `dist/`'s contents to any static host).
