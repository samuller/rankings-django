import { browser } from "$app/environment";
import { writable } from 'svelte/store';
import { asyncReadable, type Loadable } from '@square/svelte-store';


const readJSONAPI = function(initial: any, url: string): Loadable<any> {
  if (!browser) return {} as Loadable<any>;
  return asyncReadable(
      initial,
      async () => {
        const response = await fetch(url);
        if (!response.ok) {
          throw { message: response.statusText, status: response.status }
        }
        const jsonData = await response.json();
        return jsonData;
      },
      { reloadable: true }
  );
}

export const page_title = writable("");

export const activities = readJSONAPI([], '/api/activities/?active=true&select=url,name')
