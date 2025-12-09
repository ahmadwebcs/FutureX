# Postman Quick Run Guide — FutureX

This guide shows how to run and verify all API endpoints using Postman (GUI) and how to run the exported collection automatically (Newman / CI). It assumes you used the `postman/` files added to the repo: `FutureX.postman_collection.json` and `FutureX.postman_environment.json`.

Summary of steps
- Ensure the Django app is running locally (or accessible at the `base_url` in the environment).
- Import the collection + environment into Postman.
- Create a Workspace (optional, recommended for teams).
- Run the `Auth / Get Token` request or run the collection (collection will auto-obtain token).
- Execute the requests or run the collection runner.

1) Prerequisites
- Node + npm (for Newman): https://nodejs.org/
- Postman desktop app or web app: https://www.postman.com/
- Python 3.11+ and virtualenv (project already has venv in `futurex/`).
- Newman (optional): `npm install -g newman` or use the `postman/package.json` script.

2) Start the server locally (PowerShell)
Use one of the following options.

- Quick manual start (keeps server in foreground):

```powershell
futurex\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

- Automated local run (starts server and runs the collection via Newman):

```powershell
.\scripts\run_postman.ps1
```

Note: `run_postman.ps1` will start the server in background and run `npm install` + `newman` against the `postman/` collection.

3) Import collection and environment into Postman

- Open Postman → click `Import` → `File` → choose the two files from `postman/`:
  - `FutureX.postman_collection.json`
  - `FutureX.postman_environment.json`
- After import, choose the environment `futurex-local` at the top-right.

4) Create a Team Workspace (optional)
- In Postman, click the workspace switcher (top-left) → `Create Workspace`.
- Choose `Team` type if you want to share with colleagues.
- Give it a name (e.g., `FutureX QA`) and click `Create`.
- From the left collection panel, open the collection `FutureX API` and click `Share` → `Share Collection` → choose your workspace.

5) How authentication works in the collection
- The collection includes a collection-level Pre-request script that automatically obtains an auth token if `{{token}}` is empty using `{{admin_email}}` and `{{admin_password}}` from the environment.
- You can either run `Auth / Get Token` manually once, or run the collection — the pre-request script will fetch the token for you.

6) Running the requests (recommended order)
- Run `Auth / Get Token` (this will populate `{{token}}`).
- Use `Investors / Register` to create a new investor (public endpoint).
- Use `Investors / List` to confirm the investor exists (requires token).
- Upload KYC using `Investors / Upload KYC` (use Body → `form-data`, choose a file for the `file` key).
- Add a `College` through admin (or create via a quick script) and use `Investments / Add Investment` to create an investment.
- Generate a forecast with `Finance / Generate Forecast`.
- Run `Finance / List Payments` to see generated payment schedules.

7) Running the full collection in Postman GUI
- Click the collection → `Run` (right-side) → Runner opens.
- Select Environment: `futurex-local`.
- Click `Run` to start the collection. The collection pre-request script will request a token automatically when needed.

8) Running via Newman (local / CI)
- From the `postman/` folder:

```powershell
cd postman
npm ci
npm run run-postman
```

This executes `newman run FutureX.postman_collection.json -e FutureX.postman_environment.json` (script present in `postman/package.json`).

9) GitHub Actions (CI)
- A workflow file `.github/workflows/postman.yml` is included. On push to `main`, it:
  - Installs Python deps and runs migrations
  - Starts the Django dev server
  - Installs Node and runs the Newman command in `postman/`
- If you want the workflow to use secrets for credentials, update the workflow to accept secrets and set environment variables accordingly (I can add that change).

10) File uploads (KYC) in Postman — tips
- Select the `Investors / Upload KYC` request.
- In Body tab choose `form-data`.
- Add fields: `investor` (text), `name` (text), `file` (type: File) and pick the file from disk.
- Do not manually set `Content-Type` header — Postman will set multipart boundaries automatically.

11) Troubleshooting
- 401 Unauthorized: run `Auth / Get Token` and ensure `{{token}}` is populated. Check admin credentials in environment.
- 500 server error: check Django server console for stacktrace. If running via `run_postman.ps1`, check that the server started successfully.
- Missing `college` id: create a `College` via the admin UI (`/admin/`) or via a short Django script.

12) Optional improvements I can add
- Add request-level Postman `Tests` (assertions) so Newman fails the run on unexpected responses. I can add status/assert checks for each request.
- Use Postman API to programmatically create and share the Workspace (requires your Postman API key). I can generate curl commands you can run with your key.
- Switch CI to use a production-like WSGI server and an ephemeral test DB for isolation.

If you want, I can now:
- Add `Tests` to the Postman collection so the Newman run asserts expected HTTP statuses and JSON keys, or
- Generate the curl commands to create a Postman workspace and upload the collection using the Postman API (you'll supply an API key).
