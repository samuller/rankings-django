import { type CellDetail } from './components';
import {
    type Matches,
} from '../store';


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
