import { useState, useEffect, useCallback } from "react";
import { apiService } from "../services/api";
import type { HealthResponse } from "../types/placement";

export type ConnectionStatus = "connected" | "checking" | "disconnected";

export function useApiHealth() {
  const [status, setStatus] = useState<ConnectionStatus>("checking");
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkHealth = useCallback(async () => {
    setStatus("checking");
    try {
      const data = await apiService.getHealth();
      setHealthData(data);
      if (data.status === "healthy" && data.model_loaded) {
        setStatus("connected");
      } else {
        setStatus("disconnected");
      }
    } catch {
      setHealthData(null);
      setStatus("disconnected");
    } finally {
      setLastChecked(new Date());
    }
  }, []);

  useEffect(() => {
    checkHealth();
    // Re-check periodically every 45 seconds
    const interval = setInterval(checkHealth, 45000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    status,
    healthData,
    lastChecked,
    refreshHealth: checkHealth,
  };
}
