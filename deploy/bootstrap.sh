#!/bin/sh
# Container entrypoint. Runs on every boot. Idempotent.
#
#   1. Applies any pending database migrations.
#   2. If TANZAWA_SUPERUSER_* env vars are set, creates that superuser on first
#      boot only (no-op on subsequent boots). The check is by username — if a
#      user with the same username already exists, this script does NOT update
#      the password or email. Change credentials via the Django admin or
#      `manage.py changepassword`, not by editing .env.
#   3. Hands off to uWSGI via `exec` so signal handling stays correct.

set -eu

cd /app/apps

# Sync collected static into the shared volume Caddy reads from. Docker named
# volumes preserve content across container recreation, so a fresh image's
# new CSS/JS would never reach users without this rsync. --delete removes
# stale files (e.g. an asset deleted upstream).
echo "[bootstrap] refreshing static volume…"
rsync -a --delete /app/staticfiles-image/ /app/staticfiles/

echo "[bootstrap] applying migrations…"
python manage.py migrate --noinput

if [ -n "${TANZAWA_SUPERUSER_USERNAME:-}" ] && [ -n "${TANZAWA_SUPERUSER_PASSWORD:-}" ]; then
    echo "[bootstrap] checking initial superuser…"
    # Env vars are read inside Python (os.environ) — never interpolated into
    # the shell-quoted heredoc — to avoid shell injection if a password
    # contains quotes or backticks.
    python manage.py shell <<'PYEOF'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ["TANZAWA_SUPERUSER_USERNAME"]
email = os.environ.get("TANZAWA_SUPERUSER_EMAIL", "")
password = os.environ["TANZAWA_SUPERUSER_PASSWORD"]

if User.objects.filter(username=username).exists():
    print(f'[bootstrap] superuser "{username}" already exists — skipping.')
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'[bootstrap] created superuser "{username}".')
PYEOF
else
    echo "[bootstrap] no TANZAWA_SUPERUSER_* env vars set — skipping superuser creation."
    echo "[bootstrap] create one manually: docker compose exec app python apps/manage.py createsuperuser"
fi

echo "[bootstrap] starting uWSGI…"
exec uwsgi --ini /app/apps/interfaces/public/uwsgi.ini
