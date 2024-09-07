import { writable } from 'svelte/store';
import { asyncDerived } from '@square/svelte-store';
import { DefaultDict, readJSONAPI, readJSONAPIList, type PageableAPIStore } from '$lib/api';

export const currentActivityUrl = writable<string | null>(null);
// Title used for breadcrumbs in the navbar.
export const navTitle = writable<string>('');

/** Stores for activities **/
export interface Activity {
	url: string;
	name: string;
	about?: string;
}
export const activities = readJSONAPIList<Activity[]>(
	[],
	'/api/activities/?active=true&select=url,name'
);
export const activitiesAbout = readJSONAPIList<Activity[]>(
	[],
	'/api/activities/?active=true&select=url,name,about'
);
// AsyncDerive waits until after all of the async parents have finished loading.
export const currentActivity = asyncDerived(
	[currentActivityUrl, activities],
	// We return null to indicate error.
	async ([$currentActivityUrl, $activities]) => {
		if ($currentActivityUrl == null) {
			return null;
		}
		const found = $activities.find((act: Activity) => act.url == $currentActivityUrl!);
		// Return null instead of undefined (which can't be differentiated from initial state).
		if (!found) {
			return null;
		}
		return found;
	}
);

/** Stores for players **/
export interface Player {
	id: number;
	name: string;
	email: string;
}
export const players = readJSONAPIList<Player[]>([], '/api/players/?ordering=name');

/** Stores for player rankings **/
export interface Ranking {
	player: {
		id: number;
		name: string;
	};
	skill: number;
}
export const rankingsAPIStore = function (activity_url: string) {
	return readJSONAPIList<Ranking[]>(
		[],
		`/api/rankings/?activity=${activity_url}&ordering=-skill&select=player,skill`
	);
};
// A shared store of rankings for each type of activity. Rankings for a new activity will be correctly initialised when
// accessed for the first time.
export const apiRankings = new DefaultDict(rankingsAPIStore) as { [key: string]: any };

/** Stores for lists of matches **/
export interface Matches {
	id: number;
	datetime: number;
	submittor: string;
	validated: number;
	games: { id: number; datetime: number; winning_team: number }[];
	teams: { id: number; members: { player: { id: number; name: string; email: string } }[] }[];
}
export const generateListAPIStore = function <T>(url: string) {
	return readJSONAPIList<T[]>([], url);
};
// The type coercion is needed to use correctly typed indexing on the DefaultDict.
const _apiMatches = new DefaultDict(generateListAPIStore<Matches>) as {
	[key: string]: PageableAPIStore<Matches[]>;
};
const _apiPendingMatches = new DefaultDict(generateListAPIStore<Matches>) as {
	[key: string]: PageableAPIStore<Matches[]>;
};

const addPagingToURL = function (url: string, pageNr = 1, limit = 100) {
	const pagedUrl = new URL(url, window.location.href);
	const offset = (pageNr - 1) * limit;
	pagedUrl.searchParams.set('offset', offset.toString());
	pagedUrl.searchParams.set('limit', limit.toString());
	return pagedUrl.href;
};

export const apiMatches = function (
	activity_url: string,
	pageNr = 1,
	limit = 100
): PageableAPIStore<Matches[]> {
	const url = `/api/matches/${activity_url}/?ordering=-datetime&validated=1`;
	return _apiMatches[addPagingToURL(url, pageNr, limit)];
};

export const apiPendingMatches = function (
	activity_url: string,
	pageNr = 1,
	limit = 100
): PageableAPIStore<Matches[]> {
	const url = `/api/matches/${activity_url}/?ordering=-datetime&pending=true`;
	return _apiPendingMatches[addPagingToURL(url, pageNr, limit)];
};

/** Stores for single matches **/
export const generateSingleMatchAPIStore = function <T>(url: string) {
	return readJSONAPI<T | null>(null, url);
};
const _apiSingleMatch = new DefaultDict(generateSingleMatchAPIStore<Matches>) as {
	[key: string]: PageableAPIStore<Matches>;
};

export const apiSingleMatch = function (
	activity_url: string,
	matchId = 1
): PageableAPIStore<Matches> {
	const url = `/api/matches/${activity_url}/${matchId}/`;
	return _apiSingleMatch[url] as unknown as PageableAPIStore<Matches>;
};
