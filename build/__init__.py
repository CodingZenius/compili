"""
build package
=============

The build system for VTC pages. Turns `pages/*.vtc` (page files that can
mix ---html---/---css---/---vtc--- sections) into a plain, browser-ready
`dist/` folder of .html/.css/.js files.

This package sits ON TOP of the existing compiler -- it imports and calls
`compiler.Compiler`, but never modifies it. See sections.py for the only
new parsing this adds (splitting a page file into its three sections).

    build.py    build_all() / build_page()  -- compile pages/ -> dist/
    watch.py    watch()                     -- rebuild on file change
    serve.py    serve()                     -- serve dist/ over HTTP
    cli.py      command-line entry point (python -m build.cli build|watch|serve)
"""
