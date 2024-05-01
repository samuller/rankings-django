# Rankings Svelte UI

## Versioning

Semantic versioning or [SemVer](https://semver.org/) is used for this frontend. While backend and frontend will always be updated together to be in sync, their versions will differ. This is because they have different users/clients and the differences in their "public APIs" means the concept of "breaking changes" will have different meanings.

For the frontend, breaking changes that increment the MAJOR version will be defined by changes that break common workflows. This means:

- Changes to the URL/routing structure (that aren't just additions), as they will break bookmarks and shared links.
- Large shifts in position of UI element as such location changes affect muscle memory with mouse input and touch devices.
- Changes to keyboard shortcuts which will break workflows based on keyboard input.

## Initial creation of project

This Svelte project was created by [`create-svelte`](https://github.com/sveltejs/kit/tree/master/packages/create-svelte).

```bash
# Create a new project SvelteKit project in "svelte-ui" folder.
# Interactive options will appear. Chosen options were:
#  * Skeleton project
#  * With typescript syntax
#  * And the following extras enabled: eslint, prettier, playwright, vitest
npm init svelte@latest svelte-ui
```

## Additional dependencies

Beyond `svelte-kit` we only added the following additional dependencies:

```bash
# Install Tailwind CSS, see: https://tailwindcss.com/docs/guides/sveltekit
npm i -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install DaisyUI, see: https://daisyui.com/docs/install/
npm i -D daisyui@latest
# Then add to tailwind.config.js
#     module.exports = {
#         //...
#         plugins: [require("daisyui")],
#     }

# Add Square-up's svelte-store
# See reason for "--force": https://github.com/square/svelte-store/issues/67
npm i -D @square/svelte-store --force
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```bash
npm run dljs
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://kit.svelte.dev/docs/adapters) for your target environment.
