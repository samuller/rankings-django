import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';

const pkgPath = fileURLToPath(new URL('package.json', import.meta.url));
const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));


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
	// Define these variables carefully as they get replaced directly in the code and can easily break it
	// (e.g. string values need to be quoted in the code else code will look for variables by that name).
	define: {
		// Types for these can be added to app.d.ts to fix Typescript compiler warnings.
		__APP_VERSION__: { name: pkg.version, buildDate: new Date().toISOString() },
    }
});
