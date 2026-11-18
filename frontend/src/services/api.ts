/**
 * Dedicated API Service Module for CareerLens.
 * Interacts with the Python Flask REST API with strong typing and error handling.
 */
import type {
  StudentFormData,
  PredictionResponse,
  HealthResponse,
  ModelInfoResponse,
  ApiErrorResponse,
  PPOFormData,
  PPOPredictionResponse,
  PPOHealthResponse,
  PPOModelInfoResponse,
  SkillRolesResponse,
  SkillRequirementsResponse,
  SkillMetadataResponse,
  SkillAnalysisRequest,
  SkillAnalysisResponse,
  SkillRecommendRequest,
  SkillRecommendResponse,
  SkillResourcesResponse,
  SkillResourcesSummaryResponse,
  SegmentationRolesResponse,
  SegmentationOverviewResponse,
  SegmentationClustersResponse,
  SegmentationPredictRequest,
  SegmentationPredictResponse,
  SegmentationModelInfoResponse,
} from "../types/placement";

function normalizeApiBaseUrl(raw: string): string {
  let base = (raw || "/api").trim().replace(/\/+$/, "");
  if (!base) base = "/api";

  // If a full backend origin/URL is provided without an /api path, append /api once
  // so requests like /health resolve to /api/health (the Flask blueprint prefix).
  try {
    const parsed = new URL(base);
    const path = parsed.pathname.replace(/\/+$/, "");
    if (path === "" || path === "/") {
      parsed.pathname = "/api";
      base = parsed.toString().replace(/\/+$/, "");
    } else {
      base = `${parsed.origin}${path}`;
    }
  } catch {
    // Relative base (e.g. /api) - keep as-is
  }

  return base;
}

const RAW_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) || "/api";
export const API_BASE_URL = normalizeApiBaseUrl(RAW_BASE_URL);

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export function isLocalBackendUrl(url: string = API_BASE_URL): boolean {
  return /^(?:\/api$|https?:\/\/(?:127\.0\.0\.1|localhost)(?::\d+)?(?:\/|$))/i.test(url);
}

export class ApiClientError extends Error {
  status: number;
  details?: string[];

  constructor(message: string, status: number = 500, details?: string[]) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.details = details;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...options.headers,
  };

  try {
    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
      let errorBody: ApiErrorResponse | null = null;
      try {
        errorBody = await response.json();
      } catch {
        // Response was not JSON
      }

      const errorMessage =
        errorBody?.message ||
        errorBody?.error ||
        `Request failed with status code ${response.status} (${response.statusText})`;

      throw new ApiClientError(errorMessage, response.status, errorBody?.details);
    }

    return (await response.json()) as T;
  } catch (err: any) {
    if (err instanceof ApiClientError) {
      throw err;
    }
    const local = isLocalBackendUrl();
    throw new ApiClientError(
      local
        ? "Unable to communicate with the local backend API. Please verify the Flask server is running and the API base URL is configured correctly."
        : "Unable to communicate with the backend API. The server may be unavailable or waking up (Render free services can take up to a minute). Please try again shortly and verify the configured backend URL/CORS settings.",
      0
    );
  }
}

export const apiService = {
  /**
   * Health check endpoint to verify placement backend process and model readiness.
   */
  async getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>("/health");
  },

  /**
   * Submit student profile features and return deterministic inference results.
   */
  async predictPlacement(profile: StudentFormData): Promise<PredictionResponse> {
    return request<PredictionResponse>("/predict", {
      method: "POST",
      body: JSON.stringify(profile),
    });
  },

  /**
   * Retrieve model architecture, canonical test metrics, confusion matrix, and coefficients.
   */
  async getModelInfo(): Promise<ModelInfoResponse> {
    return request<ModelInfoResponse>("/model/info");
  },

  /**
   * Independent PPO health check.
   */
  async getPPOHealth(): Promise<PPOHealthResponse> {
    return request<PPOHealthResponse>("/ppo/health");
  },

  /**
   * Independent PPO prediction.
   */
  async predictPPO(profile: PPOFormData): Promise<PPOPredictionResponse> {
    return request<PPOPredictionResponse>("/ppo/predict", {
      method: "POST",
      body: JSON.stringify(profile),
    });
  },

  /**
   * Independent PPO model info.
   */
  async getPPOModelInfo(): Promise<PPOModelInfoResponse> {
    return request<PPOModelInfoResponse>("/ppo/info");
  },

  async getSkillRoles(): Promise<SkillRolesResponse> {
    return request<SkillRolesResponse>("/skills/roles");
  },

  async getSkillRequirements(roleId: string): Promise<SkillRequirementsResponse> {
    return request<SkillRequirementsResponse>(`/skills/requirements/${encodeURIComponent(roleId)}`);
  },

  async getSkillMetadata(): Promise<SkillMetadataResponse> {
    return request<SkillMetadataResponse>("/skills/metadata");
  },

  async analyzeSkillGap(payload: SkillAnalysisRequest): Promise<SkillAnalysisResponse> {
    return request<SkillAnalysisResponse>("/skills/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getSkillResources(params?: {
    skill_id?: string;
    difficulty?: string;
    resource_type?: string;
    free_only?: boolean;
    provider?: string;
  }): Promise<SkillResourcesResponse> {
    const q = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v === undefined || v === null || v === "") return;
        q.set(k, String(v));
      });
    }
    const qs = q.toString();
    return request<SkillResourcesResponse>(`/skills/resources${qs ? `?${qs}` : ""}`);
  },

  async getSkillResourcesSummary(): Promise<SkillResourcesSummaryResponse> {
    return request<SkillResourcesSummaryResponse>("/skills/resources/summary");
  },

  async recommendSkills(payload: SkillRecommendRequest): Promise<SkillRecommendResponse> {
    return request<SkillRecommendResponse>("/skills/recommend", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  // Phase 3: Student Segmentation
  async getSegmentationRoles(): Promise<SegmentationRolesResponse> {
    return request<SegmentationRolesResponse>("/segmentation/roles");
  },

  async getSegmentationOverview(roleId: string): Promise<SegmentationOverviewResponse> {
    return request<SegmentationOverviewResponse>(`/segmentation/overview/${encodeURIComponent(roleId)}`);
  },

  async getSegmentationClusters(roleId: string): Promise<SegmentationClustersResponse> {
    return request<SegmentationClustersResponse>(`/segmentation/clusters/${roleId ? encodeURIComponent(roleId) : ""}`);
  },

  async predictStudentSegment(payload: SegmentationPredictRequest): Promise<SegmentationPredictResponse> {
    return request<SegmentationPredictResponse>("/segmentation/predict", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getSegmentationModelInfo(roleId: string): Promise<SegmentationModelInfoResponse> {
    return request<SegmentationModelInfoResponse>(`/segmentation/model-info/${encodeURIComponent(roleId)}`);
  },
};
