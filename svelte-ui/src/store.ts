import { writable } from 'svelte/store';
import { derived } from '@square/svelte-store';
import { DefaultDict, readJSONAPIList, type PageableAPIStore } from '$lib/api';

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
