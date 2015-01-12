Minimal-Blog 
============

A responsive blog theme for Jekyll. You can see it in use [here](http://nickw.it).

## Features & Preferences

Things to be aware of, feel free to disable:

 * Syntax highlighting is *client-side*, using the [jekyll prism plugin](https://github.com/gmurphey/jekyll-prism-plugin). If you want to make sure you have enough languages covered in the stylesheet (`css/prism.custom.css`), make your own at [the Prism site](http://prismjs.com/download.html).
 * [FitVids.js](http://fitvidsjs.com), and consequently Zepto.js are included so embedded videos will fit within a post. Appreciate this may be unwanted bloat. To remove, see bottom of `_layouts/default.html`.
 * Tags listed in the frontmatter of a post are listed on the archive/index page.
 * Be sure to check everything in `_config.yml`.

## Rebuilding Styles

The `.less` source file is in `css/_less`. Build using [LESS](http://lesscss.org) like so:

    lessc css/_less/styles.less css/styles.css

## Todo

 * Build script - don't like the unminifed CSS and separate JS files
