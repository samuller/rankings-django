import type { PageLoad } from './$types';

export const load: PageLoad = ({ params }) => {
	return {
		activity_url: params.activity
	}
}

export interface ActivityPage{
	activity_url: string
}
