import { browser } from "$app/environment";
import { writable } from 'svelte/store';
import { asyncReadable, derived, type Loadable } from '@square/svelte-store';


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


const readJSONAPI = function<T = any>(initial: T, url: string): Loadable<T> {
  if (!browser) return {} as Loadable<T>;
  return asyncReadable<T>(
      initial,
      async () => {
        const response = await fetch(url);
        if (!response.ok) {
          throw { message: response.statusText, status: response.status }
        }
        const jsonData: T = await response.json();
        return jsonData;
      },
      { reloadable: true }
  );
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
