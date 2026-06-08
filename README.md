# Alba Amicorum

## Running locally

You need two terminals: one for the API, one for the frontend.

### API (FastAPI)

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv run uvicorn api.main:app --reload --port 8000
```

Runs at `http://localhost:8000`.

**Endpoints:**
- `GET /api/albums` — list of all albums with location
- `GET /api/albums/{id}` — single album with contributions

CORS is enabled for `http://localhost:5173` (Vite dev server).

### Frontend (React + Vite)

Requires Node.js.

```bash
cd client
npm install
npm run dev
```

Runs at `http://localhost:5173`.

### Database

PostgreSQL database named `alba`, connecting as the current OS user (no password). Make sure Postgres is running before starting the API.
