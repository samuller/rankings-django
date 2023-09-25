// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface Platform {}
	}
}

// Compile-time definitions defined in vite.config.ts.
declare const __APP_VERSION__: { name: string, buildDate: string };

export {};
