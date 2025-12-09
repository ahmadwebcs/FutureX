# Postman Workspace Guide — FutureX Investor Management

This document converts the example payloads into a Postman-friendly format, shows how to set up environment variables and pre-request scripts, and explains how to create and share a Postman workspace for team testing.

Base setup (environment)
- Create a new Postman Environment named `futurex-local` (or any name). Add these variables:
  - `base_url` = `http://127.0.0.1:8000`
  - `admin_email` = `admin@example.com`
  - `admin_password` = `adminpass`
  - `token` = `` (leave empty — populated by auth request)

Authentication (Pre-request helper)
- Create a request in Postman named `Get Token` in a folder `Auth`.
- Request: `POST {{base_url}}/api/token-auth/` with `x-www-form-urlencoded` body:
  - `username` = `{{admin_email}}`
  - `password` = `{{admin_password}}`
- Test script (Postman) to save token to environment (add in Tests tab):

```javascript
if (responseCode.code === 200) {
  var json = pm.response.json();
  pm.environment.set('token', json.token);
}
```

Using the token in requests
- In request Headers add:
  - `Authorization: Token {{token}}`
  - `Content-Type: application/json` (or omit for multipart)

Folder structure suggestion
- `Auth` — `Get Token`
- `Investors` — `Register`, `List`, `Retrieve`, `KYC Upload`, `Sign`, `Approvals`
- `Investments` — `Add Investment`, `Investments list`, `Portfolio`, `Withdrawals`
- `Finance` — `ROI`, `Payments`, `Generate Forecast`, `Statements`

Common notes for requests
- Use `{{base_url}}` for all endpoints.
- For protected endpoints, run `Get Token` first, then `Send` other requests.
- For file uploads (KYC), set request type to `POST`, Body -> `form-data`, include key `file` and choose `File` type.

Example Postman requests (copy into new requests)

1) Register Investor (Investors/Register)
- Method: POST
- URL: `{{base_url}}/api/investors/register/`
- Body (raw JSON):

```json
{
  "name": "Test Investor",
  "cnic": "12345-1234567-1",
  "email": "test.investor@example.com",
  "phone": "03001234567",
  "address": "123 Example Street",
  "password": "strongpassword"
}
```

2) Get Investors (Investors/List)
- Method: GET
- URL: `{{base_url}}/api/investors/investors/`
- Headers: `Authorization: Token {{token}}`

3) Upload KYC Document (Investors/KYC Upload)
- Method: POST
- URL: `{{base_url}}/api/investors/kyc-docs/`
- Body: form-data
  - `investor` = `<INVESTOR_PK>` (text)
  - `name` = `ID Document` (text)
  - `file` = choose file (type: File)
- Headers: `Authorization: Token {{token}}` (no Content-Type required — Postman sets it)

4) Add Investment (Investments/Add)
- Method: POST
- URL: `{{base_url}}/api/investments/add/`
- Body (raw JSON):

```json
{
  "investor": "<INVESTOR_PK>",
  "college": "<COLLEGE_PK>",
  "amount": 1000.00,
  "share_percentage": 0.0
}
```
- Headers: `Authorization: Token {{token}}`

5) Generate Forecast (Finance/Forecasts/Generate)
- Method: POST
- URL: `{{base_url}}/api/finance/forecasts/generate/`
- Body (raw JSON):

```json
{
  "investor": "<INVESTOR_PK>",
  "months": 12
}
```
- Headers: `Authorization: Token {{token}}`

6) Generate Monthly ROI (management command) — Postman can't run management commands directly.
- Use this curl from your local machine or run the command in terminal:

```bash
python manage.py generate_monthly_roi
```

7) List Payment Schedules (Finance/Payments)
- Method: GET
- URL: `{{base_url}}/api/finance/payments/`
- Headers: `Authorization: Token {{token}}`

Exporting to a Postman collection
- After you create the requests and folders, use Postman's `Export` feature: Click the collection -> `...` -> `Export` -> choose `Collection v2.1` or `v2.0`.

Creating and sharing a Team Workspace
1. In Postman, create a new Workspace (top-left) -> `Create Workspace` -> choose `Team` and name it `FutureX Testing`.
2. Add team members by email invite.
3. In the workspace, create the collection with requests and environment `futurex-local`.
4. Save the environment and set it as the active environment for the workspace.
5. From the collection, click `Share` -> `Share Collection` -> choose the workspace -> `Update` so team members can access.
6. Optionally, export the collection JSON and commit it to the repo in a `postman/` folder for versioning.

Automated test scripts in Postman
- Add Tests to requests (Tests tab) to assert response codes and JSON fields. Example test for Register request:

```javascript
pm.test("status is 201", function () { pm.response.to.have.status(201); });
pm.test("has investor_id", function () { var json = pm.response.json(); pm.expect(json.investor_id).to.exist; });
```

CI integration
- Export Postman collection and run it in CI using Newman:

```bash
npm install -g newman
newman run FutureX.postman_collection.json -e futurex-local.postman_environment.json
```

Repository integration
- Add `postman/` folder to repo containing exported collection and environment JSON. Team members can import these into Postman quickly.

If you'd like, I can:
- Generate and add a `postman/` folder containing a ready-to-import Collection JSON and Environment JSON.
- Add Newman scripts in `package.json` for CI.

Tell me which of those you'd like and I will create them next.
