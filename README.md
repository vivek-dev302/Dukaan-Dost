# Dukaan Dost

Dukaan Dost is a voice-enabled dashboard for small retail shops. The current MVP helps a shopkeeper manage an item catalog, a restocking reminder list, customer credit (khata), and an AI assistant. It uses a React frontend, a FastAPI backend, PostgreSQL, and Redis.

## Current features

- Google sign-in; each account gets its own shop data.
- Item categories and catalog. The catalog is a reference and does not track stock quantities.
- Restocking list for products to reorder.
- Customer accounts and credit records. Money is stored in paise.
- Gemini-backed assistant with confirmation for protected changes and an agent action log.
- Voice commands, approval by voice, and spoken responses through Sarvam.

## Run locally

Requirements: Python 3.10+, Node.js, Docker, and FFmpeg (used to convert recorded audio).

1. Create `.env` from `.env.example`. Set `POSTGRES_PASSWORD`, `DATABASE_URL` to use that same password, `GEMINI_API_KEY`, both Google client ID values, and `SARVAM_API_KEY`. For Google sign-in, configure the web OAuth client to allow `http://localhost:5173`.
2. Start PostgreSQL and Redis:

   ```bash
   docker compose up -d
   ```

3. Install backend dependencies and create/update the database schema:

   ```bash
   python -m venv .venv
   # Activate the virtual environment, then:
   pip install -r requirements.txt
   alembic upgrade head
   ```

4. Start the API from the project root:

   ```bash
   uvicorn backend.main:app --reload
   ```

   The API is at `http://localhost:8000`; interactive docs are at `http://localhost:8000/docs`.

5. In another terminal, start the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Open `http://localhost:5173`.

`compose.yaml` starts PostgreSQL and Redis only; the API and frontend currently run as local development processes. Keep `.env` private and never commit real API keys or passwords.
