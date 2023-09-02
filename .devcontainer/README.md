# Devcontainer

Visual Studio Code's devcontainer setup makes it easy to do development in isolated docker containers.

```
cd rankings-tailwind/
npm i
npm run dev
npm run dev -- --host
# Use this for hot reloading in WSL.
CHOKIDAR_USEPOLLING=1 npm run dev
```
