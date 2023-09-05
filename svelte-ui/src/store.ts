import { browser } from "$app/environment";
import { writable } from 'svelte/store';
import { asyncReadable, derived, type Loadable } from '@square/svelte-store';


const readJSONAPI = function<T = any>(initial: any, url: string): Loadable<any> {
  if (!browser) return {} as Loadable<any>;
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
export const page_title = writable("");

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
    name: string
  };
  skill: number;
}
export const rankingsAPIStore = function(activity_url: string) {
  return readJSONAPI<Ranking[]>([], `/api/rankings/?activity=${activity_url}&ordering=-skill&select=player,skill`);
}
