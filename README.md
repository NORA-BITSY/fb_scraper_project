Thought for a couple of seconds


```markdown
# Facebook-Group Post Scraper 📄⚡

A turnkey Playwright + Python 3.11 stack that logs into Facebook, scrolls any private Group you own, parses every post (author, text, images, timestamp) and stores it in Postgres with full-text search.  
It ships with a Flask GUI, Celery workers, Redis broker, automated nightly jobs, multi-arch Docker images, and an HCL **bake file** for Buildx power-users.

---

## ✨  Features

| Layer | Tech | Highlights |
|-------|------|------------|
| **Scraper** | Playwright 1.44 | Headless Firefox, cookie persistence, secret/SSH mounts |
| **Parser** | BeautifulSoup + Pydantic | Robust to FB class-name churn, extracts IDs via two regex paths |
| **Storage** | Postgres 15 | `pg_trgm` index → instant full-text search |
| **Jobs** | Celery 5 + Redis | Per-group jobs, retry, beat schedule |
| **GUI** | Flask 3, HTMX, Bootstrap 5 | Add/remove groups, trigger scrapes, browse posts |
| **Images** | Buildx + BuildKit | Multi-arch (`amd64`,`arm64`), remote cache, SBOM/provenance |
| **CI/Deploy** | Docker Compose | Single-command prod bring-up (`docker compose up -d`) |

---

## 🗂 Repository layout (top-level)

```

.
├─ compose.yaml           ← production stack (web, worker, db, redis)
├─ Dockerfile             ← single ARG-driven file for web & worker
├─ .build/bake.hcl        ← multi-arch Buildx definition
├─ facebook\_scraper/      ← Python package
│  ├─ core/               ← Playwright engine + Celery tasks
│  ├─ db/                 ← SQLAlchemy models + init
│  ├─ web/                ← Flask blueprints, templates
│  └─ cli.py              ← helper CLI (`bootstrap`, `scrape`)
└─ tests/                 ← pytest parser sanity test

````

---

## 🚀  Quick Start (with Docker Compose)

```bash
git clone https://github.com/yourorg/facebook_group_scraper.git
cd facebook_group_scraper
cp .env.example .env            # put real FB creds, DB pwd, etc.
docker compose --env-file .env up -d --build
````

* Browse to **[http://localhost:8000](http://localhost:8000)** → log in with `ADMIN_EMAIL` / `ADMIN_PASSWORD` from `.env`.
* “Groups ▶ Add” → paste **Group ID** (`123456789…`) + full URL → Save.
* Click **Scrape** ▶ watch log (`docker compose logs -f worker`) → posts appear under **Posts**.

---

## 🛠 Manual (non-Docker) Install —for dev hacking

```bash
# Ubuntu 22+/Debian 12
sudo apt update && sudo apt install -y python3.11 python3.11-venv redis postgresql
python3.11 -m venv venv && source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
playwright install firefox

# DB bootstrap
createdb fb_scraper
python -m facebook_scraper.db.init   # creates tables + pg_trgm
python -m facebook_scraper.cli bootstrap   # first Playwright login
flask --app facebook_scraper.web run --debug
celery -A facebook_scraper.core.tasks worker -B -l info
```

---

## ⚙️ Config  (`.env` keys of interest)

| Var                             | What it does                                                   |
| ------------------------------- | -------------------------------------------------------------- |
| `FB_EMAIL` / `FB_PASSWORD`      | Credentials of a **dummy** FB profile that can view the Groups |
| `PLAYWRIGHT_STATE`              | JSON cookie file; survives container restarts                  |
| `USER_DATA_DIR`                 | Persistent Firefox profile directory                           |
| `DATABASE_URL`                  | `postgresql+psycopg://user:pwd@host/db`                        |
| `REDIS_URL`                     | Celery broker/result backend                                   |
| `FLASK_SECRET`                  | Session signing key                                            |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | First admin login for GUI                                      |

---

## 🔧 Developer workflow

### 1  Run tests

```bash
pytest -q
```

### 2  Lint & format

```bash
ruff check .
black .
```

### 3  CLI helpers

```bash
# Scrape specific group immediately
python -m facebook_scraper.cli scrape 123456789

# Inspect DB
psql fb_scraper -c "SELECT id, text FROM posts LIMIT 5;"
```

---

## 🏗 Building & Publishing images (Buildx / BuildKit)

```bash
# Create multi-arch builder once
docker buildx create --name proton --driver docker-container --bootstrap --use

# Build & push web + worker with shared cache
docker buildx bake --file .build/bake.hcl --set common.args.GIT_SHA=$(git rev-parse --short HEAD) --push
```

*Cache is stored in `ghcr.io/<user>/cache/fb-scraper`, slashing CI build times.*

---

## 🕵️ Troubleshooting

| Symptom                                            | Fix                                                                                |
| -------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **`TimeoutError: waiting for selector "article"`** | Group layout changed → bump `how_far` or tweak parser CSS selector.                |
| **`PlaywrightError: Browser closed unexpectedly`** | Out of RAM → limit `--max-old-space-size` in container, or use Chromium.           |
| **Nothing scraped, cookie expired**                | `docker compose exec worker python -m facebook_scraper.cli bootstrap` to re-login. |
| **“permission denied /bin/sh” in Docker build**    | Your base image is `scratch`; ensure proper `RUN --mount=type=ssh,id=default`.     |
| **DB disk bloat**                                  | `VACUUM` weekly or enable Postgres partitioning on `published_at`.                 |

---

## 👩‍💻 GUI User Guide

1. **Login** – navigate to `/login`, sign in.
2. **Groups**

   * *Add* – enter ID + full URL (must match exactly).
   * *Scrape* – click lightning-bolt → Celery job queues instantly.
   * Remove row → deletes from YAML and stops scheduled jobs.
3. **Posts**

   * Type in search box, hit ⏎ – full-text search via `ILIKE` + `pg_trgm`.
   * Click column headers to sort (HTMX incremental loads 100 rows).
4. **Logs** – `docker compose logs -f worker` for real-time scrape progress.

---

## 🔒 Security Notes

* Only ever run with a **throwaway FB account**.
* GUI protected by Flask-Login; reverse-proxy behind Nginx + LetsEncrypt for HTTPS.
* Secrets (FB pwd, DB pwd) sourced exclusively from `.env` / Docker secrets.
* SBOM + SLSA provenance (`docker buildx build --provenance=true --sbom=true`) available for supply-chain auditing.

---

## ➕ Contributing

Pull requests are welcome!  Please:

1. Fork → create feature branch → commit with conventional-commit message.
2. Run `pre-commit run --all-files`.
3. Update `tests/` if you touch the parser or models.
4. Describe **why** the change is needed in the PR template.

---

## 📜 License

MIT – see [`LICENSE`](LICENSE).

```

Copy-paste this into `README.md` at the repo root; every command & path matches the project structure provided earlier.  Happy scraping!
```
