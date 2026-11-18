# Student Segmentation Training Summary

Generated (UTC): 2026-11-18T10:55:39.335147+00:00

- Dataset: `backend/datasets/student_skill_profiles.csv`
- Roles trained: backend_developer, data_analyst, frontend_developer, full_stack_developer, ml_engineer, software_developer
- K range evaluated: 2..8

## Role Results

### Backend Developer (`backend_developer`)
- Students: 167 | Features: 14 | Selected K: 2
- Silhouette: 0.24604226012277203 | Davies-Bouldin: 1.424495240401174 | Calinski-Harabasz: 72.37902648351955 | WCSS: 1625.122512779294
- Rationale: Selected K=2 using aggregate rank across Silhouette (higher better), Davies-Bouldin (lower better), and Calinski-Harabasz (higher better) for K=2..8. Ties broken by higher Silhouette, then smaller K (parsimony). For selected K: Silhouette=0.24604226012277203, Davies-Bouldin=1.424495240401174, Calinski-Harabasz=72.37902648351955, WCSS=1625.122512779294. Metric leaders in evaluated range: best Silhouette K=2, best Davies-Bouldin K=2, best Calinski-Harabasz K=2. WCSS is reported for elbow analysis; K was not chosen by a single metric.
  - Cluster 0 (Developing Python & SQL Profile): 61 students (36.53%), avg 53.06
  - Cluster 1 (Strong Node.js & REST APIs Profile): 106 students (63.47%), avg 69.06

### Data Analyst (`data_analyst`)
- Students: 166 | Features: 12 | Selected K: 2
- Silhouette: 0.291372435314659 | Davies-Bouldin: 1.2651578274320752 | Calinski-Harabasz: 96.957790684808 | WCSS: 1251.8806169484426
- Rationale: Selected K=2 using aggregate rank across Silhouette (higher better), Davies-Bouldin (lower better), and Calinski-Harabasz (higher better) for K=2..8. Ties broken by higher Silhouette, then smaller K (parsimony). For selected K: Silhouette=0.291372435314659, Davies-Bouldin=1.2651578274320752, Calinski-Harabasz=96.957790684808, WCSS=1251.8806169484426. Metric leaders in evaluated range: best Silhouette K=2, best Davies-Bouldin K=2, best Calinski-Harabasz K=2. WCSS is reported for elbow analysis; K was not chosen by a single metric.
  - Cluster 0 (Developing DBMS & Python Profile): 86 students (51.81%), avg 53.43
  - Cluster 1 (Strong Git/GitHub & Matplotlib Profile): 80 students (48.19%), avg 71.34

### Frontend Developer (`frontend_developer`)
- Students: 167 | Features: 13 | Selected K: 2
- Silhouette: 0.3153917094681985 | Davies-Bouldin: 1.1994740344579258 | Calinski-Harabasz: 110.01856886278156 | WCSS: 1302.5120502998789
- Rationale: Selected K=2 using aggregate rank across Silhouette (higher better), Davies-Bouldin (lower better), and Calinski-Harabasz (higher better) for K=2..8. Ties broken by higher Silhouette, then smaller K (parsimony). For selected K: Silhouette=0.3153917094681985, Davies-Bouldin=1.1994740344579258, Calinski-Harabasz=110.01856886278156, WCSS=1302.5120502998789. Metric leaders in evaluated range: best Silhouette K=2, best Davies-Bouldin K=2, best Calinski-Harabasz K=2. WCSS is reported for elbow analysis; K was not chosen by a single metric.
  - Cluster 0 (Strong Problem Solving & CSS Profile): 87 students (52.1%), avg 66.54
  - Cluster 1 (Developing OOP & SQL Profile): 80 students (47.9%), avg 47.5

### Full Stack Developer (`full_stack_developer`)
- Students: 167 | Features: 15 | Selected K: 2
- Silhouette: 0.2692961706051056 | Davies-Bouldin: 1.3238573638211029 | Calinski-Harabasz: 89.09468360839739 | WCSS: 1626.657410262874
- Rationale: Selected K=2 using aggregate rank across Silhouette (higher better), Davies-Bouldin (lower better), and Calinski-Harabasz (higher better) for K=2..8. Ties broken by higher Silhouette, then smaller K (parsimony). For selected K: Silhouette=0.2692961706051056, Davies-Bouldin=1.3238573638211029, Calinski-Harabasz=89.09468360839739, WCSS=1626.657410262874. Metric leaders in evaluated range: best Silhouette K=2, best Davies-Bouldin K=2, best Calinski-Harabasz K=2. WCSS is reported for elbow analysis; K was not chosen by a single metric.
  - Cluster 0 (Strong Git/GitHub & Node.js Profile): 92 students (55.09%), avg 68.1
  - Cluster 1 (Developing OOP & Communication Profile): 75 students (44.91%), avg 50.35

### Machine Learning Engineer (`ml_engineer`)
- Students: 166 | Features: 14 | Selected K: 2
- Silhouette: 0.2994616009321471 | Davies-Bouldin: 1.2095553147087714 | Calinski-Harabasz: 106.7888233351561 | WCSS: 1407.502700095812
- Rationale: Selected K=2 using aggregate rank across Silhouette (higher better), Davies-Bouldin (lower better), and Calinski-Harabasz (higher better) for K=2..8. Ties broken by higher Silhouette, then smaller K (parsimony). For selected K: Silhouette=0.2994616009321471, Davies-Bouldin=1.2095553147087714, Calinski-Harabasz=106.7888233351561, WCSS=1407.502700095812. Metric leaders in evaluated range: best Silhouette K=2, best Davies-Bouldin K=2, best Calinski-Harabasz K=2. WCSS is reported for elbow analysis; K was not chosen by a single metric.
  - Cluster 0 (Strong Statistics & Matplotlib Profile): 79 students (47.59%), avg 75.46
  - Cluster 1 (Developing SQL & TensorFlow Profile): 87 students (52.41%), avg 56.89

### Software Developer (`software_developer`)
- Students: 167 | Features: 13 | Selected K: 2
- Silhouette: 0.2637790619357428 | Davies-Bouldin: 1.379410071985099 | Calinski-Harabasz: 83.63749757882626 | WCSS: 1440.7118937739228
- Rationale: Selected K=2 using aggregate rank across Silhouette (higher better), Davies-Bouldin (lower better), and Calinski-Harabasz (higher better) for K=2..8. Ties broken by higher Silhouette, then smaller K (parsimony). For selected K: Silhouette=0.2637790619357428, Davies-Bouldin=1.379410071985099, Calinski-Harabasz=83.63749757882626, WCSS=1440.7118937739228. Metric leaders in evaluated range: best Silhouette K=2, best Davies-Bouldin K=2, best Calinski-Harabasz K=2. WCSS is reported for elbow analysis; K was not chosen by a single metric.
  - Cluster 0 (Developing DBMS & Computer Networks Profile): 78 students (46.71%), avg 48.68
  - Cluster 1 (Strong Problem Solving & Operating Systems Profile): 89 students (53.29%), avg 65.95
