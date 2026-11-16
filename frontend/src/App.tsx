import React, { useState } from "react";
import type { PageView } from "./types/placement";
import { useApiHealth } from "./hooks/useApiHealth";
import { Sidebar } from "./components/Sidebar";
import { TopNav } from "./components/TopNav";
import { OverviewPage } from "./pages/OverviewPage";
import { PredictorPage } from "./pages/PredictorPage";
import { PPOPredictorPage } from "./pages/PPOPredictorPage";
import { ModelInsightsPage } from "./pages/ModelInsightsPage";
import { AboutPage } from "./pages/AboutPage";
import { ApiStatusPage } from "./pages/ApiStatusPage";

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<PageView>("overview");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { status: apiStatus, refreshHealth } = useApiHealth();

  return (
    <div className="flex min-h-screen bg-[#F6F3ED] text-[#202B38]">
      {/* Sidebar Navigation */}
      <Sidebar
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        apiStatus={apiStatus}
        onRefreshHealth={refreshHealth}
        isOpenMobile={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Workspace */}
      <div className="flex flex-1 flex-col min-w-0">
        <TopNav
          currentPage={currentPage}
          apiStatus={apiStatus}
          onOpenMobile={() => setIsMobileMenuOpen(true)}
        />

        {/* Content Viewport */}
        <main className="flex-1 p-6 sm:p-8 lg:p-10 max-w-7xl w-full mx-auto">
          {currentPage === "overview" && (
            <OverviewPage onNavigate={(page) => setCurrentPage(page)} />
          )}

          {currentPage === "predictor" && (
            <PredictorPage
              apiStatus={apiStatus}
              onRefreshHealth={refreshHealth}
            />
          )}

          {currentPage === "ppo-predictor" && <PPOPredictorPage />}

          {currentPage === "model-insights" && <ModelInsightsPage />}

          {currentPage === "about" && <AboutPage />}

          {currentPage === "api-status" && <ApiStatusPage />}
        </main>

        {/* Editorial Footer */}
        <footer className="border-t border-[#E4E1DA] bg-white py-6 px-6 text-center text-xs text-[#738091]">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-[#202B38]">CareerLens</span>
              <span>—</span>
              <span>Student Intelligence Platform</span>
            </div>
            <div className="flex items-center gap-4 text-[11px]">
              <span>Placement + PPO Prediction</span>
              <span>·</span>
              <span>Independent ML Pipelines</span>
              <span>·</span>
              <span>Flask + React</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default App;
