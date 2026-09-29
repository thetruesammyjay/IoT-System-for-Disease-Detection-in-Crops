# REST API Reference

Start the development server from the repository root:

```powershell
uv run python main.py --serve
```

The default base URL is `http://127.0.0.1:5000/api/v1`. All timestamps use ISO 8601. The API is intended for local-network use and does not yet provide authentication, so it should not be exposed directly to the public internet.

The browser dashboard is available at `http://127.0.0.1:5000/`. It uses these REST endpoints to refresh monitoring state, classifications, and sensor trends every three seconds. It does not require an internet connection or third-party JavaScript assets.

## System

### `GET /system/health`

Reports database availability and, when configured, continuous-monitoring status. It returns HTTP 200 when the database is available and HTTP 503 when it is unavailable.

### `GET /system/info`

Returns the application version, Python version, operating-system platform, stored-classification count, and whether monitoring is configured.

## Classifications

### `GET /detections`

Returns classification records in descending identifier order.

| Parameter | Default | Constraint | Purpose |
|---|---:|---|---|
| `limit` | 20 | 1 to 100 | Maximum records returned |
| `offset` | 0 | 0 or greater | Records skipped for pagination |
| `disease` | none | Exact display label | Filter by predicted disease |
| `status` | none | `accepted` or `uncertain` | Filter by prediction status |
| `from` | none | ISO 8601 | Earliest capture time |
| `to` | none | ISO 8601 | Latest capture time |

The response contains `items` and a `pagination` object with `limit`, `offset`, `returned`, and `total`.

### `GET /detections/latest`

Returns the latest classification or HTTP 404 when no record exists.

### `GET /detections/<id>`

Returns one classification or HTTP 404 when the identifier does not exist.

## Environmental Sensors

### `GET /sensors/latest`

Returns the most recent temperature and humidity reading or HTTP 404 when no reading exists.

### `GET /sensors/history`

| Parameter | Default | Constraint | Purpose |
|---|---:|---|---|
| `limit` | 100 | 1 to 500 | Maximum readings returned |
| `offset` | 0 | 0 or greater | Readings skipped for pagination |
| `from` | none | ISO 8601 | Earliest recorded time |
| `to` | none | ISO 8601 | Latest recorded time |

## Monitoring

### `GET /monitoring/status`

Returns whether monitoring is running, whether a cycle is active, the configured interval, completed, failed and skipped counters, the last result identifier, timestamps, and the last error.

### `POST /monitoring/start`

Starts the scheduler. It returns HTTP 202 when state changes and HTTP 200 when monitoring is already running.

### `POST /monitoring/stop`

Requests graceful shutdown and waits for an active cycle to finish. It returns HTTP 503 if the configured shutdown timeout is exceeded.

### `POST /inference/trigger`

Runs one capture and classification synchronously. It returns HTTP 201 with the stored result, HTTP 409 when another cycle is active, HTTP 500 when classification fails, or HTTP 503 when monitoring is not configured.

The scheduler and manual endpoint share the same non-blocking inference lock, so two cycles cannot overlap.

### `POST /inference/upload`

Accepts one leaf photograph as `multipart/form-data` using the field name `image`. JPEG, PNG, and WebP images are supported, and the default maximum request size is 10 MB. The server verifies the actual image content, corrects its EXIF orientation, converts it to RGB, stores a normalized local copy, and passes it through the configured classification pipeline.

The endpoint returns HTTP 201 with the stored classification and the original upload filename. It returns HTTP 400 for a missing or invalid image, HTTP 409 when another inference cycle holds the pipeline lock, HTTP 413 when the request exceeds the configured limit, HTTP 500 when classification fails, or HTTP 503 when the classification service is unavailable.

PowerShell example:

```powershell
$form = @{ image = Get-Item "C:\path\to\tomato-leaf.jpg" }
Invoke-RestMethod `
  -Method Post `
  -Form $form `
  http://127.0.0.1:5000/api/v1/inference/upload
```

## Reports

### `GET /reports/export`

Exports up to 10,000 records in ascending identifier order. The endpoint supports the same `disease`, `status`, `from`, and `to` filters as `/detections`.

Use `format=json` for structured JSON or `format=csv` for a spreadsheet-compatible file. Any other format returns HTTP 400.

## Validation Errors

Invalid integers, timestamps, status values, formats, or reversed date ranges return HTTP 400 with a JSON `error` field. Unknown resources return HTTP 404.
