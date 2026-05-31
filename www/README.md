# WWW

Code for [nkthanh.dev](https://nkthanh.dev), migrated from Next.js/MDX to
[pyssg](https://github.com/magiskboy/pyssg).

## Prerequisites

- Python >= 3.13
- pyssg with the `template` and `highlight` extras

## Usage

Build the site (output goes to `dist/`):

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
| `layouts/`         | Jinja templates and partials.                            |
| `static/`          | Stylesheet and images, copied verbatim to the site root. |
| `pyssg.config.py`  | Build config: the `i18n_blog` preset plus site options.  |
| `plugins/`         | Site-local plugins: localized dates, KaTeX, categories.  |

## Settings

Site options live in `pyssg.config.py` (`Config.options`):

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
