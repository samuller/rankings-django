import type { PageLoad } from './$types';

export const load: PageLoad = ({ params }) => {
	return {
		activity_url: params.activity,
		player_id: params.player_id,
	}
}

export interface PlayerPage{
	activity_url: string;
	player_id: number;
}
