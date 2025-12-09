# API Test Payloads

This file contains example JSON payloads and example requests for the project's API endpoints (project-level and app-level) so you can quickly test the system.

Prerequisites
- Server running: `python manage.py runserver` (default `http://127.0.0.1:8000/`).
- Use the superuser created earlier (`admin@example.com` / `adminpass`) or any other user.
- For endpoints that require authentication include header: `Authorization: Token <your_token>` (you can get a token at `POST /api/token-auth/`).

Quick: obtain token (form-encoded):

POST /api/token-auth/

Form body (x-www-form-urlencoded):

- `username=admin@example.com`
- `password=adminpass`

Example curl (returns JSON `{ "token": "..." }`):

```bash
curl -X POST http://127.0.0.1:8000/api/token-auth/ \
  -d "username=admin@example.com&password=adminpass"
```

---

SECTION A — Investors (app-level)

1) Register investor (public)

POST /api/investors/register/

JSON body:

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

2) List investors (read-only)

GET /api/investors/investors/

No body required. Use token header to list protected items if needed.

3) Retrieve investor

GET /api/investors/investors/{pk}/

Replace `{pk}` with the investor primary key (UUID or numeric id depending on model). No body.

4) My profile

GET /api/investors/investors/me/

Requires `Authorization: Token <token>` header. No body.

5) Upload KYC document (multipart)

POST /api/investors/kyc-docs/

Example curl (multipart form-data):

```bash
curl -X POST http://127.0.0.1:8000/api/investors/kyc-docs/ \
  -H "Authorization: Token <token>" \
  -F "investor=<INVESTOR_PK>" \
  -F "name=Identity Document" \
  -F "file=@/path/to/id_scan.jpg"
```

If you need a JSON representation for tests that don't send the file, use:

```json
{
  "investor": "<INVESTOR_PK>",
  "name": "Identity Document",
  "file": "<binary multipart upload required>"
}
```

6) Digital signature (store signature data)

POST /api/investors/signatures/

JSON body (signature_data can be base64 SVG/PNG or a string token):

```json
{
  "investor": "<INVESTOR_PK>",
  "document": "<KYCDOC_ID>",
  "signature_data": "data:image/svg+xml;base64,PHN2ZyB..."
}
```

7) Onboarding approvals (create / update)

POST /api/investors/approvals/

JSON body to create an approval record (admin use):

```json
{
  "investor": "<INVESTOR_PK>",
  "approved": false,
  "reviewed_by": "",
  "notes": "Initial review pending"
}
```

PATCH /api/investors/approvals/{pk}/ to approve:

```json
{
  "approved": true,
  "reviewed_by": "Compliance Officer",
  "notes": "KYC verified"
}
```

---

SECTION B — Investments (app-level)

1) Add investment (APIView)

POST /api/investments/add/

JSON body:

```json
{
  "investor": "<INVESTOR_PK>",
  "college": "<COLLEGE_PK>",
  "amount": 1000.00,
  "share_percentage": 0.0
}
```

2) Investment viewset (create/list/retrieve/update/delete)

POST /api/investments/investments/

Body same as above. Example to update share percentage (PATCH):

PATCH /api/investments/investments/{pk}/

```json
{ "share_percentage": 12.5 }
```

3) Portfolio entries (read-only)

GET /api/investments/portfolio/

Optional filter by investor via query param: `?investor=<INVESTOR_PK>`

4) Withdrawals (request withdrawal)

POST /api/investments/withdrawals/

```json
{
  "investor": "<INVESTOR_PK>",
  "amount": 200.00
}
```

Note: The simple withdrawal handler reduces active investments proportionally (see implementation). Use admin review in production.

---

SECTION C — Finance (app-level)

1) List ROI distributions

GET /api/finance/roi/

Optional filter params: `?investor=<INVESTOR_PK>&month=YYYY-MM`

2) Payment schedules (list/create/update)

GET /api/finance/payments/

POST /api/finance/payments/ (create manually):

```json
{
  "investor": "<INVESTOR_PK>",
  "investment": "<INVESTMENT_PK>",
  "amount": 20.00,
  "due_date": "2025-12-15"
}
```

To mark a payment paid (PATCH):

PATCH /api/finance/payments/{pk}/

```json
{ "paid": true, "paid_at": "2025-12-15" }
```

3) Generate a forecast (naive projection endpoint)

POST /api/finance/forecasts/generate/

JSON body:

```json
{
  "investor": "<INVESTOR_PK>",
  "months": 12
}
```

Response contains `forecast_id` and `projection` array of monthly values.

4) Statements (create/list)

POST /api/finance/statements/

```json
{
  "investor": "<INVESTOR_PK>",
  "content": "{\"ledger\": [...]}"
}
```

---

SECTION D — Project-level / Auth / Admin

1) Obtain token (form-encoded)

POST /api/token-auth/

Form body: `username`, `password` (example above).

2) DRF browsable auth (login)

Visit `GET /api/auth/login/` in a browser to sign in using the browsable API.

3) Admin UI

Visit `/admin/` with superuser credentials (`admin@example.com` / `adminpass`). Many models are registered (Investors, KYCDocuments, Investments, PortfolioEntry, Withdrawals, ROIDistribution, PaymentSchedule, Statement, Forecast, etc.). Use admin to inspect created records.

---

Tips for testing with `curl` and a token

- Obtain token:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token-auth/ -d "username=admin@example.com&password=adminpass" | jq -r .token)
```

- Use token in requests:

```bash
curl -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" \
  -d '{"investor":"<INV>","college":"<COL>","amount":1000}' \
  http://127.0.0.1:8000/api/investments/investments/
```

Notes & caveats
- File uploads require multipart/form-data (see KYC example).
- Some operations are implemented as management commands (e.g. `generate_monthly_roi`) — use `python manage.py generate_monthly_roi` or schedule them with Celery/cron.
- Endpoints that use `investor` or `investment` ids accept the primary key used by your models (UUIDs in this project).
- The system includes basic implementations for many features; production-ready behavior (secure e-signatures, payment gateway, background workers, notification delivery, full audit trails) still needs integration.

If you'd like, I can produce a Postman collection or a single JSON file containing all the example bodies ready to import into a testing tool. Tell me which format you prefer.
