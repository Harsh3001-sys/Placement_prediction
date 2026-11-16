import React from "react";
import {
  Code2,
  Terminal,
  Shield,
  Layers,
  GraduationCap,
  Cpu,
  FileText,
} from "lucide-react";

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="border-b border-[#E4E1DA] pb-5">
        <div className="inline-flex items-center gap-2 rounded-full border border-[#C6A66B]/30 bg-[#F7F3E9] px-3 py-1 text-xs font-semibold text-[#9A7B3E] mb-2">
          <span>CAPSTONE SPECIFICATION</span>
        </div>
        <h1 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-[#202B38]">
          About CareerLens
        </h1>
        <p className="mt-1 text-sm text-[#738091] max-w-3xl leading-relaxed">
          Project background, system architecture, engineering standards, and algorithmic ethics documentation.
        </p>
      </div>

      {/* Project Overview */}
      <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex items-center gap-2 border-b border-[#E4E1DA] pb-4 mb-5">
          <GraduationCap className="h-5 w-5 text-[#3D827C]" />
          <h2 className="font-heading text-base font-bold text-[#202B38]">
            Academic Purpose & Context
          </h2>
        </div>

        <div className="text-xs text-[#738091] space-y-3 leading-relaxed">
          <p>
            <strong>CareerLens</strong> was conceived as a comprehensive Machine Learning Capstone (CP) project to bridge statistical classification techniques with modern software engineering practices. Campus recruitment drives are critical milestones for higher education institutions; identifying key preparedness factors enables academic mentors to offer targeted interventions and career coaching.
          </p>
          <p>
            Unlike naive heuristic screening tools, CareerLens combines 13 multidimensional attributes—spanning standardized aptitude benchmarks, formal coursework grades (SSC, HSC, CGPA), practical project portfolios, and extracurricular leadership—into an empirical, mathematically validated classification pipeline.
          </p>
        </div>
      </div>

      {/* Architecture Overview */}
      <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex items-center gap-2 border-b border-[#E4E1DA] pb-4 mb-6">
          <Layers className="h-5 w-5 text-[#3D827C]" />
          <h2 className="font-heading text-base font-bold text-[#202B38]">
            Full-Stack System Architecture
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
          {/* Client layer */}
          <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-5 space-y-3">
            <div className="flex items-center gap-2 font-bold text-[#202B38]">
              <Code2 className="h-4 w-4 text-[#3D827C]" />
              <span>Frontend Client</span>
            </div>
            <ul className="space-y-1.5 text-[#738091]">
              <li>• <strong>React 19 & TypeScript:</strong> Type-safe component architecture.</li>
              <li>• <strong>Tailwind CSS v4:</strong> Editorial design system with custom palette.</li>
              <li>• <strong>React Hook Form & Zod:</strong> Client-side schema constraints.</li>
              <li>• <strong>Recharts:</strong> Authentic ROC curve & confusion matrix visualizations.</li>
            </ul>
          </div>

          {/* API layer */}
          <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-5 space-y-3">
            <div className="flex items-center gap-2 font-bold text-[#202B38]">
              <Terminal className="h-4 w-4 text-[#3D827C]" />
              <span>Backend REST API</span>
            </div>
            <ul className="space-y-1.5 text-[#738091]">
              <li>• <strong>Python Flask:</strong> Application factory architecture.</li>
              <li>• <strong>Flask-CORS:</strong> Explicit origin whitelisting.</li>
              <li>• <strong>Strict Schemas:</strong> Defense against missing, NaN, or non-finite inputs.</li>
              <li>• <strong>Pytest:</strong> Comprehensive test suite covering 14 critical cases.</li>
            </ul>
          </div>

          {/* Model layer */}
          <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-5 space-y-3">
            <div className="flex items-center gap-2 font-bold text-[#202B38]">
              <Cpu className="h-4 w-4 text-[#3D827C]" />
              <span>ML Inference Engine</span>
            </div>
            <ul className="space-y-1.5 text-[#738091]">
              <li>• <strong>scikit-learn 1.6+:</strong> Serialized pipeline artifact.</li>
              <li>• <strong>StandardScaler:</strong> Zero-mean unit-variance transformation.</li>
              <li>• <strong>Logistic Regression:</strong> L2 penalized liblinear solver (C=5.0).</li>
              <li>• <strong>Deterministic Probabilities:</strong> Predicts continuous log-odds.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Feature Specification Table */}
      <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex items-center gap-2 border-b border-[#E4E1DA] pb-4 mb-4">
          <FileText className="h-5 w-5 text-[#3D827C]" />
          <h2 className="font-heading text-base font-bold text-[#202B38]">
            Complete Feature Specification (13 Parameters)
          </h2>
        </div>

        <div className="overflow-x-auto text-xs">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#E4E1DA] bg-[#F6F3ED] text-[#202B38]">
                <th className="py-2.5 px-3 font-semibold">Feature Name</th>
                <th className="py-2.5 px-3 font-semibold">Category</th>
                <th className="py-2.5 px-3 font-semibold">Accepted Range</th>
                <th className="py-2.5 px-3 font-semibold">Coefficient</th>
                <th className="py-2.5 px-3 font-semibold">Dataset Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#ECE9E2] text-[#738091]">
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">AptitudeTestScore</td>
                <td className="py-2.5 px-3">Academic</td>
                <td className="py-2.5 px-3">0 – 100</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#3D827C]">+0.6137</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">PlacementTraining</td>
                <td className="py-2.5 px-3">Preparation</td>
                <td className="py-2.5 px-3">Yes / No</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#3D827C]">+0.3917</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">ExtracurricularActivities</td>
                <td className="py-2.5 px-3">Experience</td>
                <td className="py-2.5 px-3">Yes / No</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#3D827C]">+0.3682</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">SSC_Marks</td>
                <td className="py-2.5 px-3">Academic</td>
                <td className="py-2.5 px-3">0 – 100%</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#3D827C]">+0.2813</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">Projects</td>
                <td className="py-2.5 px-3">Experience</td>
                <td className="py-2.5 px-3">0 – 15</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#3D827C]">+0.2638</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">SoftSkillsRating</td>
                <td className="py-2.5 px-3">Academic</td>
                <td className="py-2.5 px-3">0.0 – 5.0</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#3D827C]">+0.2635</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">CGPA</td>
                <td className="py-2.5 px-3">Academic</td>
                <td className="py-2.5 px-3">0.0 – 10.0</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#3D827C]">+0.2563</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">HSC_Marks</td>
                <td className="py-2.5 px-3">Academic</td>
                <td className="py-2.5 px-3">0 – 100%</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#3D827C]">+0.2220</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">Workshops/Certifications</td>
                <td className="py-2.5 px-3">Preparation</td>
                <td className="py-2.5 px-3">0 – 15</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#3D827C]">+0.0968</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">Publications</td>
                <td className="py-2.5 px-3">Technical</td>
                <td className="py-2.5 px-3">0 – 4</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#9A7B3E]">+0.0407</td>
                <td className="py-2.5 px-3"><span className="text-[#9A7B3E] font-medium bg-[#F7F3E9] px-1.5 py-0.5 rounded">Synthetic</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">Internships</td>
                <td className="py-2.5 px-3">Experience</td>
                <td className="py-2.5 px-3">0 – 10</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-slate-500">-0.0102</td>
                <td className="py-2.5 px-3"><span className="text-emerald-700 font-medium">Original</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">LeetCode_Problems_Solved</td>
                <td className="py-2.5 px-3">Technical</td>
                <td className="py-2.5 px-3">0 – 500</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#9A7B3E]">-0.0143</td>
                <td className="py-2.5 px-3"><span className="text-[#9A7B3E] font-medium bg-[#F7F3E9] px-1.5 py-0.5 rounded">Synthetic</span></td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-medium text-[#202B38]">Hackathon_Wins</td>
                <td className="py-2.5 px-3">Technical</td>
                <td className="py-2.5 px-3">0 – 5</td>
                <td className="py-2.5 px-3 font-mono font-semibold text-[#9A7B3E]">-0.0408</td>
                <td className="py-2.5 px-3"><span className="text-[#9A7B3E] font-medium bg-[#F7F3E9] px-1.5 py-0.5 rounded">Synthetic</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Ethical Considerations */}
      <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex items-center gap-2 border-b border-[#E4E1DA] pb-4 mb-4">
          <Shield className="h-5 w-5 text-[#3D827C]" />
          <h2 className="font-heading text-base font-bold text-[#202B38]">
            Ethical Governance in Algorithmic Placement Screening
          </h2>
        </div>

        <div className="text-xs text-[#738091] space-y-3 leading-relaxed">
          <p>
            When utilizing machine learning models within academic institutions, transparent governance is vital to prevent unfair algorithmic screening. Placement models must serve as <strong>supportive diagnostic tools</strong> rather than punitive gatekeepers.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div className="rounded-lg bg-[#FBF9F5] p-3.5 border border-[#E4E1DA]">
              <strong className="text-[#202B38] block mb-1">Constructive Guidance Principle</strong>
              <span>
                Predictions should be interpreted by mentors to identify skill deficits early (such as lack of placement preparation or lower aptitude scores) so tailored support can be provided.
              </span>
            </div>
            <div className="rounded-lg bg-[#FBF9F5] p-3.5 border border-[#E4E1DA]">
              <strong className="text-[#202B38] block mb-1">Human-in-the-Loop Safeguard</strong>
              <span>
                Automated models should never disqualify a student from sitting for campus interviews. Final placement opportunity access must remain equitable and human-reviewed.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
