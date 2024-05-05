# Static sites

The Caddy server in our docker container is setup to support being extended with "static sites", i.e. extra URL paths can be added to the website that will redirect to a folder containing content for a static website (a collection of HTML, CSS and JavaScript files).

This `static-sites` folder is an example to show how these static sites can be mounted and configured. It requires creating a folder that contains a `caddy` subdirectory containing files whose config will be imported to the main `Caddyfile` config (see the [import documentation](https://caddyserver.com/docs/caddyfile/directives/import) for more examples). It is then recommended to add other subdirectories for each of your static website data that will be referenced in the config files.

Once setup, the `static-sites` folder should be mounted into the docker container at `/app/static-sites/`, for example:
```shell
docker run -it --rm -p 80:8080 --mount type=bind,src=$PWD/deploy/static-sites,dst=/app/static-sites/ samuller/rankings-site:4.0.1-1.0.0
```
