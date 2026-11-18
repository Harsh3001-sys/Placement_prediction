# CareerLens — Student Intelligence Platform

> Unified academic platform with independent, integrated intelligence modules:
> 1) **Student Placement Prediction** (existing ML model)
> 2) **Student PPO Prediction** (independent ML model)
> 3) **Skill Intelligence** — **Phase 1 Skill Gap Analysis** (rule-based, explainable) + **Phase 2 Personalized Learning Recommendations** (curated resources, explainable ranking, 4-stage roadmap)
> 4) **Student Segmentation** — **Phase 3 Role-Aware K-Means Clustering** (unsupervised, explainable cluster profiling; not placement prediction)

Built with **Flask + scikit-learn** on the backend and **React 19 + TypeScript + Vite + Tailwind CSS** on the frontend.  
Prepared for deployment with **Vercel (frontend)** and **Render (backend, Gunicorn)**.

---

## 1. Project Overview

CareerLens provides decision-support insights through separate systems integrated in one application:

- **Placement Predictor**: estimates likelihood of student placement using 13 academic/experience/technical features (trained ML model).
- **PPO Predictor**: estimates likelihood of receiving a Pre-Placement Offer (PPO) using 8 internship performance indicators (independent trained ML model).
- **Skill Intelligence (Phase 1 + Phase 2)**:
  - **Phase 1 (Skill Gap Analysis)**: compares a student's current skill proficiency against role-specific benchmark requirements to compute skill gaps, priority skills, an overall role-readiness score, and an improvement roadmap (**rule-based, explainable; no trained ML model**).
  - **Phase 2 (Personalized Learning Recommendations)**: recommends curated genuine learning resources and a 4-stage personalized learning roadmap based on Phase 1 gap/priority results (**content-based, explainable ranking; no DB, no ML training/KMeans/collaborative filtering**).
- **Student Segmentation (Phase 3)**: groups students with similar role-relevant skill profiles using **real K-Means clustering** on synthetic student profiles, evaluates multiple K values per role, generates dynamic cluster names/descriptions from learned centroids and Phase 1 role requirements, and supports individual cluster assignment with comparison to cluster averages and Phase 1/2-integrated improvement insights (**unsupervised clustering; not rule-based grouping, not placement prediction**).

All systems are integrated into one UI and one Flask app, but remain **modular and independent** (separate logic/artifacts/data where applicable, separate API endpoints, and separate frontend flows). Existing Placement/PPO behavior and contracts are preserved.

### Placement Model (Existing, Preserved)
- Algorithm: Logistic Regression pipeline (with StandardScaler)
- Task: Binary classification (`Placed` / `Not Placed`)
- Features: 13
- Training data: 10,000 records (7,000 train / 3,000 test)
- Test metrics (recorded): Accuracy **79.57%**, Precision **79.17%**, Recall **79.56%**, F1 **79.36%**, ROC-AUC **87.39%**

### PPO Model (Independent, Preserved)
- Algorithm: Logistic Regression (with StandardScaler)
- Task: Binary classification (`PPO Likely` / `PPO Unlikely`)
- Features: 8
- Decision threshold: **0.50**
- Training data: 3,000 synthetic records (2,400 train / 600 test)
- Test metrics (recorded): Accuracy **98.17%**, Precision **98.82%**, Recall **98.82%**, F1 **98.82%**, ROC-AUC **99.72%**
- **Disclosure**: trained on **synthetic data** for academic demonstration only (not guaranteed to reflect real-world PPO decisions)

### Skill Gap Analysis Engine (Phase 1, Preserved)
- Type: **Rule-based, explainable analysis system** (not an ML prediction model)
- Inputs: target role + current skill proficiency scores (0–100)
- Outputs: per-skill gaps, gap percentages, weighted priorities, overall role-readiness score (0–100), strongest skills, critical gaps, top priorities, and improvement roadmap
- **Important**: readiness is **weighted skill coverage** against selected role benchmark requirements, **not placement probability**
- **Data disclosure**: role requirements and student profiles are **synthetic, illustrative benchmarks** for demonstration/testing and are **not verified industry-wide hiring standards** or real student records

### Personalized Learning Recommendation Engine (Phase 2, Preserved)
- Type: **Content-based, explainable recommendation system** (rule-based ranking; not an ML prediction model)
- Inputs: Phase 1 analysis results (reused from same request/logic) + curated learning resources + optional user preferences
- Outputs: top 3–5 recommended resources per priority skill, explainable ranking scores/reasons, recommendation summary, and a **4-stage learning roadmap**
- **Important**: recommendation scores are ranking signals, **not scientifically validated probabilities** and **not placement guarantees/outcomes**
- **Data disclosure**: learning resources are **curated genuine resources** with URLs verified at dataset generation time (external availability/pricing/content may change over time)

### Student Segmentation Engine (Phase 3, New)
- Type: **Unsupervised clustering (K-Means)** for role-aware student segmentation (not a classification/placement model)
- Data: `backend/datasets/student_skill_profiles.csv` (1,000 synthetic profiles, 35 columns, 6 target roles)
- Role-aware features: only skills relevant to the selected role are used (from Phase 1 `role_skill_requirements.csv` mappings), with consistent feature ordering per role
- Outputs: per-role cluster overview, cluster profiles (dynamic names/descriptions/statistics), individual segment prediction (cluster assignment only), comparison with cluster averages, and personal-vs-cluster improvement insights
- **Important**: cluster assignment is **not a placement prediction** and clustering metrics on synthetic data do **not** prove real-world segmentation quality

---

## 2. Repository Structure

```text
cp/
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py              # Flask app factory, CORS, blueprint registration
│  │  ├─ routes.py                # Placement API endpoints
│  │  ├─ schemas.py               # Placement input validation
│  │  ├─ predictor.py             # Placement model loading/inference
│  │  ├─ ppo_routes.py            # PPO API endpoints
│  │  ├─ ppo_schemas.py           # PPO input validation
│  │  ├─ ppo_predictor.py         # PPO model loading/inference
│  │  ├─ skill_gap/               # Skill Intelligence (Phase 1 + Phase 2)
│  │  │  ├─ __init__.py
│  │  │  ├─ dataset_loader.py     # Load/validate skill datasets + curated learning resources
│  │  │  ├─ gap_analyzer.py       # Phase 1 gap/readiness/priority/roadmap calculations
│  │  │  ├─ recommendation_engine.py # Phase 2 explainable ranking/recommendations
│  │  │  ├─ recommendation_schemas.py # Phase 2 request/filter validation
│  │  │  ├─ roadmap_generator.py  # Phase 2 4-stage learning roadmap
│  │  │  ├─ skill_schemas.py      # Phase 1 request validation/normalization
│  │  │  └─ skill_routes.py       # Phase 1 + Phase 2 API endpoints
│  │  └─ student_segmentation/    # Student Segmentation (Phase 3)
│  │     ├─ __init__.py
│  │     ├─ preprocessing.py      # Role-aware feature selection, validation, scaling prep
│  │     ├─ clustering.py         # K evaluation/selection and reproducible KMeans training
│  │     ├─ cluster_analyzer.py   # Dynamic cluster naming/descriptions/statistics
│  │     ├─ model_loader.py       # Backend-relative artifact loading/prediction helpers
│  │     ├─ segmentation_schemas.py # Predict request validation
│  │     └─ segmentation_routes.py # `/api/segmentation/*` endpoints and Phase 1/2 reuse
│  ├─ datasets/                   # Skill Intelligence / Segmentation datasets
│  │  ├─ role_skill_requirements.csv      # Synthetic, illustrative (Phase 1; reused by Phase 3)
│  │  ├─ skill_metadata.csv               # Synthetic, illustrative (Phase 1)
│  │  ├─ student_skill_profiles.csv       # Synthetic, illustrative (Phase 1; used by Phase 3 clustering)
│  │  ├─ learning_resources.csv           # Curated genuine resources (Phase 2)
│  │  └─ learning_resources_validation_report.json # URL/coverage validation report (Phase 2)
│  ├─ scripts/
│  │  ├─ generate_skill_datasets.py       # Reproducible Phase 1 dataset generator
│  │  ├─ generate_learning_resources.py   # Reproducible Phase 2 curated resource generator + URL verification
│  │  └─ train_student_clusters.py        # Reproducible Phase 3 role-aware K-Means training + reports/plots
│  ├─ models/
│  │  ├─ placement/
│  │  │  ├─ placement_model.joblib
│  │  │  └─ features.json
│  │  ├─ ppo/
│  │  │  ├─ ppo_prediction_model.joblib
│  │  │  ├─ ppo_features.json
│  │  │  └─ metadata.json
│  │  └─ segmentation/
│  │     └─ <role_id>/                    # Per-role Phase 3 artifacts (6 roles)
│  │        ├─ kmeans_model.joblib
│  │        ├─ scaler.joblib
│  │        ├─ feature_config.json
│  │        ├─ training_metadata.json
│  │        └─ cluster_analysis.json
│  ├─ reports/
│  │  └─ segmentation/                    # Phase 3 evaluation reports and plots
│  │     ├─ training_summary.json
│  │     ├─ training_summary.md
│  │     └─ <role_id>/
│  │        ├─ *_k_evaluation_metrics.csv/.json
│  │        ├─ *_training_metadata.json
│  │        ├─ *_cluster_analysis.json
│  │        ├─ *_summary.json
│  │        └─ plots (elbow/silhouette/DB/CH/distribution/profile/PCA)
│  ├─ artifacts/                  # Legacy copies preserved (not used at runtime)
│  ├─ tests/
│  │  ├─ conftest.py
│  │  ├─ test_cors.py
│  │  ├─ test_health.py
│  │  ├─ test_predict.py
│  │  ├─ test_skill_gap.py
│  │  ├─ test_skill_recommendations.py
│  │  └─ test_student_segmentation.py
│  ├─ .env.example
│  ├─ .python-version             # 3.11.11 (Render)
│  ├─ requirements.txt
│  └─ run.py                      # Flask entry (also exposes `app` for Gunicorn)
├─ datasets/                      # Original/source datasets (preserved)
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ skill-gap/            # Skill Intelligence UI (Phase 1 + Phase 2; reused in Phase 3)
│  │  │  │  ├─ ImprovementRoadmap.tsx
│  │  │  │  ├─ LearningRecommendations.tsx
│  │  │  │  ├─ LearningRoadmap.tsx
│  │  │  │  ├─ SkillAssessment.tsx   # Reused by "Find My Student Segment"
│  │  │  │  └─ ...
│  │  ├─ pages/
│  │  │  ├─ SkillIntelligence.tsx
│  │  │  ├─ StudentSegmentation.tsx  # Phase 3 dashboard
│  │  │  └─ ...
│  │  ├─ services/api.ts          # Centralized API client (VITE_API_BASE_URL)
│  │  ├─ types/placement.ts
│  │  └─ App.tsx / Sidebar.tsx / TopNav.tsx
│  ├─ .env.example
│  ├─ package.json
│  └─ vite.config.ts
├─ .gitignore
└─ README.md
```

---

## 3. Feature Independence & Isolation

Placement, PPO, Skill Intelligence, and Student Segmentation are intentionally isolated and modular:

- **Placement ML**: `backend/app/{predictor.py,routes.py,schemas.py}` + `backend/models/placement/*`
- **PPO ML**: `backend/app/{ppo_predictor.py,ppo_routes.py,ppo_schemas.py}` + `backend/models/ppo/*`
- **Skill Intelligence (rule-based)**: `backend/app/skill_gap/*` + `backend/datasets/*`
  - Phase 1: gap analysis using synthetic role/skill/profile datasets
  - Phase 2: learning recommendations/roadmap reusing Phase 1 analysis + curated `learning_resources.csv`
- **Student Segmentation (unsupervised)**: `backend/app/student_segmentation/*` + `backend/models/segmentation/*` + `backend/reports/segmentation/*`
  - Trains/loads separate per-role K-Means artifacts (no modification/retraining of Placement or PPO)
  - Reuses Phase 1 role mappings/requirements/metadata and Phase 2 recommendation engine/dataset for interpretation and suggestions (no duplicate datasets/logic)
- Separate validation logic, API endpoints, and frontend pages/components where appropriate
- Existing Placement/PPO model artifacts, endpoints, and behavior are preserved (no ML retraining/replacement/deletion)
- Phase 2/3 extend existing flows and API patterns without duplicating Phase 1/2 logic or breaking Phase 1/2 contracts

---

## 4. Skill Intelligence Details (Phase 1 + Phase 2)

### 4.1 Supported target roles (initial)
- Software Developer (`software_developer`)
- Backend Developer (`backend_developer`)
- Frontend Developer (`frontend_developer`)
- Full Stack Developer (`full_stack_developer`)
- Data Analyst (`data_analyst`)
- Machine Learning Engineer (`ml_engineer`)

Each role includes role-relevant skills with role-specific required proficiency and importance weights (used by Phase 1/2 and reused by Phase 3 role-aware clustering).

### 4.2 Phase 1 datasets (synthetic, illustrative)
Generated by `backend/scripts/generate_skill_datasets.py` (fixed seed, reproducible, safe to rerun):

1. `backend/datasets/role_skill_requirements.csv`
   - Columns: `role_id, role_name, skill_id, skill_name, required_proficiency, importance_weight, skill_category, is_core_skill`
   - 6 roles, 81 role-skill rows, 33 unique skills
   - Proficiency scale: 0–100, positive importance weights normalized to sum to **1.0 per role**

2. `backend/datasets/skill_metadata.csv`
   - Columns: `skill_id, skill_name, skill_category, description, beginner_description, intermediate_description, advanced_description`
   - 33 rows with consistent skill IDs used across datasets

3. `backend/datasets/student_skill_profiles.csv`
   - Columns: `student_id, target_role` + skill proficiency columns (union of skills used across roles)
   - **1,000 synthetic profiles**, 35 columns, no missing cells, no duplicate `student_id`
   - Role distribution: `software_developer=167`, `backend_developer=167`, `frontend_developer=167`, `full_stack_developer=167`, `data_analyst=166`, `ml_engineer=166`

**Phase 1 data notes**
- All Phase 1 datasets are **synthetic and illustrative** for demonstration/testing.
- Role requirements are **not verified industry-wide hiring standards**.
- Student profiles are **not real student records** and not ground truth.

### 4.3 Phase 1 algorithm and formulas (rule-based)

For each skill in the selected role:
- **Skill Gap**: `Gap = max(0, Required Proficiency - Current Proficiency)`
- **Gap Percentage**: `(Gap / Required Proficiency) * 100` (if `Required Proficiency == 0`, treated as `0`)
- **Weighted Skill Priority**: `Priority = (Gap / 100) * Importance Weight`

**Overall Role Readiness (0–100):**
- `Readiness Score = Σ(Current Proficiency × Importance Weight)` (importance weights normalized per role; result clamped to 0–100)
- Current proficiency inputs are validated/clamped to 0–100
- If current proficiency exceeds required proficiency, the student is **not penalized** (gap becomes 0; readiness uses current proficiency as provided)
- Missing role skill inputs in analysis requests are handled consistently by defaulting to **0**
- Skills not relevant to the selected role are excluded from calculations

**Gap classification (priority labels):**
- `Critical Gap`: gap > 30
- `Moderate Gap`: 15 < gap ≤ 30
- `Minor Gap`: 0 < gap ≤ 15
- `Strong`: gap == 0

**Phase 1 roadmap generation:**
- Immediate focus: critical gaps (sorted by weighted priority)
- Next focus: moderate gaps
- Maintain strengths: strong/low-gap skills (with maintenance tips)

### 4.4 Phase 2 curated learning resources dataset

Generated by `backend/scripts/generate_learning_resources.py` (safe to rerun; overwrites output) and stored in:
- `backend/datasets/learning_resources.csv`
- `backend/datasets/learning_resources_validation_report.json` (URL verification + coverage report)

**Dataset characteristics (current generated dataset):**
- **165** curated resources covering **33/33** Phase 1 skills
- **URL verification (final run): 165 OK, 0 failed** (HTTP reachability checked during generation; report saved in `learning_resources_validation_report.json`)
- Free vs paid-limited: **152 free / 13 paid-limited**
- Difficulty distribution: **Beginner 87 / Intermediate 63 / Advanced 15**
- Resource types include: **Documentation, Interactive Tutorial, Course, Practice Platform, Book or Reading Material, Video Course, Project Tutorial**

**Required resource metadata columns:**
- `resource_id`, `resource_title`, `skill_id`, `skill_name`, `provider`, `resource_type`, `difficulty_level`, `description`, `resource_url`, `estimated_hours`, `prerequisites`, `is_free`, `language`, `quality_score`, `tags`

**Curation/validation rules:**
- Genuine, curated resources only (no fabricated titles, URLs, or attributions)
- Skill IDs/names aligned with Phase 1 `skill_metadata.csv`
- No duplicate resource IDs/URLs, valid difficulty/resource types, positive estimated hours, valid quality scores
- URL verification is performed at generation time; external availability/pricing/content may still change later

### 4.5 Phase 2 recommendation algorithm (explainable, content-based)

Phase 2 reuses Phase 1 analysis and ranks curated resources per priority skill.

**Difficulty mapping (student proficiency → level):**
- `0–30`: Beginner
- `31–65`: Intermediate
- `66–100`: Advanced

**Recommendation score (normalized 0–100 components, initial configurable weights, not scientifically validated):**
- `Recommendation Score = 0.40*SkillPriority + 0.25*DifficultyMatch + 0.20*ResourceQuality + 0.10*Relevance + 0.05*FreeResource`

**Selection behavior:**
- Returns **top 3–5 resources per priority skill** (or fewer if unavailable; no fabricated recommendations)
- Deduplicates recommendations per skill, favors diversity of resource types where possible
- Supports preferences: `free_only`, `preferred_types`, `difficulty_preference` (`adaptive|beginner|intermediate|advanced`)
- Generates meaningful, condition-based explanations and adds maintenance recommendations for **Strong** skills

### 4.6 Phase 2 personalized learning roadmap (4 stages)

1. **Immediate Focus** — Critical gap skills; start with foundational resources addressing highest-priority gaps
2. **Skill Development** — Moderate gap skills; build depth with intermediate learning and practice
3. **Strengthening Skills** — Minor/near-benchmark gaps; use practice/revision to close remaining gaps
4. **Maintain Strengths** — Strong skills at/near benchmark; occasional advanced practice/maintenance resources

Estimated hours are calculated from actual selected resource metadata (estimates only).

---

## 5. Student Segmentation (Phase 3)

### 5.1 Why K-Means (and what it is not)
- **K-Means** is an unsupervised clustering algorithm that groups students by similarity in role-relevant skill profiles (distance to learned centroids in standardized feature space).
- It is appropriate here for discovering interpretable cohort patterns in numeric proficiency data without labels.
- Phase 3 uses **real `sklearn.cluster.KMeans`** (not manual/rule-based grouping, not a classifier, and **not placement prediction**).

### 5.2 Dataset and role-aware clustering
- Source: `backend/datasets/student_skill_profiles.csv` (**1,000 synthetic profiles**, 35 columns, no missing cells, no duplicate `student_id`)
- Role distribution: `software_developer=167`, `backend_developer=167`, `frontend_developer=167`, `full_stack_developer=167`, `data_analyst=166`, `ml_engineer=166`
- Profiles are loaded via `app.skill_gap.dataset_loader.STUDENT_PROFILES_CSV`
- **Role-aware feature selection**: for each role, only skills relevant to that role are used, derived from existing Phase 1 mappings (`get_role_requirements()` / `role_skill_requirements.csv`)
- **Consistent feature ordering per role** is enforced and persisted in `feature_config.json`
- Irrelevant skills are excluded from role models; roles with insufficient samples for evaluation/training are rejected with informative errors

**Features per role (current trained artifacts):**
- `backend_developer`: 14
- `data_analyst`: 12
- `frontend_developer`: 13
- `full_stack_developer`: 15
- `ml_engineer`: 14
- `software_developer`: 13

### 5.3 Preprocessing and scaling
- Numeric validation and conversion for role-relevant skill columns
- Missing/non-numeric handling and duplicate checks during role dataset preparation
- Role-based feature selection and ordered feature matrix construction
- **`StandardScaler` fit on role training data only** and persisted per role (`scaler.joblib`) to avoid leakage between fitting and inference artifacts
- Individual prediction builds an ordered feature vector for the selected role and applies the persisted scaler/model (no retraining)

### 5.4 K selection and metrics interpretation (real results)
- For roles with sufficient samples, Phase 3 evaluates **`K = 2..8`**
- Metrics computed per candidate K: **WCSS/Inertia** (Elbow), **Silhouette** (higher better), **Davies-Bouldin** (lower better), **Calinski-Harabasz** (higher better)
- **Defensible K selection (not a single metric):** aggregate rank across Silhouette, Davies-Bouldin, and Calinski-Harabasz, with tie-breakers (higher Silhouette, then smaller K/parsimony). WCSS is reported for elbow analysis but not used as the sole selector.
- Reproducible training: `KMeans(random_state=42, n_init=10, max_iter=300)`

**Selected K and metrics (from `backend/reports/segmentation/training_summary.json`):**
| Role | Students | Features | Selected K | Silhouette ↑ | Davies-Bouldin ↓ | Calinski-Harabasz ↑ | WCSS |
|---|---:|---:|---:|---:|---:|---:|---:|
| Backend Developer (`backend_developer`) | 167 | 14 | 2 | 0.24604226012277203 | 1.424495240401174 | 72.37902648351955 | 1625.122512779294 |
| Data Analyst (`data_analyst`) | 166 | 12 | 2 | 0.291372435314659 | 1.2651578274320752 | 96.957790684808 | 1251.8806169484426 |
| Frontend Developer (`frontend_developer`) | 167 | 13 | 2 | 0.3153917094681985 | 1.1994740344579258 | 110.01856886278156 | 1302.5120502998789 |
| Full Stack Developer (`full_stack_developer`) | 167 | 15 | 2 | 0.2692961706051056 | 1.3238573638211029 | 89.09468360839739 | 1626.657410262874 |
| ML Engineer (`ml_engineer`) | 166 | 14 | 2 | 0.2994616009321471 | 1.2095553147087714 | 106.7888233351561 | 1407.502700095812 |
| Software Developer (`software_developer`) | 167 | 13 | 2 | 0.2637790619357428 | 1.379410071985099 | 83.63749757882626 | 1440.7118937739228 |

**Interpretation notes:** in the evaluated range, K=2 was the metric leader for Silhouette, Davies-Bouldin, and Calinski-Harabasz for all 6 roles on this synthetic dataset; aggregate-rank selection rationale is stored per role in training metadata/reports. Metrics indicate structure/separation on the provided synthetic data and do **not** establish real-world segmentation quality.

### 5.5 Cluster interpretation logic (dynamic, data-driven)
- For each role/cluster, Phase 3 computes: student counts/percentages, average proficiency per skill, strongest/weakest skills/patterns, cluster average proficiency, and difference from overall role average
- **Cluster names/descriptions are generated dynamically** from learned centroids and Phase 1 role requirements/metadata (no hardcoded ID-based labels)
- Cluster profile outputs include category/profile context and comparison against role benchmark requirements (illustrative)

**Discovered clusters (current artifacts):**
- **Backend Developer**: `Developing Python & SQL Profile` (61, 36.53%), `Strong Node.js & REST APIs Profile` (106, 63.47%)
- **Data Analyst**: `Developing DBMS & Python Profile` (86, 51.81%), `Strong Git/GitHub & Matplotlib Profile` (80, 48.19%)
- **Frontend Developer**: `Strong Problem Solving & CSS Profile` (87, 52.10%), `Developing OOP & SQL Profile` (80, 47.90%)
- **Full Stack Developer**: `Strong Git/GitHub & Node.js Profile` (92, 55.09%), `Developing OOP & Communication Profile` (75, 44.91%)
- **ML Engineer**: `Strong Statistics & Matplotlib Profile` (79, 47.59%), `Developing SQL & TensorFlow Profile` (87, 52.41%)
- **Software Developer**: `Developing DBMS & Computer Networks Profile` (78, 46.71%), `Strong Problem Solving & Operating Systems Profile` (89, 53.29%)

(Full dynamic descriptions, per-skill centroid averages, and rationales are in `backend/reports/segmentation/training_summary.json` and per-role `cluster_analysis.json` artifacts/reports.)

### 5.6 Training, artifacts, and reports
- Training script: `backend/scripts/train_student_clusters.py` (role-aware, reproducible, saves artifacts + reports/plots)
- Per-role runtime artifacts in `backend/models/segmentation/<role_id>/`:
  - `kmeans_model.joblib`
  - `scaler.joblib`
  - `feature_config.json`
  - `training_metadata.json`
  - `cluster_analysis.json`
- Evaluation artifacts/reports in `backend/reports/segmentation/`:
  - `training_summary.json`, `training_summary.md`
  - per-role `*_k_evaluation_metrics.csv/.json`, `*_training_metadata.json`, `*_cluster_analysis.json`, `*_summary.json`
  - plots per role: elbow/WCSS, silhouette-by-K, Davies-Bouldin-by-K, Calinski-Harabasz-by-K, cluster distribution, cluster profile comparison, and **PCA 2D visualization** (visualization only)
- Backend loads artifacts via backend-relative paths; `GET /api/segmentation/roles` returns Phase 1 roles with available trained segmentation artifacts

### 5.7 Backend APIs (`/api/segmentation`)
- `GET /api/segmentation/roles` — roles with available trained segmentation artifacts/summary info
- `GET /api/segmentation/overview/<role_id>` — role overview (students analyzed, selected K, evaluation metrics, cluster distribution, summary)
- `GET /api/segmentation/clusters/<role_id>` — detailed cluster profiles (dynamic names/descriptions/statistics/skill averages)
- `POST /api/segmentation/predict` — individual cluster assignment (no retraining) with comparison to cluster averages and improvement insights
- `GET /api/segmentation/model-info/<role_id>` — persisted model/scaler/feature/training metadata

**`POST /api/segmentation/predict` request (example):**
```json
{
  "target_role": "frontend_developer",
  "skills": {
    "React": 70,
    "JavaScript": 65,
    "CSS": 60,
    "HTML": 75
  }
}
```
Notes:
- `target_role` must be a supported role with trained segmentation artifacts
- `skills` must include valid role-relevant skills (names/IDs per role mapping), numeric values in `0–100`
- Response includes predicted cluster ID/name/description/characteristics, strongest/weakest skills, comparison with cluster averages, recommended improvement areas, and **explicitly separated** personal vs cluster-level insights

### 5.8 Frontend dashboard and integration
- New **Student Segmentation** page: `frontend/src/pages/StudentSegmentation.tsx` (added to existing navigation/routing in `App.tsx`, `Sidebar.tsx`, `TopNav.tsx`)
- Uses existing centralized API client and types (`frontend/src/services/api.ts`, `frontend/src/types/placement.ts`) with `VITE_API_BASE_URL` normalization (no hardcoded localhost URLs, no duplicate API client)
- Role selection, overview cards (clusters/students/K/silhouette/distribution), cluster distribution chart, cluster skill comparison chart (real centroid data), and cluster profile cards (dynamic name/description/stats/strong/weak/avg)
- **“Find My Student Segment”** reuses Phase 1 `SkillAssessment` component patterns, calls `POST /api/segmentation/predict`, and displays predicted cluster, comparison highlights, and separated insights
- Real API data only; responsive layout with loading/error/empty states; follows existing theme/patterns

### 5.9 Phase 1/Phase 2 integration (no duplicated logic/data)
- **Phase 1 reuse:** role requirements/mappings/metadata and rule-based `analyze_skill_gap` are reused for personal and cluster-centroid gap interpretation
- **Phase 2 reuse:** existing recommendation engine/dataset (`recommend_for_analysis`/`generate_learning_roadmap` and curated `learning_resources.csv`) are reused for individual-gap and cluster-weakness suggestions
- **Clear separation:** personal gaps/recommendations are computed from the submitted student profile; cluster-level weaknesses/recommendations are derived from the predicted cluster centroid profile for the role cohort

---

## 6. Backend API Endpoints

### Health & Info
- `GET /` — API metadata and endpoint index
- `GET /api/health` — Placement service/model health
- `GET /api/model/info` — Placement model metadata
- `GET /api/ppo/health` — PPO service/model health
- `GET /api/ppo/info` — PPO model metadata

### Prediction
- `POST /api/predict` — Placement prediction (13 features)
- `POST /api/ppo/predict` — PPO prediction (8 features)

### Skill Intelligence (Phase 1 + Phase 2)
- `GET /api/skills/roles` — Supported roles and role-level metadata
- `GET /api/skills/requirements/<role_id>` — Role skill requirements (ordered by importance)
- `GET /api/skills/metadata` — Skill metadata/descriptions (all skills)
- `POST /api/skills/analyze` — Rule-based gap analysis and Phase 1 roadmap (preserved contract)
- `GET /api/skills/resources` — Browse curated learning resources (filters: `skill_id`, `difficulty`, `resource_type`, `free_only`, `provider`)
- `GET /api/skills/resources/summary` — Learning resources dataset summary/counts/distribution/disclosure
- `POST /api/skills/recommend` — Reuses Phase 1 analysis and returns recommendations + 4-stage roadmap

### Student Segmentation (Phase 3)
- `GET /api/segmentation/roles` — Roles with available trained segmentation artifacts
- `GET /api/segmentation/overview/<role_id>` — Segmentation overview for role (students, selected K, metrics, distribution)
- `GET /api/segmentation/clusters/<role_id>` — Cluster profiles for role (dynamic names/descriptions/statistics)
- `POST /api/segmentation/predict` — Predict student segment/cluster and return comparison + integrated insights
- `GET /api/segmentation/model-info/<role_id>` — Segmentation model/scaler/feature/training metadata

### Validation & Errors
- Placement/PPO endpoints validate feature presence, types, and ranges per schema.
- Skill endpoints validate `target_role`, skill ranges, known skills for the selected role, and Phase 2 filters/preferences.
- Segmentation endpoints validate role availability/artifacts, request payload/skill inputs, and return meaningful HTTP errors for invalid roles/inputs/missing models/datasets.
- Consistent JSON error responses for invalid JSON, validation failures, missing resources/models, and service unavailability.

---

## 7. Frontend Integration

- **Placement/PPO pages** remain unchanged in behavior and continue to use existing endpoints and UI patterns.
- **Skill Intelligence page** (`frontend/src/pages/SkillIntelligence.tsx`) integrates Phase 1 and Phase 2 in one flow (analysis + personalized recommendations + 4-stage roadmap).
- **Student Segmentation page** (`frontend/src/pages/StudentSegmentation.tsx`) integrates Phase 3:
  - Loads available segmentation roles and role overview/cluster profiles from `/api/segmentation/*`
  - Renders role-aware clustering overview, distribution/comparison charts, and dynamic cluster profile cards
  - Reuses Phase 1 `SkillAssessment` component for “Find My Student Segment” and calls `POST /api/segmentation/predict`
  - Displays predicted cluster, comparison with cluster averages, and clearly separated personal vs cluster-level insights/recommendations
- Frontend uses centralized API client (`frontend/src/services/api.ts`) with `VITE_API_BASE_URL` normalization (`/api` in dev/proxy or backend origin/origin+`/api` in deployed environments).

---

## 8. Local Setup & Run

### Prerequisites
- Python **3.11** (recommended; matches Render config) or compatible local environment
- Node.js **18+** and npm
- pip

### 8.1 Backend (Flask API)

```bash
cd backend
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
python run.py
```

Backend runs at `http://127.0.0.1:5000` by default.

**Optional backend env vars** (`backend/.env` or environment):
```env
PORT=5000
FLASK_ENV=development
SECRET_KEY=dev-careerlens-key-academic-only
# Comma-separated origins (no trailing slashes)
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 8.2 Generate Skill Intelligence datasets (required/reproducible)

**Phase 1 (synthetic role/skill/profile datasets):**
```bash
# from repo root (recommended)
python backend/scripts/generate_skill_datasets.py

# or
cd backend
python scripts/generate_skill_datasets.py
```
Generates/overwrites:
- `backend/datasets/role_skill_requirements.csv`
- `backend/datasets/skill_metadata.csv`
- `backend/datasets/student_skill_profiles.csv`

**Phase 2 (curated learning resources + URL verification report):**
```bash
# from repo root (recommended)
python backend/scripts/generate_learning_resources.py

# or
cd backend
python scripts/generate_learning_resources.py
```
Generates/overwrites:
- `backend/datasets/learning_resources.csv`
- `backend/datasets/learning_resources_validation_report.json`

### 8.3 Train Student Segmentation models (Phase 3)

Requires Phase 1 datasets/mappings (especially `student_skill_profiles.csv` and `role_skill_requirements.csv`).

```bash
# from repo root (recommended)
python backend/scripts/train_student_clusters.py

# or
cd backend
python scripts/train_student_clusters.py
```

Generates/overwrites:
- `backend/models/segmentation/<role_id>/` artifacts (`kmeans_model.joblib`, `scaler.joblib`, `feature_config.json`, `training_metadata.json`, `cluster_analysis.json`)
- `backend/reports/segmentation/` summaries, per-role metrics/JSON, and plots (including PCA 2D visualization)

Notes:
- Training is reproducible (`random_state=42`, `n_init=10`, `max_iter=300`).
- Serialized artifacts are intended for the pinned backend runtime stack (`scikit-learn==1.6.1`, Python 3.11.11). Loading artifacts in a different scikit-learn version may produce unpickle/version warnings or incompatibilities.

### 8.4 Frontend (React/Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` (Vite dev proxy forwards `/api` to `http://127.0.0.1:5000`).

**Frontend env var** (`frontend/.env`):
```env
VITE_API_BASE_URL=/api
```
For deployed environments, set `VITE_API_BASE_URL` to your backend URL (origin or origin + `/api`).

---

## 9. Verification & Testing

### Backend tests
```bash
cd backend
python -m pytest tests -q
```
Covers CORS, placement health/predict, PPO, Phase 1 skill-gap dataset loading/validation/algorithm/API, Phase 2 resource loading/filtering/difficulty matching/ranking/deduplication/roadmap/API validation/integration, and **Phase 3 segmentation** (dataset loading, role feature selection, preprocessing/scaling, K evaluation/selection, cluster analysis/assignment, prediction, invalid inputs/missing models, API success/failure, Phase 1/2 integration).

**Latest recorded run (local):** `51 passed, 124 warnings` (warnings include scikit-learn pickle/version mismatch warnings under local Python 3.14/scikit-learn 1.8.0 while artifacts/runtime target 3.11.11/1.6.1).

### Frontend build
```bash
cd frontend
npm run build
```
**Latest recorded run:** succeeded (`tsc -b && vite build`; chunk-size warning only).

### Manual / smoke checks
- Placement APIs: `/api/health`, `/api/predict`, `/api/model/info`
- PPO APIs: `/api/ppo/health`, `/api/ppo/predict`, `/api/ppo/info`
- Skill Intelligence APIs: `/api/skills/roles`, `/api/skills/requirements/<role_id>`, `/api/skills/metadata`, `/api/skills/analyze`, `/api/skills/resources`, `/api/skills/resources/summary`, `/api/skills/recommend`
- Segmentation APIs: `/api/segmentation/roles`, `/api/segmentation/overview/<role_id>`, `/api/segmentation/clusters/<role_id>`, `/api/segmentation/model-info/<role_id>`, `POST /api/segmentation/predict`
- UI: Placement Predictor, PPO Predictor, **Skill Intelligence**, and **Student Segmentation** (overview/clusters/charts + “Find My Student Segment”) render and use real API data

**Latest recorded segmentation smoke test (Flask test client):** `/api/segmentation/roles` returned 6 available roles; overview/clusters/model-info for `frontend_developer` succeeded; `POST /api/segmentation/predict` returned predicted cluster, cluster comparison, personal gaps, and individual-gap recommendations.

---

## 10. Deployment (Vercel + Render)

### Backend (Render Web Service)
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn run:app --bind 0.0.0.0:$PORT`
- **Python**: `3.11.11` (via `backend/.python-version`)
- **Environment variables**:
  - `SECRET_KEY=<strong-random-secret>`
  - `ALLOWED_ORIGINS=https://<your-vercel-app>.vercel.app` (comma-separated, no trailing slashes)

### Frontend (Vercel)
- **Root Directory**: `frontend`
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment variable**:
  - `VITE_API_BASE_URL=https://<your-render-service>.onrender.com` (or `/api` if proxied)

Notes:
- `backend/requirements.txt` pins a Render-compatible stack for serialized model loading (incl. `scikit-learn==1.6.1`) and includes `matplotlib` for Phase 3 report/plot generation.
- Runtime model artifacts are loaded from `backend/models/placement/*`, `backend/models/ppo/*`, and `backend/models/segmentation/*`; Placement/PPO datasets are not required at runtime.
- Skill Intelligence and Student Segmentation APIs read CSV datasets from `backend/datasets/` (Phase 1 synthetic datasets, Phase 2 `learning_resources.csv`, and Phase 3 use of `student_skill_profiles.csv`/role mappings must be present). Ensure trained segmentation artifacts/reports are available in deployed environments if the segmentation UI is enabled.

---

## 11. Limitations & Responsible Use
- Placement and PPO outputs are **decision-support estimates**, not guarantees.
- PPO model is trained on **synthetic data** and may not reflect real company policies.
- Skill Gap (Phase 1) role requirements and student profiles are **synthetic illustrative benchmarks**, not verified industry-wide hiring standards or real records.
- Skill Gap readiness is **weighted skill coverage** for a selected role benchmark, **not placement probability**.
- Learning resources (Phase 2) are **curated genuine resources** with URLs verified at dataset generation time; external availability, pricing, and content may change.
- Phase 2 recommendation scores are **rule-based, explainable ranking signals** with initial configurable weights (**not scientifically validated**) and do **not** predict placement outcomes or guarantee learning/job results.
- **Student Segmentation (Phase 3)** uses **synthetic student profiles** and produces **cluster labels/descriptions derived from learned centroids** on synthetic data with illustrative role mappings; these are **not real student records** and **not verified real-world segments**.
- Clustering evaluation metrics (Silhouette, Davies-Bouldin, Calinski-Harabasz, WCSS/elbow) indicate structure/separation on the provided synthetic dataset and **do not prove real-world segmentation quality**; selected K is defensible by the implemented multi-metric strategy but not a ground-truth optimum.
- **Cluster assignment is not a placement prediction**, not a hiring outcome, and not a guarantee of performance or readiness.
- Improvement recommendations based on individual gaps and cluster patterns are guidance only; personal and cluster-level insights should be interpreted separately.
- Validate on **real, representative student data** and appropriate evaluation processes before drawing real-world conclusions.
- Estimated learning hours are summed from actual resource metadata and are **estimates**, not guaranteed completion times.
- Improvement roadmaps and recommendations are guidance only.
