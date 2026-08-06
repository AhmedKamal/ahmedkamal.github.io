/**
 * Defaults for every post in this directory.
 *
 * The permalink is computed in JS rather than templated, because migrated posts
 * are literal HTML with templating switched off (old code samples contain {{ }}).
 */
module.exports = {
	layout: "post.njk",
	eleventyComputed: {
		permalink: (data) => `${data.slug || data.page.fileSlug}/index.html`,
	},
};
