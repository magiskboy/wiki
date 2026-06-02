# WWW

Code for [nkthanh.dev](https://nkthanh.dev), migrated from Next.js/MDX to
[pyssg](https://github.com/magiskboy/pyssg).

## Prerequisites

- Python >= 3.13
- Dependencies pinned in `requirements.txt` (pyssg `v0.1.0` + pymdown-extensions):

```bash
$ uv venv && uv pip install -r requirements.txt
```

## Usage

Build the site (output goes to `public/`):

```bash
$ pyssg build
```

Run the live-reload dev server:

```bash
$ pyssg serve
```

## Layout

| Path               | Description                                              |
|--------------------|----------------------------------------------------------|
| `content/`         | Markdown posts, one folder per locale (`vi`, `en`).      |
| `layouts/theme/`   | Layout package: `layout.toml` + Jinja templates.         |
| `static/`          | Stylesheet, images and `robots.txt`, copied to the root. |
| `pyssg.config.py`  | Build config: built-in plugins + site-local plugins.     |
| `plugins/`         | Site-local plugins (see below).                          |

`plugins/` holds the customizations the multilingual blog needs on top of the
built-in pyssg plugins: markdown with KaTeX math (`markdown`), per-locale
paginated post lists (`collections`), per-locale tag/category pages
(`taxonomy`), per-locale RSS (`rss`), `data-theme`-scoped code highlighting
(`highlighting`), legacy URL redirects (`redirects`), and the `static/` copier
(`static_files`).

## Settings

Site options live in `pyssg.config.py` (`Config.site`):

| Option              | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `base_url`          | Absolute site URL, used for SEO tags, sitemap and feeds.                    |
| `socials`           | Social links shown top-right (`title` + `link`).                            |
| `navs`              | Top navigation links (`title` + `link`).                                    |
| `utterances_repo`   | GitHub repo backing the [utterances](https://utteranc.es) comment widget.   |
| `gtag_id`           | Google Analytics measurement id (optional).                                 |

The default locale (`vi`) renders at the site root; other locales keep a
`/<locale>/` prefix.

## License

- Code is licensed under MIT.
- Writings are my own.
