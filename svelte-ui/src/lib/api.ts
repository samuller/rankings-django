import { browser } from '$app/environment';
import { asyncReadable, type Reloadable } from '@square/svelte-store';

// See: https://stackoverflow.com/questions/19127650/defaultdict-equivalent-in-javascript
export class DefaultDict<T> {
	constructor(defaultInit: (key: string) => T) {
		return new Proxy<{ [key: string]: T }>(
			{},
			{
				get: (target: { [key: string]: T }, name: string): T =>
					name in target ? target[name] : (target[name] = defaultInit(name))
			}
		);
	}
}

export interface HeaderAPIStore<T> extends Reloadable<T> {
	headers(): Headers | null;
}

export interface PageableAPIStore<T> extends HeaderAPIStore<T> {
	paged(): boolean;
	pageFromURL(url: string): number;
	prevURL(): string | null;
	nextURL(): string | null;
	firstURL(): string | null;
	lastURL(): string | null;
	linkURL(name: string): string | null;
}

/**
 * Read from API, keeping any headers returned and parsing the response as JSON.
 */
export const readJSONAPI = function <T = any>(
	initial: T,
	url: string,
	// eslint-disable-next-line  @typescript-eslint/no-empty-function
	processHeaders: (_: Headers) => void = () => {}
): HeaderAPIStore<T> {
	if (!browser) return {} as HeaderAPIStore<T>;
	let headers: Headers | null = null;
	const store = asyncReadable<T>(
		initial,
		async () => {
			const response = await fetch(url);
			if (!response.ok) {
				throw { message: response.statusText, status: response.status };
			}
			headers = response.headers;
			processHeaders(headers);
			const jsonData: T = await response.json();
			return jsonData;
		},
		{ reloadable: true }
	) as HeaderAPIStore<T>;
	store.headers = () => headers;
	return store;
};

/**
 * Read from a JSON API that is expected to return a list of items and potentially be pageable.
 */
export const readJSONAPIList = function <T = any>(initial: T, url: string): PageableAPIStore<T> {
	if (!browser) return {} as PageableAPIStore<T>;
	const pagingURLs: { [key: string]: string } = {};
	const store = readJSONAPI<T>(initial, url, (headers) => {
		// Link header is used for Github-style pagination.
		// See: https://docs.github.com/en/rest/guides/traversing-with-pagination
		if (headers != null && headers.has('link')) {
			// We use try-catch since this metadata is optional and we'd rather lose it than crash.
			try {
				const links = headers.get('link')!.split(', ');
				links.forEach((link) => {
					const linkTuple = link.split('; ');
					if (linkTuple.length != 2) {
						console.log("Unexpected 'link' header value:", linkTuple);
						return;
					}
					const linkURL = new URL(linkTuple[0].slice(1, -1));
					// Remove hostname/path etc. to make URL relative in-case backend has internally got wrong hostname.
					const relativeURL = linkURL.pathname + linkURL.search + linkURL.hash;
					const relation = (/rel="(.*)"/g.exec(linkTuple[1]) ?? ['', ''])[1];
					pagingURLs[relation] = relativeURL;
				});
			} catch (err) {
				console.log(err);
			}
		}
	}) as PageableAPIStore<T>;
	// Add pagination functions.
	store.paged = () => Object.keys(pagingURLs).length != 0;
	store.pageFromURL = (url: string) => {
		const _url = new URL(url, window.location.href);
		const offset = parseInt(_url.searchParams.get('offset') ?? '0');
		const limit = parseInt(_url.searchParams.get('limit') ?? '100');
		return 1 + offset / limit;
	};
	store.linkURL = function (name: string) {
		if (name in pagingURLs) {
			return pagingURLs[name];
		}
		return null;
	};
	store.prevURL = () => store.linkURL('prev');
	store.nextURL = () => store.linkURL('next');
	store.firstURL = () => store.linkURL('first');
	store.lastURL = () => store.linkURL('last');
	return store;
};
