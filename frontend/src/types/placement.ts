/**
 * Data contracts and TypeScript type definitions for CareerLens.
 */

export interface StudentFormData {
  CGPA: number;
  SSC_Marks: number;
  HSC_Marks: number;
  AptitudeTestScore: number;
  SoftSkillsRating: number;
  Internships: number;
  Projects: number;
  "Workshops/Certifications": number;
  PlacementTraining: "Yes" | "No";
  ExtracurricularActivities: "Yes" | "No";
  LeetCode_Problems_Solved: number;
  Hackathon_Wins: number;
  Publications: number;
}

export type PredictionRequest = StudentFormData;

export interface PredictionResponse {
  prediction: "Placed" | "Not Placed";
  placement_probability: number;
  not_placed_probability: number;
  model: string;
  features_analyzed: number;
  disclaimer: string;
}

export interface ApiErrorResponse {
  error: string;
  message?: string;
  details?: string[];
}

export interface HealthResponse {
  status: "healthy" | "degraded";
  model_loaded: boolean;
  model_name: string;
  n_features: number;
  sklearn_version: string;
  service: string;
}

export interface ConfusionMatrixData {
  true_negative: number;
  false_positive: number;
  false_negative: number;
  true_positive: number;
  matrix: number[][];
  labels: string[];
}

export interface ModelEvaluation {
  test_accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  dataset_total_samples: number;
  train_samples: number;
  test_samples: number;
  split_ratio: string;
  algorithm: string;
  confusion_matrix: ConfusionMatrixData;
  synthetic_features: string[];
  synthetic_disclosure: string;
}

export interface RocPoint {
  fpr: number;
  tpr: number;
}

export interface ModelInfoResponse {
  model_name: string;
  is_loaded: boolean;
  n_features: number;
  features: string[];
  feature_metadata: Record<string, any>;
  coefficients: Record<string, number>;
  intercept: number | null;
  evaluation: ModelEvaluation;
  roc_curve: RocPoint[];
}

export type PageView = "overview" | "predictor" | "ppo-predictor" | "model-insights" | "about" | "api-status";

export interface PPOFormData {
  Technical_Evaluation: number;
  Task_Completion_Rate: number;
  Attendance_Rate: number;
  Communication_Score: number;
  Manager_Rating: number;
  Code_Quality_Score: number;
  Teamwork_Score: number;
  Deadline_Adherence: number;
}

export interface PPOPredictionResponse {
  success: boolean;
  model: "ppo_prediction";
  prediction: 0 | 1;
  prediction_label: "PPO Likely" | "PPO Unlikely";
  ppo_probability: number;
  no_ppo_probability: number;
  threshold: number;
  raw_model_prediction?: number;
}

export interface PPOHealthResponse {
  status: "healthy" | "degraded";
  model_loaded: boolean;
  model: "ppo_prediction";
  n_features: number;
  threshold: number;
  load_error?: string | null;
}

export interface PPOFeatureDefinition {
  type: string;
  min: number;
  max: number;
  label: string;
  description: string;
}

export interface PPOEvaluation {
  test_accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  balanced_accuracy?: number;
}

export interface PPOModelInfoResponse {
  is_loaded: boolean;
  features: string[];
  feature_definitions?: Record<string, PPOFeatureDefinition>;
  load_error?: string | null;
  algorithm: string;
  dataset: string;
  dataset_records: number;
  n_features: number;
  threshold: number;
  evaluation: PPOEvaluation;
  coefficients: Record<string, number>;
  disclosure: string;
}
