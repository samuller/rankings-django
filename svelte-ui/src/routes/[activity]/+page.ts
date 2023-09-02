import type { PageLoad } from './$types';

export const load: PageLoad = ({ params }) => {
	return {
		url: params.activity
	}
}

export interface ActivityPage{
	url: string
}
