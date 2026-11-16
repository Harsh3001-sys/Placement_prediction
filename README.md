# CareerLens — Student Intelligence Platform

> Unified academic ML platform with **two independent prediction systems**:  
> 1) **Student Placement Prediction** (existing)  
> 2) **Student PPO Prediction** (independent)

Built with **Flask + scikit-learn** on the backend and **React 19 + TypeScript + Vite + Tailwind CSS** on the frontend.  
Prepared for deployment with **Vercel (frontend)** and **Render (backend, Gunicorn)**.

---

## 1. Project Overview

CareerLens provides decision-support predictions through separate ML pipelines exposed in the same application:

- **Placement Predictor**: estimates likelihood of student placement using 13 academic/experience/technical features.
- **PPO Predictor**: estimates likelihood of receiving a Pre-Placement Offer (PPO) using 8 internship performance indicators.

Both systems are integrated into one UI and one Flask app, but remain **fully isolated** (separate artifacts, schemas, services, validation, endpoints, and frontend flows).

### Placement Model (Existing, Preserved)
- Algorithm: Logistic Regression pipeline (with StandardScaler)
- Features: 13
- Canonical test metrics (existing project configuration): Accuracy 80.85%, Precision 77.01%, Recall 77.47%, F1 77.24%, ROC-AUC 0.8840
- Existing placement APIs/contracts preserved: `/api/health`, `/api/predict`, `/api/model/info`

### PPO Model (Independent, Preserved Artifacts)
- Algorithm: Logistic Regression (serialized scikit-learn pipeline)
- Dataset: Synthetic PPO Dataset V3
- Dataset records: 8,017
- Input features: 8 (exact order read from `ppo_features.json`)
- Classification threshold: 0.50
- Synthetic test metrics: Accuracy 82.29%, Precision 86.44%, Recall 89.16%, F1 87.78%, ROC-AUC 0.8852, Balanced Accuracy 77.19%

> **PPO Disclosure:** The PPO model was trained and evaluated on synthetic PPO data. Metrics and predictions are for academic demonstration and must not be presented as verified real-world company PPO performance.

---

## 2. Project Structure (Deployment-Oriented)

```text
CareerLens/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── predictor.py
│   │   ├── ppo_predictor.py
│   │   ├── routes.py
│   │   ├── ppo_routes.py
│   │   ├── schemas.py
│   │   └── ppo_schemas.py
│   ├── artifacts/                    # legacy copies preserved
│   ├── models/
│   │   ├── placement/
│   │   │   ├── placement_model.joblib
│   │   │   └── features.json
│   │   └── ppo/
│   │       ├── ppo_prediction_model.joblib
│   │       ├── ppo_features.json
│   │       └── metadata.json
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   ├── public/
│   ├── .env.example
│   ├── package.json
│   └── vite.config.ts
├── datasets/
│   ├── placementdata.csv
│   ├── placementdata_updated (1).csv
│   ├── ppo_dataset_v3.csv
│   └── original_provided/
│       ├── placement_model.joblib
│       ├── ppo_prediction_model (1).joblib
│       └── ppo_features (1).json
├── .gitignore
└── README.md
```

### Runtime artifact loading
- Placement runtime artifacts: `backend/models/placement/placement_model.joblib`, `backend/models/placement/features.json`
- PPO runtime artifacts: `backend/models/ppo/ppo_prediction_model.joblib`, `backend/models/ppo/ppo_features.json`, `backend/models/ppo/metadata.json`
- Backend model-loading paths are resolved **relative to backend source files** using `pathlib` (CWD-independent) with legacy fallbacks for safety.
- Models are loaded **once during app initialization** (not per request).

### Datasets (not required at runtime for predictions)
- Root CSV/source files were moved into `datasets/` for organization and preserved.
- Original provided root copies (including `(1)` filenames) were preserved under `datasets/original_provided/`.
- No datasets were deleted and no model artifacts were retrained/regenerated.

---

## 3. Architecture & Isolation Guarantees

### Backend (Flask)
- Placement modules (preserved): `backend/app/routes.py`, `backend/app/predictor.py`, `backend/app/schemas.py`
- PPO modules (independent): `backend/app/ppo_routes.py`, `backend/app/ppo_predictor.py`, `backend/app/ppo_schemas.py`
- Both blueprints registered in `backend/app/__init__.py`; predictors initialized independently on startup.

### Isolation
- **Separate artifacts/config:** placement and PPO load different model/feature/metadata files.
- **Separate feature handling:** PPO reads feature order from `ppo_features.json`; placement keeps its existing 13-feature schema/order.
- **Separate services/validation/endpoints:** no shared prediction logic; `/api/*` and `/api/ppo/*` are independent.
- **Independent initialization:** one model failing to load does not prevent the other from initializing/serving (where supported by current architecture).

---

## 4. API Documentation

### Placement APIs (existing, preserved)
- `GET /api/health` — placement model/service health
- `POST /api/predict` — placement prediction (13 existing features)
- `GET /api/model/info` — placement model transparency/metrics/coefficients/ROC/confusion matrix

### PPO APIs (independent)
- `GET /api/ppo/health` — PPO model/service health
- `POST /api/ppo/predict` — PPO prediction (8 required features, exact order from `ppo_features.json`, threshold `0.50`)
- `GET /api/ppo/info` — PPO model metadata/metrics/coefficients/feature definitions

**PPO required feature order:**
1. `Technical_Evaluation`
2. `Task_Completion_Rate`
3. `Attendance_Rate`
4. `Communication_Score`
5. `Manager_Rating`
6. `Code_Quality_Score`
7. `Teamwork_Score`
8. `Deadline_Adherence`

**PPO validation/error behavior:** missing fields, non-numeric/boolean/NaN/infinite values, and out-of-range values return `400`; unavailable model returns `503`; unexpected inference errors return safe JSON `500` (no stack traces exposed).

---

## 5. Local Development

### Prerequisites
- Python 3.10+ (development/tested in this environment with Python 3.14)
- Node.js 18+ and npm

### Backend
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```
- Runs on `http://127.0.0.1:5000` by default (`PORT` env var supported).
- CORS origins are configured via `ALLOWED_ORIGINS` (comma-separated). Defaults support localhost dev.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
- Vite dev server (typically `http://localhost:5173`) proxies `/api` to `http://127.0.0.1:5000` (see `frontend/vite.config.ts`).
- Frontend API calls use `VITE_API_BASE_URL` (defaults to `/api`).

---

## 6. Deployment Preparation (Vercel + Render)

### Backend (Render)
- **Root directory:** `backend`
- **Build command:** `pip install -r requirements.txt`
- **Start command (Gunicorn):** `gunicorn run:app --bind 0.0.0.0:$PORT`
  - Flask app instance is exposed in `backend/run.py` as `app = create_app()`.
- **Python version:** `3.11.11` (configured via `backend/.python-version` for Render) to match serialized model compatibility.
- **Python deps:** `backend/requirements.txt` pins `scikit-learn==1.6.1` (matching serialized Joblib models) with compatible `numpy/scipy/pandas/joblib` constraints, plus Flask, Flask-CORS, gunicorn, and pytest.
- **Runtime artifacts:** `backend/models/placement/*` and `backend/models/ppo/*` must be present in the deployed backend (they are tracked in git).

### Frontend (Vercel)
- **Root directory:** `frontend`
- **Build command:** `npm run build`
- **Output directory:** `dist` (Vite default)
- **Install command:** `npm install` (default)
- API base URL is read from `VITE_API_BASE_URL` in `frontend/src/services/api.ts` (no hardcoded Render URL).

### Environment Variables

**Backend (Render):**
- `ALLOWED_ORIGINS` = your deployed Vercel frontend origin(s), comma-separated, no trailing slashes (e.g. `https://your-app.vercel.app`)
- `SECRET_KEY` = production secret value
- `PORT` = provided by Render (app/start command already supports it)
- Optional overrides: `MODEL_PATH`, `FEATURES_PATH`, `PPO_MODEL_PATH`, `PPO_FEATURES_PATH`, `PPO_METADATA_PATH`

**Frontend (Vercel):**
- `VITE_API_BASE_URL` = deployed backend API base URL (e.g. `https://your-backend.onrender.com/api`)
- Local dev: `VITE_API_BASE_URL=/api` (with Vite proxy)

See `backend/.env.example` and `frontend/.env.example`.

---

## 7. Testing & Verification Notes

### Reorganization/deployment-prep checks performed in this environment
- Runtime model artifacts reorganized under `backend/models/placement` and `backend/models/ppo` (including PPO `metadata.json`).
- Backend model-loading paths updated to backend-relative `pathlib` resolution; models load from different working directories (verified from project root and from `backend/`).
- Placement and PPO endpoints verified with Flask test client after reorganization:
  - `GET /api/health` → `200`, model loaded
  - `GET /api/model/info` → `200`, 13 features
  - `POST /api/predict` (valid sample) → `200`, `Placed`
  - `GET /api/ppo/health` → `200`, model loaded
  - `GET /api/ppo/info` → `200`, 8 features
  - `POST /api/ppo/predict` (valid sample) → `200`, `PPO Likely` with actual probabilities
- Existing backend tests: `cd backend && python -m pytest tests -q` → **14 passed** (sklearn pickle version warnings observed in this environment).
- Frontend build: `cd frontend && npm run build` → **succeeded** (Vite chunk-size warning only).

### Important compatibility notes
- Both trained Joblib model artifacts were serialized with **scikit-learn 1.6.1** (unchanged). Deployment dependencies are now pinned to **scikit-learn==1.6.1** and Render Python is configured to **3.11.11** (`backend/.python-version`) for compatibility.
- Dependency resolution for **Python 3.11 (cp311)** with the updated `backend/requirements.txt` was verified locally by resolving/downloading wheels (including `scikit-learn 1.6.1`, `numpy`, `scipy`, `pandas`, `joblib`). However, runtime model-loading verification under the exact configured deployment stack (Python 3.11 + scikit-learn 1.6.1) could **not** be executed in this local environment because only Python 3.14 is installed and scikit-learn 1.6.1 wheels are unavailable for cp314. Validate load/inference on the Render Python 3.11 deployment after build.
- Prior post-reorganization endpoint/model checks and backend tests passed in this local Python 3.14 / scikit-learn 1.8.x environment (with existing compatibility handling), but that is not the pinned Render deployment stack.

---

## 8. Notes
- Placement and PPO trained model artifacts, features, and prediction logic are preserved (deployment-prep/path/config changes only).
- PPO metrics shown in UI/API info are synthetic-dataset evaluation results and are disclosed as such.
- Datasets were moved to `datasets/` (not deleted) and are not required for runtime prediction requests.
