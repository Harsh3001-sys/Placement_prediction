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
} from "../types/placement";

const RAW_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
const API_BASE_URL = RAW_BASE_URL.endsWith("/")
  ? RAW_BASE_URL.slice(0, -1)
  : RAW_BASE_URL;

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
    // Network / offline error
    throw new ApiClientError(
      "Unable to communicate with the prediction server. Please verify the backend API is reachable and CORS/API base URL are configured correctly.",
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
};
