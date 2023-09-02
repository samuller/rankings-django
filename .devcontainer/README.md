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
# Use this for hot reloading in WSL.
CHOKIDAR_USEPOLLING=1 npm run dev
```
