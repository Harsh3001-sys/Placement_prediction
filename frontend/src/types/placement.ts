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

export type PageView =
  | "overview"
  | "predictor"
  | "ppo-predictor"
  | "skill-intelligence"
  | "student-segmentation"
  | "model-insights";

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

export interface SkillRoleSummary {
  role_id: string;
  role_name: string;
  skill_count: number;
  core_skill_count: number;
}

export interface SkillRolesResponse {
  roles: SkillRoleSummary[];
  count: number;
  disclaimer?: string;
}

export interface SkillRequirementItem {
  skill_id: string;
  skill_name: string;
  required_proficiency: number;
  importance_weight: number;
  skill_category: string;
  is_core_skill: boolean;
}

export interface SkillRequirementsResponse {
  role_id: string;
  role_name: string;
  skill_count: number;
  skills: SkillRequirementItem[];
  disclaimer?: string;
}

export interface SkillMetadataItem {
  skill_id: string;
  skill_name: string;
  skill_category: string;
  description: string;
  beginner_description: string;
  intermediate_description: string;
  advanced_description: string;
}

export interface SkillMetadataResponse {
  skills: SkillMetadataItem[];
  count: number;
}

export interface SkillAnalysisRequest {
  target_role: string;
  skills: Record<string, number>;
}

export interface SkillComparisonItem {
  skill_id: string;
  skill_name: string;
  skill_category: string;
  is_core_skill: boolean;
  current_proficiency: number;
  required_proficiency: number;
  gap: number;
  gap_percentage: number;
  importance_weight: number;
  priority_score: number;
  priority_classification: "Strong" | "Minor Gap" | "Moderate Gap" | "Critical Gap";
  description: string;
  why_it_matters: string;
  improvement_suggestion: string;
}

export interface SkillRoadmapSkill {
  skill_name: string;
  gap: number;
  importance_weight: number;
  priority_classification: string;
  reason: string;
}

export interface SkillRoadmapPhase {
  phase: "immediate_focus" | "next_focus" | "maintain_strengths";
  title: string;
  description: string;
  skills: SkillRoadmapSkill[];
}

export interface SkillAnalysisSummary {
  total_skills: number;
  critical_gaps: number;
  moderate_gaps: number;
  minor_gaps: number;
  strong_skills: number;
}

export interface SkillAnalysisResponse {
  target_role: string;
  role_name: string;
  overall_readiness_score: number;
  readiness_score_interpretation?: string;
  skill_comparison: SkillComparisonItem[];
  strongest_skills: SkillComparisonItem[];
  skills_requiring_improvement: SkillComparisonItem[];
  top_priority_skills: SkillComparisonItem[];
  improvement_roadmap: SkillRoadmapPhase[];
  summary: SkillAnalysisSummary;
  disclaimer?: string;
}

// -------------------- Phase 2: Learning Recommendations --------------------

export interface SkillRecommendationPreferences {
  free_only?: boolean;
  preferred_types?: string[];
  difficulty_preference?: "adaptive" | "beginner" | "intermediate" | "advanced";
}

export interface SkillRecommendRequest {
  target_role: string;
  skills: Record<string, number>;
  preferences?: SkillRecommendationPreferences;
}

export interface LearningResource {
  resource_id: string;
  resource_title: string;
  skill_id: string;
  skill_name: string;
  provider: string;
  resource_type: string;
  difficulty_level: "Beginner" | "Intermediate" | "Advanced";
  description: string;
  resource_url: string;
  estimated_hours: number;
  prerequisites: string;
  is_free: boolean;
  language: string;
  quality_score: number;
  tags: string;
  recommendation_score?: number;
  score_components?: {
    skill_priority_score: number;
    difficulty_match_score: number;
    resource_quality_score: number;
    relevance_score: number;
    free_resource_score: number;
  };
  why_recommended?: string[];
  recommended_rank?: number;
}

export interface RecommendedSkillGroup {
  skill_id: string;
  skill_name: string;
  priority_classification: string;
  priority_score: number;
  current_proficiency: number;
  required_proficiency: number;
  gap: number;
  resources: LearningResource[];
}

export interface LearningRoadmapResourceBrief {
  resource_id: string;
  resource_title: string;
  provider: string;
  resource_type: string;
  difficulty_level: string;
  estimated_hours: number;
  is_free: boolean;
  resource_url: string;
  recommendation_score?: number;
  why_recommended?: string[];
}

export interface LearningRoadmapSkillItem {
  skill_id: string;
  skill_name: string;
  current_proficiency: number;
  required_proficiency: number;
  gap: number;
  priority: string;
  importance_weight: number;
  priority_score: number;
  recommended_resources: LearningRoadmapResourceBrief[];
  recommended_sequence: {
    step: number;
    resource_id: string;
    resource_title: string;
    difficulty_level: string;
    resource_type: string;
  }[];
  reason_for_prioritization: string;
  estimated_resource_hours: number;
}

export interface LearningRoadmapStage {
  stage: "immediate_focus" | "skill_development" | "strengthening_skills" | "maintain_strengths";
  title: string;
  description: string;
  skill_count: number;
  estimated_stage_hours: number;
  skills: LearningRoadmapSkillItem[];
}

export interface RecommendationSummary {
  priority_skills_covered: number;
  total_recommended_resources: number;
  free_resources_recommended: number;
  estimated_total_learning_hours: number;
  maintenance_resources_count?: number;
  maintenance_estimated_hours?: number;
  maintenance_free_resources?: number;
  top_skill_to_focus: string | null;
}

export interface SkillRecommendResponse {
  target_role: string;
  role_name: string;
  overall_readiness_score: number;
  readiness_score_interpretation?: string;
  priority_skills: SkillComparisonItem[];
  recommended_resources_by_skill: RecommendedSkillGroup[];
  recommendation_ranking?: Record<string, any>;
  learning_roadmap: LearningRoadmapStage[];
  recommendation_summary: RecommendationSummary;
  preferences_applied?: SkillRecommendationPreferences;
  analysis_summary?: SkillAnalysisSummary;
  dataset_disclosure?: Record<string, string>;
}

export interface SkillResourcesResponse {
  resources: LearningResource[];
  count: number;
  filters_applied?: Record<string, any>;
  disclosure?: string;
}

export interface SkillResourcesSummaryResponse {
  total_resources: number;
  total_covered_skills: number;
  resource_counts_by_difficulty: Record<string, number>;
  resource_counts_by_type: Record<string, number>;
  free_vs_paid: { free: number; paid: number };
  provider_distribution: Record<string, number>;
  disclosure?: string;
}

// -------------------- Phase 3: Student Segmentation --------------------

export interface SegmentationRoleSummary {
  role_id: string;
  role_name: string;
  available: boolean;
  selected_k?: number;
  n_samples_trained?: number;
  n_features?: number;
  algorithm?: string;
}

export interface SegmentationRolesResponse {
  roles: SegmentationRoleSummary[];
  count: number;
  disclosure?: string;
}

export interface SegmentationClusterDistributionItem {
  cluster_id: number;
  cluster_name: string;
  student_count: number;
  student_percentage: number;
}

export interface SegmentationOverviewResponse {
  role_id: string;
  role_name: string;
  n_clusters: number;
  students_analyzed: number;
  cluster_distribution: SegmentationClusterDistributionItem[];
  selected_k: number;
  clustering_evaluation_metrics: {
    silhouette_score?: number | null;
    davies_bouldin_score?: number | null;
    calinski_harabasz_score?: number | null;
    wcss?: number | null;
  };
  candidate_k_metrics?: Array<Record<string, any>>;
  k_selection?: Record<string, any>;
  overall_clustering_summary?: Record<string, any>;
  disclosure?: string;
}

export interface SegmentationSkillDelta {
  skill_name: string;
  cluster_average: number;
  overall_average?: number;
  difference_from_overall?: number;
}

export interface SegmentationClusterProfile {
  cluster_id: number;
  cluster_name: string;
  cluster_description: string;
  student_count: number;
  student_percentage: number;
  average_skill_proficiency: number;
  difference_from_overall_role_average?: number;
  average_proficiency_per_skill: Record<string, number>;
  skill_profile_vs_requirements?: Array<Record<string, any>>;
  strongest_skills: SegmentationSkillDelta[];
  weakest_skills: SegmentationSkillDelta[];
  category_profile?: Array<Record<string, any>>;
}

export interface SegmentationClustersResponse {
  role_id: string;
  role_name: string;
  selected_k: number;
  students_analyzed: number;
  clusters: SegmentationClusterProfile[];
  disclosure?: string;
}

export interface SegmentationPredictRequest {
  target_role: string;
  skills: Record<string, number>;
}

export interface SegmentationComparisonItem {
  skill_id?: string;
  skill_name: string;
  skill_category?: string;
  is_core_skill?: boolean;
  student_proficiency: number;
  cluster_average: number;
  overall_role_average?: number;
  required_proficiency?: number;
  difference_from_cluster: number;
  difference_from_overall?: number;
}

export interface SegmentationPredictResponse {
  target_role: string;
  role_name: string;
  predicted_cluster_id: number;
  cluster_name: string;
  cluster_description: string;
  cluster_characteristics: Record<string, any>;
  student_strongest_skills: SegmentationComparisonItem[] | Array<Record<string, any>>;
  student_weakest_skills: SegmentationComparisonItem[] | Array<Record<string, any>>;
  comparison_with_cluster: SegmentationComparisonItem[];
  recommended_areas_of_improvement: Array<Record<string, any>>;
  why_this_cluster?: string[];
  personal_skill_gaps?: Record<string, any>;
  cluster_level_weaknesses?: Record<string, any>;
  recommendations_based_on_individual_gaps?: Record<string, any> | null;
  recommendations_based_on_cluster_patterns?: Record<string, any> | null;
  integration_notes?: Record<string, any>;
  disclosure?: string;
}

export interface SegmentationModelInfoResponse {
  role_id: string;
  role_name: string;
  model_type: string;
  selected_k: number;
  training_sample_count: number;
  feature_count: number;
  feature_names: string[];
  training_metadata: Record<string, any>;
  evaluation_metrics: Record<string, any>;
  candidate_k_metrics?: Array<Record<string, any>>;
  disclosure?: string;
}
