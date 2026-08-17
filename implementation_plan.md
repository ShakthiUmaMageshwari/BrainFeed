# BrainFeed: Convert JS Backend → Python ML Backend

Convert the entire Express.js + sql.js backend into a **FastAPI + SQLAlchemy** Python backend, replacing hand-coded ML logic with real ML libraries (scikit-learn, XGBoost, NumPy, pandas, scipy).

Frontend (7 HTML pages) stays in JS — only API URLs updated to point to port `8000`.

## User Review Required

> [!IMPORTANT]
> The existing [brainfeed.db](file:///c:/Users/arund/Documents/BrainFeed%28js%20to%20python%29/db/brainfeed.db) SQLite file will be preserved. The Python backend will read/write the same DB.

> [!WARNING]
> The JS [server.js](file:///c:/Users/arund/Documents/BrainFeed%28js%20to%20python%29/server.js) (port 3000) and the new Python backend (port 8000) cannot share the same port. Frontend pages will be updated to call `http://localhost:8000/api/...`. The frontend can be served by any static file server or opened directly in the browser.

---

## Proposed Changes

### Python Project Setup

#### [NEW] [requirements.txt](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/requirements.txt)
Dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `bcrypt`, `numpy`, `pandas`, `scikit-learn`, `scipy`, `xgboost`, `matplotlib`

#### [NEW] [main.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/main.py)
FastAPI app with CORS middleware, route mounting, DB init on startup, static file serving

---

### Database Layer

#### [NEW] [database.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/db/database.py)
SQLAlchemy engine + session factory using the existing [db/brainfeed.db](file:///c:/Users/arund/Documents/BrainFeed%28js%20to%20python%29/db/brainfeed.db)

#### [NEW] [models.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/db/models.py)
SQLAlchemy ORM models for all 6 tables: `users`, `questions`, `question_attempts`, `sessions`, `mastery_logs`, `question_stats`

#### [NEW] [seed.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/db/seed.py)
Same 61 seed questions ported to Python

---

### API Routes (Express → FastAPI)

#### [NEW] [auth.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/routes/auth.py)
- `POST /api/auth/register` — bcrypt hashing, UUID generation
- `POST /api/auth/login` — bcrypt verify

#### [NEW] [questions.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/routes/questions.py)
- `GET /api/questions/feed` — adaptive difficulty + recommendations + cognitive load
- `POST /api/questions/submit` — record attempt + update mastery + streak

#### [NEW] [analytics.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/routes/analytics.py)
- `GET /api/analytics/dashboard` — runs all 15 ML engines and returns combined JSON

#### [NEW] [sessions.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/routes/sessions.py)
- `POST /api/sessions/start` and `POST /api/sessions/end`

---

### ML Engines (16 Modules → Python with Real ML Libraries)

Each JS ML module is rewritten in Python using proper ML libraries. Below is the algorithm mapping:

| # | Engine | JS Implementation | Python ML Libraries |
|---|--------|-------------------|---------------------|
| 1 | Mastery Model | Manual weighted formula | **NumPy** arrays + vectorized ops |
| 2 | Predictive Engine | Custom linear regression | **sklearn LinearRegression** + **Ridge** + **Lasso** |
| 3 | Adaptive Difficulty | Manual probability tables | **NumPy** + Bayesian probability |
| 4 | Behavior Profiler | Manual K-Means | **sklearn KMeans** + **StandardScaler** |
| 5 | Exam Readiness | Weighted scoring | **XGBoost** / **GradientBoosting** ensemble |
| 6 | Forgetting Curve | Manual exp decay | **scipy.optimize.curve_fit** + exponential model |
| 7 | Drop-off Risk | Manual logistic scoring | **sklearn LogisticRegression** + **DecisionTreeClassifier** |
| 8 | Auto Difficulty | Success rate thresholds | **sklearn SVM** + global stats |
| 9 | Recommendation Engine | Hybrid scoring formula | **NumPy** feature matrix + **pandas** ranking |
| 10 | Cognitive Load | Manual trend analysis | **NumPy** + **sklearn LogisticRegression** |
| 11 | Time of Day | Bucketed stats | **sklearn GaussianNB** (Naive Bayes) + **pandas** |
| 12 | Subject Affinity | Manual scoring | **sklearn PCA** + **KMeans clustering** |
| 13 | Learning Velocity | Half-split comparison | **sklearn PolynomialFeatures** + **ElasticNet** |
| 14 | Error Patterns | Rule-based classification | **sklearn KNeighborsClassifier** + **DecisionTreeClassifier** |
| 15 | Session Quality | Manual weighted scoring | **sklearn RandomForestRegressor** |
| 16 | Feature Engineering | Manual pipeline | **pandas DataFrame** pipeline + **NumPy** vectorized ops |

#### New Python ML files (all in `backend/ml/`):
- [mastery_model.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/mastery_model.py)
- [predictive_engine.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/predictive_engine.py)
- [adaptive_difficulty.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/adaptive_difficulty.py)
- [behavior_profiler.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/behavior_profiler.py)
- [exam_readiness.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/exam_readiness.py)
- [forgetting_curve.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/forgetting_curve.py)
- [dropoff_risk.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/dropoff_risk.py)
- [auto_difficulty.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/auto_difficulty.py)
- [recommendation_engine.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/recommendation_engine.py)
- [cognitive_load.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/cognitive_load.py)
- [time_of_day.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/time_of_day.py)
- [subject_affinity.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/subject_affinity.py)
- [learning_velocity.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/learning_velocity.py)
- [error_patterns.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/error_patterns.py)
- [session_quality.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/session_quality.py)
- [feature_engineering.py](file:///c:/Users/arund/Documents/BrainFeed(js%20to%20python)/backend/ml/feature_engineering.py)

---

### Frontend Updates

#### [MODIFY] All 7 HTML pages in `Pages/`
Update all `fetch()` calls from `http://localhost:3000/api/...` to `http://localhost:8000/api/...`

---

## Verification Plan

### Automated Tests
1. **Start Python backend**: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000`
2. **Health check**: `curl http://localhost:8000/api/health` — expect `{"status": "ok"}`
3. **Register test**: `POST http://localhost:8000/api/auth/register` with test user
4. **Login test**: `POST http://localhost:8000/api/auth/login` with test credentials
5. **Feed test**: `GET http://localhost:8000/api/questions/feed?limit=3` — expect JSON with questions array
6. **Submit test**: `POST http://localhost:8000/api/questions/submit` with an attempt
7. **Analytics test**: `GET http://localhost:8000/api/analytics/dashboard?userId=<id>` — expect all 15 ML engine outputs
8. **Session test**: `POST /api/sessions/start` → `POST /api/sessions/end`

### Manual Verification
- Open [index.html](file:///c:/Users/arund/Documents/BrainFeed%28js%20to%20python%29/index.html) or [Pages/LoginPG.html](file:///c:/Users/arund/Documents/BrainFeed%28js%20to%20python%29/Pages/LoginPG.html) in browser
- Register a new user, login, answer questions, check analytics page
- Verify ML analytics data renders correctly
