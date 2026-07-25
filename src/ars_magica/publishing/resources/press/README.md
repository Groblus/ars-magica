# Ars Magica Press

This directory contains versioned, renderer-neutral publishing resources.

The source contract accepts a compact mapping with `template`, `theme`,
`preset`, `content`, and optional `assets`, or the Phase 1 Pydantic
`ars_magica.models.ArtifactSpec` whose `template_id`, `style_profile_id`,
`print_preset_id`, and `data` fields map directly to those values. `content` holds structured rules
and saga data. `assets` holds artwork metadata and image URLs separately so
generated rules text is never composited into an image and artwork is never
treated as rules content.

`src/ars_magica/publishing` renders these resources. HTML requires Jinja2 and
PDF requires WeasyPrint, both imported only when their renderer is called. On
macOS, install Pango/GObject before attempting PDF output, for example with
`brew install pango gobject-introspection libffi`, then follow WeasyPrint's
documented macOS library-path setup.

Before rendering, every input is filtered for `audience`. `storyguide` values
are retained only for Storyguide output; mappings tagged with `visibility` are
handled recursively, and secret/Storyguide-named fields are omitted from
player and public output. Source references are normalized to:

```json
{"id":"source.example","title":"Core Rules","locator":"500-510","citation":"reviewed/Core.md:500-510","url":null,"authority":"definitive","notes":null}
```

Use a precise bare citation such as `reviewed/Core.md:500-510`, or a
SourceReference-like mapping with `title` plus `locator` or `citation`.

The checked-in templates target printable documents. `render_preview` returns
responsive browser HTML; it intentionally does not claim to rasterize previews.
