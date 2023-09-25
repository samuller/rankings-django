import { type CellDetail } from './components';
import {
    type Matches,
} from '../store';


/**
 * Convert given date to an ISO string, but in local time (instead of UTC).
 *
 * Source: https://stackoverflow.com/questions/12413243/javascript-date-format-like-iso-but-local
 */
export const dateToLocalISO = function (date: Date) {
    const offsetMs = date.getTimezoneOffset() * 60 * 1000;
    const msLocal =  date.getTime() - offsetMs;
    const dateLocal = new Date(msLocal);
    const iso = dateLocal.toISOString();
    const isoLocal = iso.slice(0, 19);
    return isoLocal;
}

/**
 * Convert given date to an ISO string, but in local time (instead of UTC) and with timezone shown.
 *
 * Source: https://stackoverflow.com/questions/12413243/javascript-date-format-like-iso-but-local
 */
export const dateToLocalISOWithTZ = function(date: Date) {
    // Get local timezone.
    const timezoneOffset = -(new Date().getTimezoneOffset());
    const timezoneISO = ((timezoneOffset > 0) ? '+' : '-')
        + String(Math.abs(Math.floor(timezoneOffset / 60))).padStart(2, '0')
        + ':' + String(Math.floor(timezoneOffset % 60)).padStart(2, '0');
    return `${dateToLocalISO(date)}${timezoneISO}`;
}


export const convertMatchesToTable = function(matches: Matches[], pending=false): CellDetail[][] {
    const idCol = (match: Matches) => { return {
        text: match.id
    }};
    const dateCol = (match: Matches) => { return {
        text: new Date(match.datetime*1000).toISOString().replace('T', ' ').split('.')[0]
    }};
    const team1Col = (match: Matches) => { return {
        text: match.teams[0].members.map((member) => member.player.name).join(" & "),
        ...((match.teams[0].id == match.games[0].winning_team) && { tooltip: "Winner!" }),
    }};
    const team2Col = (match: Matches) => { return {
        text: match.teams[1].members.map((member) => member.player.name).join(" & "),
        ...((match.teams[1].id == match.games[0].winning_team) && { tooltip: "Winner!" }),
    }};
    const submittorCol = (match: Matches) => { return {
        text: match.submittor,
    }};
    return matches.map((match: Matches): CellDetail[] => pending ? [
            dateCol(match),
            team1Col(match),
            team2Col(match),
            submittorCol(match),
        ]: [
            idCol(match),
            dateCol(match),
            team1Col(match),
            team2Col(match),
    ]);
};
