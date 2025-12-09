# Postman Collection for FutureX

Files:
- `FutureX.postman_collection.json` — Postman collection with requests for Auth, Investors, Investments, Finance.
- `FutureX.postman_environment.json` — Environment variables for local testing (`base_url`, `admin_email`, `admin_password`, `token`).

How to import:
1. In Postman, click `Import` -> `File` -> choose `FutureX.postman_collection.json` and `FutureX.postman_environment.json`.
2. Select environment `futurex-local`.
3. Run `Auth / Get Token` to populate `{{token}}`.
- Run in Postman / run collection directly
- The collection includes a collection-level Pre-request script that will automatically obtain a token using the `admin_email`/`admin_password` environment variables if `{{token}}` is empty.
- To run the collection in Postman GUI: Click the collection -> `Run` -> choose environment `futurex-local` -> `Run`.

Run in CI:
- Install Newman: `npm install -g newman`.
- Run: `newman run FutureX.postman_collection.json -e FutureX.postman_environment.json`
