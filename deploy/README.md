# Tanzawa — Docker Compose deployment

Self-host Tanzawa with one command on any Linux box with Docker.

## What you get

- **Tanzawa app** (uWSGI on Django + GeoDjango/SpatiaLite)
- **Caddy** as reverse proxy — handles static files, media, and automatic HTTPS in production
- **One persistent volume** for everything (SQLite DB + user uploads)
- **No external services** — no Postgres, no Redis, nothing else to babysit

## Quick start (localhost)

```bash
cd deploy
cp .env.example .env
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe())" >> .env
```

Edit `.env` and set:
```
TANZAWA_SUPERUSER_USERNAME=admin
TANZAWA_SUPERUSER_EMAIL=admin@example.com
TANZAWA_SUPERUSER_PASSWORD=<choose-a-strong-password>
```

Then bring up the stack — two flows depending on whether you want to pull a
prebuilt image or build from source:

**Pull prebuilt image (default for operators):**
```bash
docker compose pull
docker compose up -d
```
This fetches `ghcr.io/rmdes/tanzawa:latest` (multi-arch: amd64 + arm64) from
GHCR. No build toolchain or network access to PyPI/npm needed.

**Build from source (for developers / self-hosters who don't trust the registry):**
```bash
docker compose up -d --build
```
First build is ~3–5 min on a modern machine (downloads Debian packages, Python
deps, runs webpack). Subsequent builds hit Docker's layer cache and are <30 s.

The bootstrap script creates the superuser on first boot. Open <http://localhost:8080>
and sign in at `/a/`.

If you prefer to create the superuser manually instead, leave the
`TANZAWA_SUPERUSER_*` vars empty and run:
```bash
docker compose exec app python apps/manage.py createsuperuser
```

## Production deployment with automatic HTTPS

Caddy obtains and renews a Let's Encrypt certificate automatically — there's
no `certbot`, no nginx-config, no manual cert step. Just point DNS and edit
`.env`.

1. **DNS**: create an A record (and optionally AAAA) pointing your domain to
   the server's public IP. Verify with `dig +short yourdomain.com`.
2. **Firewall**: ensure TCP ports **80** and **443** are reachable from the
   public internet. ACME HTTP-01 challenge uses port 80; HTTPS traffic uses
   443. (Port 80 stays open in production for the HTTP→HTTPS redirect and
   for cert renewals.)
3. **Edit `.env`**:
   ```
   CADDY_SITE_ADDRESS=yourdomain.com
   HTTP_PORT=80
   HTTPS_PORT=443

   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DOMAIN_NAME=yourdomain.com
   PROTOCOL=https
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```
4. *(Optional)* For Let's Encrypt renewal notifications, uncomment the
   global block at the top of `Caddyfile` and replace the placeholder with
   your email address.
5. `docker compose pull && docker compose up -d`.

On first request Caddy logs `obtaining certificate` → `certificate obtained
successfully` (visible via `docker compose logs caddy`). The cert + ACME
account key persist in the `caddy-data` named volume — **don't wipe that
volume** unless you want to re-issue (Let's Encrypt rate-limits to 5 certs
per domain per week).

### Multiple domains / www redirect

Caddyfile supports multiple site labels — to also serve `www.yourdomain.com`,
edit `Caddyfile` and replace the single site block with two:

```caddy
yourdomain.com, www.yourdomain.com {
  encode gzip zstd
  ...rest unchanged...
}
```

Caddy obtains a cert covering both names. Or to redirect www → apex:

```caddy
www.yourdomain.com {
  redir https://yourdomain.com{uri} permanent
}
```

## Operating

### Create / manage users
```bash
docker compose exec app python3 apps/manage.py createsuperuser
docker compose exec app python3 apps/manage.py changepassword <username>
```

### Enable / disable plugins
```bash
docker compose exec app python3 apps/manage.py enable_plugin blog.tanzawa.plugins.nowpage
docker compose exec app python3 apps/manage.py disable_plugin blog.tanzawa.plugins.nowpage
```

### Run a Django management command
```bash
docker compose exec app python3 apps/manage.py shell
```

### Tail logs
```bash
docker compose logs -f app
docker compose logs -f caddy
```

### Restart after a config change (`.env` or `Caddyfile`)
```bash
docker compose restart
```

## Backup & restore

All persistent state lives in the `tanzawa-data` named volume (`db.sqlite3` and `media/`).

**Back up** to a tarball on the host:
```bash
docker compose exec app tar czf - -C /data . > tanzawa-backup-$(date +%F).tar.gz
```

**Restore** from a tarball:
```bash
docker compose stop app
docker compose run --rm -T app tar xzf - -C /data < tanzawa-backup.tar.gz
docker compose start app
```

## Updating

Two upgrade flows mirroring the install flows above.

**If you pulled the prebuilt image:**
```bash
docker compose pull
docker compose up -d
```
You'll get whatever was last published to `ghcr.io/rmdes/tanzawa:latest` —
i.e. the latest commit on your fork's `main` (or whatever tag you pin in
`docker-compose.yml`). Pin to a specific version (e.g. `:v1.2.3`) for
predictable upgrades.

**If you build from source:**
```bash
git fetch upstream && git merge upstream/main   # or: git pull origin main
docker compose up -d --build
```

Migrations run automatically on container start (`bootstrap.sh` calls
`manage.py migrate --noinput` before uWSGI). The static-files volume is
also refreshed on every boot, so CSS/JS updates ship correctly without a
manual `down -v`.

## Pinning a specific image version

The default `image: ghcr.io/rmdes/tanzawa:latest` always tracks main. For
predictable upgrades, edit `docker-compose.yml`:

```yaml
image: ghcr.io/rmdes/tanzawa:v1.2.3   # or :sha-<short>
```

Available tags are listed at
<https://github.com/rmdes/tanzawa/pkgs/container/tanzawa>.

## Architecture notes

- **No upstream files modified.** Everything in this directory is additive, so syncing with `jamesvandyne/tanzawa` is a clean merge.
- **Static files** are built into the image at build time (`npm run build` + `collectstatic`) and exposed to Caddy via a named volume. Theme changes require a rebuild.
- **The SECRET_KEY in the Dockerfile is only used at build time** for `collectstatic`. The runtime key comes from `.env`.
- **Caddy listens on `:80` inside the container.** The Caddyfile uses a port-only block for local development; replace with your domain for production HTTPS.

## Troubleshooting

**`docker compose up` fails with `ALLOWED_HOSTS` error**
Set `ALLOWED_HOSTS` in `.env` to include the hostname you're using (e.g. `localhost,127.0.0.1` for local testing).

**Static files are missing / unstyled site**
Rebuild the image: `docker compose up -d --build`. The static volume is populated from the image on first run.

**Healthcheck failing**
Check `docker compose logs app` — usually a missing `SECRET_KEY` or `ALLOWED_HOSTS` misconfiguration.

**SpatiaLite errors on startup**
The Debian-based image ships the right library at the default path, so `SPATIALITE_LIBRARY_PATH` should NOT be set in `.env`. Remove it if present.
