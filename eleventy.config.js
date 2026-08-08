/**
 * Eleventy config for the /blog section of ahmedkamal.me.
 *
 * Source lives in _blogsrc/, output is written into blog/ and committed, so the
 * live site keeps deploying straight from the branch with no build step in front
 * of it. Everything else in the repo (root index.html, /ar/, /card) is untouched.
 *
 *   npm run dev     preview at http://localhost:8080/blog/
 *   npm run build   regenerate blog/ before committing
 */

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

module.exports = function (eleventyConfig) {
	// Drafts are Ghost-era unfinished work. They travel with the repo, unbuilt.
	eleventyConfig.ignores.add("_blogsrc/drafts/**");
	eleventyConfig.ignores.add("_blogsrc/pages-out/**");

	eleventyConfig.addPassthroughCopy({ "_blogsrc/assets": "assets" });

	// --- Filters ------------------------------------------------------------

	eleventyConfig.addFilter("readableDate", (d) => {
		const dt = new Date(d);
		return `${MONTHS[dt.getUTCMonth()]} ${dt.getUTCDate()}, ${dt.getUTCFullYear()}`;
	});

	eleventyConfig.addFilter("isoDate", (d) => new Date(d).toISOString());

	eleventyConfig.addFilter("year", (d) => new Date(d).getUTCFullYear());

	eleventyConfig.addFilter("readingTime", (content) => {
		const words = String(content).replace(/<[^>]+>/g, " ").trim().split(/\s+/).length;
		return Math.max(1, Math.round(words / 225));
	});

	eleventyConfig.addFilter("escapeXml", (s) =>
		String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;").replace(/'/g, "&apos;"));

	// --- Collections --------------------------------------------------------

	// The curated stream. Newest first, except posts marked `demote: true` in
	// their front matter, which sink to the bottom regardless of date — for
	// pieces that are worth keeping but shouldn't set the tone of the index.
	eleventyConfig.addCollection("writing", (api) =>
		api.getFilteredByGlob("_blogsrc/posts/*.{html,md}")
			.filter((p) => !p.data.archived)
			.sort((a, b) => {
				const demoted = (a.data.demote ? 1 : 0) - (b.data.demote ? 1 : 0);
				return demoted !== 0 ? demoted : b.date - a.date;
			}));

	// "Start here" trio on the index.
	eleventyConfig.addCollection("featured", (api) =>
		api.getFilteredByGlob("_blogsrc/posts/*.{html,md}")
			.filter((p) => p.data.featured)
			.sort((a, b) => b.date - a.date));

	// Older writing, kept online but noindex and out of the index and feed.
	eleventyConfig.addCollection("archived", (api) =>
		api.getFilteredByGlob("_blogsrc/posts/*.{html,md}")
			.filter((p) => p.data.archived)
			.sort((a, b) => b.date - a.date));

	// --- Table of contents --------------------------------------------------

	// Built at compile time from the rendered body: ids are added where Ghost
	// did not supply them, and the list replaces the <!-- TOC --> placeholder.
	eleventyConfig.addTransform("toc", function (content) {
		if (!this.page.outputPath || !this.page.outputPath.endsWith(".html")) {
			return content;
		}
		if (!content.includes("<!-- TOC -->")) return content;

		const used = new Set();
		const slugify = (text) => {
			let base = text.replace(/<[^>]+>/g, "").toLowerCase()
				.replace(/[^\w\s-]/g, "").trim().replace(/\s+/g, "-") || "section";
			let slug = base, n = 2;
			while (used.has(slug)) slug = `${base}-${n++}`;
			used.add(slug);
			return slug;
		};

		const items = [];
		const body = content.replace(
			/<h([23])([^>]*)>([\s\S]*?)<\/h\1>/g,
			(all, level, attrs, text) => {
				let id = (attrs.match(/\bid="([^"]+)"/) || [])[1];
				if (id) {
					used.add(id);
				} else {
					id = slugify(text);
					attrs += ` id="${id}"`;
				}
				items.push({ level: Number(level), id, text: text.replace(/<[^>]+>/g, "").trim() });
				return `<h${level}${attrs}>${text}</h${level}>`;
			});

		if (items.length < 3) return body.replace("<!-- TOC -->", "");

		const list = items.map((i) =>
			`<li class="toc-l${i.level}"><a href="#${i.id}">${i.text}</a></li>`).join("");
		const toc = `<nav class="toc" aria-label="Table of contents">` +
			`<p class="toc-head">Contents</p><ul>${list}</ul></nav>`;
		return body.replace("<!-- TOC -->", toc);
	});

	return {
		dir: {
			input: "_blogsrc",
			output: "blog",
			includes: "_includes",
			data: "_data",
		},
		pathPrefix: "/blog/",
		// Migrated Ghost bodies are literal HTML: never run them through a
		// template engine, or stray {{ }} in old code samples would explode.
		htmlTemplateEngine: false,
		markdownTemplateEngine: "njk",
		templateFormats: ["njk", "md", "html"],
	};
};
