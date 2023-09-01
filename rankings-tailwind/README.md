# Rankings Svelte UI


## Initial creation of project

This Svelte project was created by [`create-svelte`](https://github.com/sveltejs/kit/tree/master/packages/create-svelte). 
```bash
# Create a new project SvelteKit project in "rankings-tailwind" folder.
# Interactive options will appear. Chosen options were:
#  * Skeleton project
#  * With typescript syntax
#  * And the following extras enabled: eslint, prettier, playwright, vitest
npm init svelte@latest rankings-tailwind
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
