import { useEffect, useState } from "react";
import { fetchHealth, fetchVersion, HealthStatus, VersionInfo } from "../services/api";

function Dashboard(): JSX.Element {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [version, setVersion] = useState<VersionInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStatus(): Promise<void> {
      try {
        const [healthData, versionData] = await Promise.all([
          fetchHealth(),
          fetchVersion(),
        ]);
        setHealth(healthData);
        setVersion(versionData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to connect to API");
      } finally {
        setLoading(false);
      }
    }

    void loadStatus();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-700">
        <h2 className="text-lg font-semibold mb-2">Connection Error</h2>
        <p>{error}</p>
        <p className="mt-2 text-sm">Ensure the API server is running on port 8000.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard</h2>
        <p className="text-gray-600">
          Welcome to ITcopilot — your AI-powered income tax assistant for India.
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatusCard
          title="API Status"
          value={health?.status ?? "unknown"}
          subtitle={`Environment: ${health?.environment ?? "N/A"}`}
          status={health?.status === "healthy" ? "success" : "error"}
        />
        <StatusCard
          title="Version"
          value={version?.version ?? "N/A"}
          subtitle={version?.name ?? "ITcopilot"}
          status="info"
        />
        <StatusCard
          title="Assessment Year"
          value="2025-26"
          subtitle="Current AY support"
          status="info"
        />
      </div>

      <section className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <ActionButton label="Compute Tax" description="Calculate income tax liability" />
          <ActionButton label="Import Broker" description="Import trade statements" />
          <ActionButton label="Generate Report" description="Create ITR summary report" />
          <ActionButton label="View Assessments" description="Browse saved assessments" />
        </div>
      </section>
    </div>
  );
}

interface StatusCardProps {
  title: string;
  value: string;
  subtitle: string;
  status: "success" | "error" | "info";
}

function StatusCard({ title, value, subtitle, status }: StatusCardProps): JSX.Element {
  const statusColors = {
    success: "border-green-200 bg-green-50",
    error: "border-red-200 bg-red-50",
    info: "border-primary-100 bg-primary-50",
  };

  return (
    <div className={`rounded-xl border p-6 ${statusColors[status]}`}>
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <p className="text-2xl font-bold mt-1 capitalize">{value}</p>
      <p className="text-xs text-gray-500 mt-2">{subtitle}</p>
    </div>
  );
}

interface ActionButtonProps {
  label: string;
  description: string;
}

function ActionButton({ label, description }: ActionButtonProps): JSX.Element {
  return (
    <button
      type="button"
      className="text-left p-4 rounded-lg border border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-colors"
    >
      <p className="font-medium text-gray-900">{label}</p>
      <p className="text-sm text-gray-500 mt-1">{description}</p>
    </button>
  );
}

export default Dashboard;
