WORKDIR /app

# Copy the project venv folder from builder image 
COPY --from=api-builder ${API_VENV} /app/.venv
# Copy local files for application
COPY $SRC_API_DIR $APP_API_DIR
# Installing our code as an (editable) package is currently only needed so that
# we can extract the version at runtime (without duplication) using the
# approach from: https://stackoverflow.com/questions/67085041/how-to-specify-version-in-only-one-place-when-using-pyproject-toml
RUN . /app/.venv/bin/activate && pip install -e $APP_API_DIR && deactivate
# Create path for database
RUN mkdir /db
ENV DJANGO_DB_PATH=/db
# We choose not to define database as a volume during build due to some downsides
# See: https://boxboat.com/2017/01/23/volumes-and-dockerfiles-dont-mix/
# Rather do this at runtime with `docker run` or `docker-compose`.
# VOLUME ["/db"]
# Create a new empty database (migrated to the newest schema)
RUN /app/.venv/bin/python api/manage.py migrate
# Give caddy user rights to write to database
RUN chown -R caddy: /db && chmod +w /db
# Setup static HTML for API
ENV DJANGO_STATIC_ROOT=/app/api/static-root/static
RUN /app/.venv/bin/python api/manage.py collectstatic
# Add command scripts that might useful during runtime
COPY deploy/manage /usr/local/bin

# Copy the statically built UI files
COPY --from=ui-builder ${UI_BUILD} /app/ui

# Default supervisor config: /etc/supervisor/conf.d/supervisord.conf
COPY deploy/supervisord.conf /app
COPY deploy/Caddyfile /app

# https://github.com/opencontainers/image-spec/blob/main/annotations.md#pre-defined-annotation-keys
LABEL org.opencontainers.image.title="Rankings-site"
LABEL org.opencontainers.image.source="https://github.com/samuller/rankings-django"
# LABEL org.opencontainers.image.version="$VERSION"
# LABEL org.opencontainers.image.revision="git rev-parse HEAD"

# Default vars for supervisor
ENV GUNICORN_WORKERS=5
ENV GUNICORN_TIMEOUT=30
# Run application
EXPOSE 8080
# Set default directory when app starts (or container is entered)
WORKDIR /app
# Default command to run if nothing else is specified.
CMD ["supervisord","-c","/app/supervisord.conf"]