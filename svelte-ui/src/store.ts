import { browser } from "$app/environment";
import { writable } from 'svelte/store';
import { asyncReadable, derived, type Reloadable } from '@square/svelte-store';


// See: https://stackoverflow.com/questions/19127650/defaultdict-equivalent-in-javascript
class DefaultDict<T> {
  constructor(defaultInit: (key: string) => T) {
    return new Proxy<{ [key: string]: T }>({}, {
      get: (target: { [key: string]: T }, name: string): T => name in target ?
        target[name] :
        (target[name] = defaultInit(name))
    })
  }
};


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
export const readJSONAPI = function<T = any>(
    initial: T,
    url: string,
    processHeaders: (_: Headers) => void = () => {}
  ): HeaderAPIStore<T> {
  if (!browser) return {} as HeaderAPIStore<T>;
  let headers: Headers | null = null;
  const store = asyncReadable<T>(
      initial,
      async () => {
        const response = await fetch(url);
        if (!response.ok) {
          throw { message: response.statusText, status: response.status }
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
}

/**
 * Read from a JSON API that is expected to return a list of items and potentially be pageable.
 */
export const readJSONAPIList = function<T = any>(initial: T, url: string): PageableAPIStore<T> {
  if (!browser) return {} as PageableAPIStore<T>;
  const pagingURLs: { [key: string]: string } = {};
  const store = readJSONAPI<T>(initial, url, (headers) => {
    // Link header is used for Github-style pagination.
    // See: https://docs.github.com/en/rest/guides/traversing-with-pagination
    if (headers != null && headers.has('link')) {
      // We use try-catch since this metadata is optional and we'd rather lose it than crash.
      try {
        const links = headers.get('link')!.split(", ");
        links.forEach((link) => {
          const linkTuple = link.split("; ");
          if (linkTuple.length != 2) {
            console.log("Unexpected 'link' header value:", linkTuple);
            return;
          }
          const linkURL = new URL(linkTuple[0].slice(1, -1));
          // Remove hostname/path etc. to make URL relative in-case backend has internally got wrong hostname.
          const relativeURL = linkURL.pathname + linkURL.search + linkURL.hash;
          const relation = (/rel="(.*)"/g.exec(linkTuple[1]) ?? ["", ""])[1];
          pagingURLs[relation] = relativeURL;
        });
      } catch(err) {
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
    return 1 + (offset / limit);
  };
  store.linkURL = function(name: string) {
    if (name in pagingURLs) {
      return pagingURLs[name];
    }
    return null;
  };
  store.prevURL = () => store.linkURL("prev");
  store.nextURL = () => store.linkURL("next");
  store.firstURL = () => store.linkURL("first");
  store.lastURL = () => store.linkURL("last");
  return store;
}

export const currentActivityUrl = writable<string | null>(null);
// Title used for breadcrumbs in the navbar.
export const navTitle = writable<string>("");

export interface Activity {
  url: string;
  name: string;
  about?: string;
}
export const activities = readJSONAPIList<Activity[]>([], '/api/activities/?active=true&select=url,name');
export const activitiesAbout = readJSONAPIList<Activity[]>([], '/api/activities/?active=true&select=url,name,about');

export const currentActivity = derived([currentActivityUrl, activities], 
  ([$currentActivityUrl , $activities]) => {
    if ($currentActivityUrl == null) {
      return null;
    }
    return $activities?.find((act: Activity) => act.url == $currentActivityUrl!)
});

export interface Player {
  id: number;
  name: string;
  email: string;
}
export const players = readJSONAPIList<Player[]>([], '/api/players/?ordering=name')

export interface Ranking {
  player: {
    id: number;
    name: string;
  };
  skill: number;
}
export const rankingsAPIStore = function(activity_url: string) {
  return readJSONAPIList<Ranking[]>([], `/api/rankings/?activity=${activity_url}&ordering=-skill&select=player,skill`);
}
// A shared store of rankings for each type of activity. Rankings for a new activity will be correctly initialised when
// accessed for the first time.
export const apiRankings = new DefaultDict(rankingsAPIStore) as { [key: string]: any };

export interface Matches {
  id: number;
  datetime: number;
  submittor: string;
  validated: number;
  games: { id: number, datetime: number, winning_team: number }[];
  teams: { id: number, members: { player: { id: number, name: string, email: string } } [] }[];
}
export const generateListAPIStore = function<T>(url: string) {
  return readJSONAPIList<T[]>([], url);
}
// The type coercion is needed to use correctly typed indexing on the DefaultDict.
const _apiMatches = new DefaultDict(generateListAPIStore<Matches>) as { [key: string]: PageableAPIStore<Matches[]> };
const _apiPendingMatches = new DefaultDict(generateListAPIStore<Matches>) as { [key: string]: PageableAPIStore<Matches[]> };

const addPagingToURL = function(url: string, pageNr: number = 1, limit: number = 100) {
  const pagedUrl = new URL(url, window.location.href);
  const offset = (pageNr - 1) * limit;
  pagedUrl.searchParams.set('offset', offset.toString());
  pagedUrl.searchParams.set('limit', limit.toString());
  return pagedUrl.href;
};

export const apiMatches = function(activity_url: string, pageNr: number = 1, limit: number = 100): PageableAPIStore<Matches[]> {
  const url = `/api/matches/${activity_url}/?ordering=-datetime&validated=1`;
  return _apiMatches[addPagingToURL(url, pageNr, limit)];
};

export const apiPendingMatches = function(activity_url: string, pageNr: number = 1, limit: number = 100): PageableAPIStore<Matches[]> {
  const url = `/api/matches/${activity_url}/?ordering=-datetime&pending=true`;
  return _apiPendingMatches[addPagingToURL(url, pageNr, limit)];
};
