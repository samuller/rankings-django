import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}']
	},
	server: {
		proxy: {
		  "^.*/api/": {
			target: "http://host.docker.internal:8000",
			changeOrigin: true,
			secure: false,
		  },
		},
	},
	// server: { hmr: false }
});
