import { writable } from 'svelte/store';
import { asyncReadable } from '@square/svelte-store';

export const page_title = writable("");

export const activities = asyncReadable(
    [],
    async () => {
      const response = await fetch('/api/activities/?active=true&select=url,name');
      if (!response.ok) {
        throw { message: response.statusText, status: response.status }
      }
      const activityList = await response.json();
      return activityList;
    },
    { reloadable: true }
);

