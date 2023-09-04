import { browser } from "$app/environment";
import { writable } from 'svelte/store';
import { asyncReadable, type Loadable } from '@square/svelte-store';


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

export const page_title = writable("");

export interface Activity {
  url: string;
  name: string;
}
export const activities = readJSONAPI<Activity[]>([], '/api/activities/?active=true&select=url,name')
