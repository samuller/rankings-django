import { browser } from "$app/environment";
import { writable } from 'svelte/store';
import { asyncReadable, derived, type Reloadable } from '@square/svelte-store';


// See: https://stackoverflow.com/questions/19127650/defaultdict-equivalent-in-javascript
class DefaultDict<T> {
  constructor(defaultInit: (key: string) => T) {
    return new Proxy({}, {
      get: (target: { [key: string]: T }, name: string) => name in target ?
        target[name] :
        (target[name] = defaultInit(name))
    })
  }
};

export interface PageableAPIStore<T> extends Reloadable<T> {
  paged(): boolean;
  prevURL(): string | null;
  nextURL(): string | null;
  firstURL(): string | null;
  lastURL(): string | null;
  linkURL(name: string): string | null;
}

export const readJSONAPI = function<T = any>(initial: T, url: string): PageableAPIStore<T> {
  if (!browser) return {} as PageableAPIStore<T>;
  const pagingURLs: { [key: string]: string } = {};
  const store = asyncReadable<T>(
      initial,
      async () => {
        const response = await fetch(url);
        if (!response.ok) {
          throw { message: response.statusText, status: response.status }
        }
        // Link header is used for Github-style pagination.
        // See: https://docs.github.com/en/rest/guides/traversing-with-pagination
        if (response.headers.has('link')) {
          const links = response.headers.get('link')!
            .split(",");
          links.forEach((link) => {
            const linkTuple = link.split("; ");
            if (linkTuple.length != 2) {
              console.log("Unexpected linkTuple value:", linkTuple);
              return;
            }
            const linkURL = new URL(linkTuple[0].slice(1, -1));
            // Remove hostname/path etc. to make URL relative in-case backend has internally got wrong hostname.
            const relativeURL = linkURL.pathname + linkURL.search + linkURL.hash;
            const relation = (/rel="(.*)"/g.exec(linkTuple[1]) ?? ["", ""])[1];
            pagingURLs[relation] = relativeURL;
          });
        }
        const jsonData: T = await response.json();
        return jsonData;
      },
      { reloadable: true }
  ) as PageableAPIStore<T>;
  // Add pagination functions.
  store.paged = () => Object.keys(pagingURLs).length != 0;
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
}
export const activities = readJSONAPI<Activity[]>([], '/api/activities/?active=true&select=url,name')

export const currentActivity = derived([currentActivityUrl, activities], 
  ([$currentActivityUrl , $activities]) => {
    if ($currentActivityUrl == null) {
      return null;
    }
    return $activities?.find((act: Activity) => act.url == $currentActivityUrl!)
});

export interface Player {
  name: string;
  email: string;
}
export const players = readJSONAPI<Player[]>([], '/api/players/?ordering=name')

export interface Ranking {
  player: {
    id: number;
    name: string;
  };
  skill: number;
}
export const rankingsAPIStore = function(activity_url: string) {
  return readJSONAPI<Ranking[]>([], `/api/rankings/?activity=${activity_url}&ordering=-skill&select=player,skill`);
}
// A shared store of rankings for each type of activity. Rankings for a new activity will be correctly initialised when
// accessed for the first time.
export const apiRankings = new DefaultDict(rankingsAPIStore) as { [key: string]: any };
