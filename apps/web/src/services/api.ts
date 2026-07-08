const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface HealthStatus {
  status: string;
  timestamp: string;
  environment: string;
  version: string;
}

export interface VersionInfo {
  name: string;
  version: string;
  api_prefix: string;
  environment: string;
}

async function apiFetch<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthStatus> {
  return apiFetch<HealthStatus>("/api/v1/health");
}

export async function fetchVersion(): Promise<VersionInfo> {
  return apiFetch<VersionInfo>("/api/v1/version");
}
