# Devcontainer

Visual Studio Code's devcontainer setup makes it easy to do development in isolated docker containers.

Backend development:
```shell
cd rankings/
poetry shell
poetry install
python manage.py runserver
```

UI development:
```shell
cd svelte-ui/
npm install
# Use polling for hot reloading in WSL, but decrease interval due to extreme CPU usage.
CHOKIDAR_USEPOLLING=1 CHOKIDAR_INTERVAL=1000 npm run dev
```
