"""
Reproducible generator for CareerLens Skill Gap Analysis (Phase 1) synthetic datasets.

Generates:
- backend/datasets/role_skill_requirements.csv
- backend/datasets/skill_metadata.csv
- backend/datasets/student_skill_profiles.csv

Notes:
- Data is synthetic and illustrative for demonstration/testing only.
- Role requirements are benchmark-like assumptions, not verified industry standards.
- Student profiles are synthetic and not real student records or ground truth.
"""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

SEED = 42
N_STUDENTS = 1000

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "backend" / "datasets"


@dataclass(frozen=True)
class RoleDef:
    role_id: str
    role_name: str
    description: str
    # (skill_id, required_proficiency, raw_importance, is_core_skill)
    skills: List[Tuple[str, float, float, bool]]


# Canonical skill catalog (consistent IDs across all datasets)
SKILLS: Dict[str, Dict[str, str]] = {
    "java": {
        "skill_name": "Java",
        "skill_category": "Programming Languages",
        "description": "Object-oriented programming language widely used for enterprise, backend, and Android development.",
        "beginner_description": "Understands basic syntax, variables, loops, and simple classes.",
        "intermediate_description": "Can build multi-class applications, use collections, exceptions, and common libraries.",
        "advanced_description": "Designs robust, performant systems using concurrency, JVM concepts, and strong OOP design.",
    },
    "python": {
        "skill_name": "Python",
        "skill_category": "Programming Languages",
        "description": "High-level language used for scripting, backend services, automation, and data/ML work.",
        "beginner_description": "Can write scripts using basic syntax, data types, and control flow.",
        "intermediate_description": "Uses functions, modules, virtual environments, and common libraries effectively.",
        "advanced_description": "Builds maintainable packages/services and applies Pythonic patterns for complex problems.",
    },
    "cpp": {
        "skill_name": "C++",
        "skill_category": "Programming Languages",
        "description": "Performance-oriented language emphasizing memory management and systems-level programming.",
        "beginner_description": "Understands syntax, pointers basics, and simple data structures.",
        "intermediate_description": "Uses STL, memory management concepts, and object-oriented features correctly.",
        "advanced_description": "Applies templates, performance optimization, and safe modern C++ practices.",
    },
    "javascript": {
        "skill_name": "JavaScript",
        "skill_category": "Programming Languages",
        "description": "Core language of the web used for interactive frontend and server-side development.",
        "beginner_description": "Can manipulate basic DOM behavior and write simple scripts/functions.",
        "intermediate_description": "Uses ES6+ features, async patterns, and modular code organization.",
        "advanced_description": "Builds scalable client/server applications with strong debugging and performance awareness.",
    },
    "dsa": {
        "skill_name": "Data Structures and Algorithms",
        "skill_category": "Computer Science Fundamentals",
        "description": "Techniques for organizing data and solving computational problems efficiently.",
        "beginner_description": "Knows arrays, strings, basic searching/sorting, and simple complexity ideas.",
        "intermediate_description": "Applies trees, graphs, hashing, and common algorithmic patterns to problems.",
        "advanced_description": "Selects and optimizes complex algorithms with strong time/space tradeoff reasoning.",
    },
    "oop": {
        "skill_name": "Object-Oriented Programming",
        "skill_category": "Computer Science Fundamentals",
        "description": "Design paradigm using classes and objects to model systems with encapsulation and abstraction.",
        "beginner_description": "Understands classes, objects, and basic inheritance concepts.",
        "intermediate_description": "Applies SOLID-like thinking, abstractions, and reusable design pattern basics.",
        "advanced_description": "Designs extensible, testable object models for complex software systems.",
    },
    "dbms": {
        "skill_name": "DBMS",
        "skill_category": "Databases",
        "description": "Principles of database systems including modeling, indexing, transactions, and normalization.",
        "beginner_description": "Understands tables, keys, and basic CRUD concepts.",
        "intermediate_description": "Can design normalized schemas and reason about indexing/transactions.",
        "advanced_description": "Optimizes queries/schemas and understands consistency, concurrency, and performance tradeoffs.",
    },
    "sql": {
        "skill_name": "SQL",
        "skill_category": "Databases",
        "description": "Language for querying and manipulating relational databases.",
        "beginner_description": "Writes basic SELECT/WHERE/JOIN queries.",
        "intermediate_description": "Uses aggregations, subqueries, joins, and indexing-aware query patterns.",
        "advanced_description": "Optimizes complex analytical queries and understands execution behavior.",
    },
    "computer_networks": {
        "skill_name": "Computer Networks",
        "skill_category": "Computer Science Fundamentals",
        "description": "Concepts of data communication including protocols, routing, HTTP, and network layers.",
        "beginner_description": "Understands IP, DNS, HTTP basics, and client-server communication.",
        "intermediate_description": "Can reason about TCP/UDP, latency, APIs over networks, and common debugging.",
        "advanced_description": "Understands performance, security implications, and distributed communication tradeoffs.",
    },
    "operating_systems": {
        "skill_name": "Operating Systems",
        "skill_category": "Computer Science Fundamentals",
        "description": "Core OS concepts such as processes, threads, memory, scheduling, and file systems.",
        "beginner_description": "Knows processes, memory basics, and file system concepts.",
        "intermediate_description": "Understands concurrency, synchronization, and resource management fundamentals.",
        "advanced_description": "Applies OS concepts to performance/debugging of real systems.",
    },
    "html": {
        "skill_name": "HTML",
        "skill_category": "Frontend",
        "description": "Markup language for structuring content on the web.",
        "beginner_description": "Can create semantic page structures with common elements.",
        "intermediate_description": "Uses accessible, semantic markup and forms effectively.",
        "advanced_description": "Builds accessible, SEO-aware, maintainable document structures.",
    },
    "css": {
        "skill_name": "CSS",
        "skill_category": "Frontend",
        "description": "Styling language for layout, responsiveness, and visual presentation on the web.",
        "beginner_description": "Can style basic layouts, colors, and typography.",
        "intermediate_description": "Builds responsive layouts with Flexbox/Grid and component styling patterns.",
        "advanced_description": "Creates scalable design systems and optimizes UI consistency/performance.",
    },
    "react": {
        "skill_name": "React",
        "skill_category": "Frontend",
        "description": "JavaScript library for building component-based user interfaces.",
        "beginner_description": "Can build simple components with props and state.",
        "intermediate_description": "Manages hooks, forms, API integration, and component composition.",
        "advanced_description": "Designs performant, maintainable frontend architectures and state flows.",
    },
    "nodejs": {
        "skill_name": "Node.js",
        "skill_category": "Backend",
        "description": "JavaScript runtime for building server-side applications and APIs.",
        "beginner_description": "Can run scripts and build simple HTTP servers.",
        "intermediate_description": "Builds REST APIs, handles middleware, and manages async workflows.",
        "advanced_description": "Designs scalable backend services with robust error handling and performance practices.",
    },
    "expressjs": {
        "skill_name": "Express.js",
        "skill_category": "Backend",
        "description": "Minimal Node.js framework for building web servers and REST APIs.",
        "beginner_description": "Creates basic routes and handlers.",
        "intermediate_description": "Structures APIs with middleware, validation, and error handling.",
        "advanced_description": "Builds maintainable API layers with security/performance considerations.",
    },
    "mongodb": {
        "skill_name": "MongoDB",
        "skill_category": "Databases",
        "description": "Document-oriented NoSQL database used for flexible data storage.",
        "beginner_description": "Understands collections/documents and basic CRUD operations.",
        "intermediate_description": "Designs schemas, indexes, and aggregation queries for applications.",
        "advanced_description": "Optimizes data models and queries for scale and consistency needs.",
    },
    "rest_apis": {
        "skill_name": "REST APIs",
        "skill_category": "Backend",
        "description": "Design and consumption of HTTP-based APIs following REST principles.",
        "beginner_description": "Understands endpoints, HTTP methods, and JSON payloads.",
        "intermediate_description": "Designs and integrates consistent APIs with validation and status codes.",
        "advanced_description": "Builds robust, versionable API contracts with strong reliability practices.",
    },
    "git_github": {
        "skill_name": "Git and GitHub",
        "skill_category": "Tools & Collaboration",
        "description": "Version control and collaboration workflows for software development.",
        "beginner_description": "Can commit changes and use basic branching/push/pull workflows.",
        "intermediate_description": "Uses branching strategies, pull requests, and conflict resolution effectively.",
        "advanced_description": "Manages collaborative workflows, reviews, and repository hygiene at scale.",
    },
    "problem_solving": {
        "skill_name": "Problem Solving",
        "skill_category": "Professional Skills",
        "description": "Ability to analyze requirements, break down problems, and implement effective solutions.",
        "beginner_description": "Solves straightforward tasks with guidance and basic debugging.",
        "intermediate_description": "Independently decomposes problems and evaluates alternative approaches.",
        "advanced_description": "Tackles ambiguous, complex problems with strong analytical judgment.",
    },
    "statistics": {
        "skill_name": "Statistics",
        "skill_category": "Data & ML",
        "description": "Methods for summarizing data, inference, and understanding variability.",
        "beginner_description": "Understands mean/median/variance and basic distributions.",
        "intermediate_description": "Applies hypothesis testing, correlation, and statistical reasoning to datasets.",
        "advanced_description": "Selects appropriate statistical methods and interprets results rigorously.",
    },
    "probability": {
        "skill_name": "Probability",
        "skill_category": "Data & ML",
        "description": "Mathematical framework for modeling uncertainty and random events.",
        "beginner_description": "Understands basic probability rules and common events.",
        "intermediate_description": "Applies conditional probability and distributions to practical problems.",
        "advanced_description": "Uses probabilistic reasoning effectively in modeling and decision-making.",
    },
    "numpy": {
        "skill_name": "NumPy",
        "skill_category": "Data & ML",
        "description": "Python library for numerical computing with arrays and vectorized operations.",
        "beginner_description": "Creates arrays and performs basic numerical operations.",
        "intermediate_description": "Uses vectorization, broadcasting, and array manipulation efficiently.",
        "advanced_description": "Implements performant numerical workflows and integrates with ML pipelines.",
    },
    "pandas": {
        "skill_name": "Pandas",
        "skill_category": "Data & ML",
        "description": "Python library for data manipulation and analysis using tabular structures.",
        "beginner_description": "Loads data and performs basic filtering/selection.",
        "intermediate_description": "Cleans, transforms, groups, and merges datasets effectively.",
        "advanced_description": "Builds efficient, reproducible data preparation workflows.",
    },
    "matplotlib": {
        "skill_name": "Matplotlib",
        "skill_category": "Data & ML",
        "description": "Visualization library for creating static plots and charts in Python.",
        "beginner_description": "Creates basic line/bar charts.",
        "intermediate_description": "Customizes plots for clear exploratory analysis.",
        "advanced_description": "Builds publication-quality visualizations and reusable plotting utilities.",
    },
    "scikit_learn": {
        "skill_name": "Scikit-learn",
        "skill_category": "Data & ML",
        "description": "Machine learning library providing algorithms, preprocessing, and evaluation tools.",
        "beginner_description": "Trains simple models using standard APIs.",
        "intermediate_description": "Builds pipelines, tunes models, and evaluates performance correctly.",
        "advanced_description": "Designs robust ML workflows with careful validation and feature handling.",
    },
    "machine_learning": {
        "skill_name": "Machine Learning",
        "skill_category": "Data & ML",
        "description": "Building models that learn patterns from data for prediction or inference tasks.",
        "beginner_description": "Understands supervised learning basics and model evaluation concepts.",
        "intermediate_description": "Selects features/models and interprets results for practical problems.",
        "advanced_description": "Designs end-to-end ML solutions with strong evaluation and tradeoff awareness.",
    },
    "deep_learning": {
        "skill_name": "Deep Learning",
        "skill_category": "Data & ML",
        "description": "Neural-network-based learning methods for complex pattern recognition tasks.",
        "beginner_description": "Understands neural network basics and training concepts.",
        "intermediate_description": "Trains and tunes basic deep models with appropriate data/preprocessing.",
        "advanced_description": "Designs and optimizes deep architectures for real-world constraints.",
    },
    "tensorflow": {
        "skill_name": "TensorFlow",
        "skill_category": "Data & ML",
        "description": "Framework for building and deploying machine learning and deep learning models.",
        "beginner_description": "Can run basic model training examples.",
        "intermediate_description": "Builds and trains custom models with standard workflows.",
        "advanced_description": "Optimizes training/inference pipelines and manages model deployment concerns.",
    },
    "pytorch": {
        "skill_name": "PyTorch",
        "skill_category": "Data & ML",
        "description": "Deep learning framework known for dynamic computation graphs and research-friendly APIs.",
        "beginner_description": "Can define tensors and simple neural network modules.",
        "intermediate_description": "Implements training loops, datasets, and model experimentation workflows.",
        "advanced_description": "Builds efficient, customizable deep learning systems and experiments.",
    },
    "data_visualization": {
        "skill_name": "Data Visualization",
        "skill_category": "Data & ML",
        "description": "Communicating insights from data through effective charts and visual narratives.",
        "beginner_description": "Creates simple charts to show trends and comparisons.",
        "intermediate_description": "Chooses appropriate visuals and communicates findings clearly.",
        "advanced_description": "Designs insightful, audience-aware visual analytics narratives.",
    },
    "system_design": {
        "skill_name": "System Design",
        "skill_category": "Architecture",
        "description": "Designing scalable, reliable software systems and component interactions.",
        "beginner_description": "Understands basic client-server and component decomposition ideas.",
        "intermediate_description": "Can design APIs, data flows, and simple scalable architectures.",
        "advanced_description": "Reasons about tradeoffs in scalability, reliability, and maintainability.",
    },
    "communication": {
        "skill_name": "Communication",
        "skill_category": "Professional Skills",
        "description": "Ability to explain ideas clearly, collaborate, and document technical work effectively.",
        "beginner_description": "Communicates basic ideas and asks clarifying questions.",
        "intermediate_description": "Explains technical decisions clearly in team settings and documentation.",
        "advanced_description": "Influences technical direction through clear, audience-aware communication.",
    },
    "teamwork": {
        "skill_name": "Teamwork",
        "skill_category": "Professional Skills",
        "description": "Collaborating effectively with others to deliver shared outcomes.",
        "beginner_description": "Participates in group tasks and follows shared workflows.",
        "intermediate_description": "Collaborates proactively, supports peers, and handles feedback constructively.",
        "advanced_description": "Drives team alignment and contributes to healthy, productive collaboration.",
    },
}


def _s(skill_id: str, req: float, raw_importance: float, is_core: bool):
    if skill_id not in SKILLS:
        raise KeyError(f"Unknown skill_id: {skill_id}")
    return (skill_id, float(req), float(raw_importance), bool(is_core))


ROLES: List[RoleDef] = [
    RoleDef(
        role_id="software_developer",
        role_name="Software Developer",
        description="Builds and maintains general-purpose software applications with strong programming fundamentals.",
        skills=[
            _s("java", 75, 11, True),
            _s("python", 70, 9, True),
            _s("cpp", 55, 5, False),
            _s("dsa", 85, 14, True),
            _s("oop", 80, 12, True),
            _s("dbms", 70, 8, True),
            _s("sql", 65, 7, True),
            _s("computer_networks", 55, 5, False),
            _s("operating_systems", 60, 6, False),
            _s("git_github", 75, 8, True),
            _s("problem_solving", 85, 10, True),
            _s("communication", 65, 3, False),
            _s("teamwork", 65, 2, False),
        ],  # 13 skills
    ),
    RoleDef(
        role_id="backend_developer",
        role_name="Backend Developer",
        description="Designs and builds server-side APIs, business logic, and data-driven application services.",
        skills=[
            _s("java", 70, 8, True),
            _s("python", 70, 8, True),
            _s("javascript", 60, 5, False),
            _s("dsa", 75, 9, True),
            _s("oop", 75, 8, True),
            _s("dbms", 85, 10, True),
            _s("sql", 85, 10, True),
            _s("nodejs", 75, 8, True),
            _s("expressjs", 70, 6, False),
            _s("mongodb", 65, 5, False),
            _s("rest_apis", 85, 9, True),
            _s("git_github", 70, 5, True),
            _s("system_design", 60, 5, False),
            _s("problem_solving", 75, 4, True),
        ],  # 14 skills
    ),
    RoleDef(
        role_id="frontend_developer",
        role_name="Frontend Developer",
        description="Creates responsive, accessible, and interactive user interfaces for web applications.",
        skills=[
            _s("javascript", 85, 12, True),
            _s("html", 85, 10, True),
            _s("css", 85, 10, True),
            _s("react", 85, 14, True),
            _s("rest_apis", 70, 8, True),
            _s("git_github", 75, 7, True),
            _s("problem_solving", 75, 8, True),
            _s("oop", 55, 4, False),
            _s("dsa", 60, 5, False),
            _s("dbms", 40, 3, False),
            _s("sql", 35, 3, False),
            _s("communication", 70, 8, True),
            _s("teamwork", 70, 8, True),
        ],  # 13 skills
    ),
    RoleDef(
        role_id="full_stack_developer",
        role_name="Full Stack Developer",
        description="Works across frontend and backend layers to deliver complete web application features.",
        skills=[
            _s("javascript", 80, 10, True),
            _s("html", 75, 6, True),
            _s("css", 75, 6, True),
            _s("react", 80, 10, True),
            _s("nodejs", 75, 9, True),
            _s("expressjs", 70, 7, True),
            _s("mongodb", 65, 5, False),
            _s("sql", 70, 7, True),
            _s("dbms", 70, 6, True),
            _s("rest_apis", 80, 9, True),
            _s("git_github", 75, 6, True),
            _s("dsa", 70, 7, True),
            _s("oop", 65, 5, False),
            _s("problem_solving", 75, 5, True),
            _s("communication", 60, 2, False),
        ],  # 15 skills
    ),
    RoleDef(
        role_id="data_analyst",
        role_name="Data Analyst",
        description="Analyzes datasets to extract insights, build reports, and support data-driven decisions.",
        skills=[
            _s("python", 75, 10, True),
            _s("sql", 85, 14, True),
            _s("dbms", 70, 7, True),
            _s("statistics", 80, 12, True),
            _s("probability", 70, 8, True),
            _s("numpy", 70, 7, True),
            _s("pandas", 85, 12, True),
            _s("matplotlib", 75, 8, True),
            _s("data_visualization", 80, 10, True),
            _s("problem_solving", 75, 6, True),
            _s("communication", 75, 4, False),
            _s("git_github", 55, 2, False),
        ],  # 12 skills
    ),
    RoleDef(
        role_id="ml_engineer",
        role_name="Machine Learning Engineer",
        description="Develops, evaluates, and deploys machine learning models and data-driven intelligent systems.",
        skills=[
            _s("python", 85, 11, True),
            _s("statistics", 85, 10, True),
            _s("probability", 80, 8, True),
            _s("numpy", 80, 8, True),
            _s("pandas", 80, 8, True),
            _s("matplotlib", 65, 4, False),
            _s("scikit_learn", 80, 9, True),
            _s("machine_learning", 90, 14, True),
            _s("deep_learning", 75, 8, True),
            _s("tensorflow", 65, 5, False),
            _s("pytorch", 65, 5, False),
            _s("sql", 70, 5, True),
            _s("dsa", 70, 3, False),
            _s("problem_solving", 80, 2, True),
        ],  # 14 skills
    ),
]


# Positive correlations to create logical relationships between related skills
CORR_GROUPS = {
    "java": ["oop", "dsa", "problem_solving"],
    "python": ["numpy", "pandas", "problem_solving", "machine_learning"],
    "cpp": ["dsa", "oop"],
    "javascript": ["react", "nodejs", "html", "css", "rest_apis"],
    "dsa": ["problem_solving", "java", "cpp", "python"],
    "oop": ["java", "cpp", "system_design"],
    "dbms": ["sql", "mongodb"],
    "sql": ["dbms", "pandas", "data_visualization"],
    "html": ["css", "react", "javascript"],
    "css": ["html", "react", "javascript"],
    "react": ["javascript", "html", "css", "rest_apis"],
    "nodejs": ["expressjs", "rest_apis", "javascript", "mongodb"],
    "expressjs": ["nodejs", "rest_apis"],
    "mongodb": ["dbms", "nodejs", "rest_apis"],
    "rest_apis": ["nodejs", "expressjs", "react", "system_design"],
    "statistics": ["probability", "machine_learning", "pandas", "numpy"],
    "probability": ["statistics", "machine_learning"],
    "numpy": ["pandas", "scikit_learn", "machine_learning", "python"],
    "pandas": ["numpy", "data_visualization", "matplotlib", "python", "sql"],
    "matplotlib": ["data_visualization", "pandas", "numpy"],
    "scikit_learn": ["machine_learning", "numpy", "pandas", "python"],
    "machine_learning": ["scikit_learn", "deep_learning", "statistics", "probability", "python"],
    "deep_learning": ["tensorflow", "pytorch", "machine_learning"],
    "tensorflow": ["deep_learning", "pytorch"],
    "pytorch": ["deep_learning", "tensorflow"],
    "data_visualization": ["matplotlib", "pandas", "communication"],
    "system_design": ["rest_apis", "dbms", "oop"],
    "communication": ["teamwork", "data_visualization"],
    "teamwork": ["communication", "problem_solving"],
}


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def write_csv(path: Path, fieldnames: List[str], rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def build_role_rows() -> Tuple[List[dict], Dict[str, List[str]]]:
    rows = []
    role_skill_ids: Dict[str, List[str]] = {}

    for role in ROLES:
        raw_weights = [s[2] for s in role.skills]
        total_raw = sum(raw_weights)
        if total_raw <= 0:
            raise ValueError(f"Role {role.role_id} has non-positive importance weight sum")
        normalized = [w / total_raw for w in raw_weights]
        rounded = [round(w, 6) for w in normalized]
        drift = round(1.0 - sum(rounded), 6)
        if abs(drift) > 1e-12:
            max_idx = max(range(len(rounded)), key=lambda i: rounded[i])
            rounded[max_idx] = round(rounded[max_idx] + drift, 6)

        role_skill_ids[role.role_id] = [s[0] for s in role.skills]
        for (skill_id, req, _raw, is_core), w in zip(role.skills, rounded):
            meta = SKILLS[skill_id]
            rows.append(
                {
                    "role_id": role.role_id,
                    "role_name": role.role_name,
                    "skill_id": skill_id,
                    "skill_name": meta["skill_name"],
                    "required_proficiency": int(round(req)),
                    "importance_weight": f"{w:.6f}",
                    "skill_category": meta["skill_category"],
                    "is_core_skill": "true" if is_core else "false",
                }
            )
    return rows, role_skill_ids


def build_metadata_rows(used_skill_ids: List[str]) -> List[dict]:
    rows = []
    for skill_id in sorted(set(used_skill_ids)):
        meta = SKILLS[skill_id]
        rows.append(
            {
                "skill_id": skill_id,
                "skill_name": meta["skill_name"],
                "skill_category": meta["skill_category"],
                "description": meta["description"],
                "beginner_description": meta["beginner_description"],
                "intermediate_description": meta["intermediate_description"],
                "advanced_description": meta["advanced_description"],
            }
        )
    return rows


def generate_student_profiles(
    role_skill_ids: Dict[str, List[str]], role_rows: List[dict], all_skill_ids: List[str]
) -> List[dict]:
    rng = random.Random(SEED)

    req_map: Dict[str, Dict[str, int]] = defaultdict(dict)
    for row in role_rows:
        req_map[row["role_id"]][row["skill_id"]] = int(row["required_proficiency"])

    # (name, probability, base_shift, noise_spread)
    level_profiles = [
        ("beginner", 0.30, -20.0, 11.0),
        ("intermediate", 0.45, -6.0, 13.0),
        ("advanced", 0.25, 4.0, 12.0),
    ]

    students: List[dict] = []
    role_ids = list(role_skill_ids.keys())

    for i in range(1, N_STUDENTS + 1):
        role_id = role_ids[(i - 1) % len(role_ids)]
        skills_for_role = set(role_skill_ids[role_id])

        # choose level bucket
        r = rng.random()
        cumulative = 0.0
        chosen = level_profiles[1]
        for lp in level_profiles:
            cumulative += lp[1]
            if r <= cumulative:
                chosen = lp
                break
        _, _, base_shift, spread = chosen

        latent_ability = rng.gauss(0.0, 7.5) + base_shift
        # category biases create strengths/weaknesses
        category_bias: Dict[str, float] = {}
        for sid in all_skill_ids:
            cat = SKILLS[sid]["skill_category"]
            if cat not in category_bias:
                category_bias[cat] = rng.gauss(0.0, 9.0)

        prof: Dict[str, float] = {}

        for sid in all_skill_ids:
            cat = SKILLS[sid]["skill_category"]
            noise = rng.gauss(0.0, spread)
            if sid in skills_for_role:
                req = req_map[role_id][sid]
                # role-relevant skills centered around requirement with student ability
                val = req + latent_ability + 0.35 * category_bias[cat] + noise
            else:
                # non-target skills: varied baseline with role-pattern tendencies
                base = 35.0 + 0.25 * category_bias[cat] + rng.gauss(0.0, 14.0)
                # modest tendencies by target role for realism (not deterministic)
                if role_id in {"frontend_developer", "full_stack_developer"} and sid in {"html", "css", "javascript", "react"}:
                    base += rng.uniform(5, 15)
                if role_id in {"backend_developer", "full_stack_developer"} and sid in {"sql", "dbms", "rest_apis", "nodejs"}:
                    base += rng.uniform(4, 14)
                if role_id == "data_analyst" and sid in {"sql", "pandas", "statistics", "data_visualization"}:
                    base += rng.uniform(5, 15)
                if role_id == "ml_engineer" and sid in {"python", "machine_learning", "statistics", "numpy", "pandas"}:
                    base += rng.uniform(5, 15)
                val = base + 0.4 * latent_ability
            prof[sid] = clamp(val)

        # correlation passes (create logical relationships, avoid identical scores)
        for _ in range(3):
            for sid in all_skill_ids:
                related = [x for x in CORR_GROUPS.get(sid, []) if x in prof]
                if not related:
                    continue
                rel_avg = sum(prof[x] for x in related) / len(related)
                # stronger pull for role-relevant skills
                pull = 0.22 if sid in skills_for_role else 0.15
                prof[sid] = clamp(0.78 * prof[sid] + pull * rel_avg + rng.gauss(0.0, 2.5))

        # inject explicit strengths/weaknesses for diversity
        role_skill_list = list(skills_for_role)
        if role_skill_list:
            strong_n = 2 if len(role_skill_list) >= 2 else 1
            weak_n = 2 if len(role_skill_list) >= 3 else 1
            strong = rng.sample(role_skill_list, k=strong_n)
            weak_candidates = [s for s in role_skill_list if s not in strong]
            weak = rng.sample(weak_candidates, k=min(weak_n, len(weak_candidates))) if weak_candidates else []
            for sid in strong:
                prof[sid] = clamp(prof[sid] + rng.uniform(6, 16))
            for sid in weak:
                prof[sid] = clamp(prof[sid] - rng.uniform(6, 18))

        # round to ints and avoid everyone being too similar by tiny jitter if duplicates cluster later not needed
        row = {
            "student_id": f"STU_{i:04d}",
            "target_role": role_id,
        }
        for sid in all_skill_ids:
            row[SKILLS[sid]["skill_name"]] = int(round(prof[sid]))
        students.append(row)

    return students


def validate_role_rows(rows: List[dict]) -> List[str]:
    errors: List[str] = []
    seen = set()
    role_weights: Dict[str, float] = defaultdict(float)

    for idx, row in enumerate(rows, start=2):
        key = (row.get("role_id"), row.get("skill_id"))
        if key in seen:
            errors.append(f"Duplicate role-skill mapping at row {idx}: {key}")
        seen.add(key)

        # missing values
        for k, v in row.items():
            if v is None or str(v).strip() == "":
                errors.append(f"Missing value '{k}' at row {idx}")

        try:
            req = float(row["required_proficiency"])
            weight = float(row["importance_weight"])
        except Exception:
            errors.append(f"Invalid numeric value at row {idx} for role/skill {key}")
            continue

        if not (0.0 <= req <= 100.0):
            errors.append(f"required_proficiency out of range at row {idx}: {req}")
        if weight <= 0:
            errors.append(f"importance_weight must be positive at row {idx}: {weight}")
        if str(row.get("is_core_skill")).lower() not in {"true", "false"}:
            errors.append(f"is_core_skill must be true/false at row {idx}: {row.get('is_core_skill')}")

        role_weights[row["role_id"]] += weight

    for role_id, total in role_weights.items():
        if abs(total - 1.0) > 1e-6:
            errors.append(f"Importance weights for {role_id} do not sum to 1.0 (sum={total:.9f})")

    # role skill counts
    counts = defaultdict(int)
    for row in rows:
        counts[row["role_id"]] += 1
    for role_id, count in counts.items():
        if count < 12 or count > 18:
            errors.append(f"Role {role_id} has {count} skills (expected 12-18)")

    return errors


def validate_metadata_rows(rows: List[dict]) -> List[str]:
    errors: List[str] = []
    seen = set()
    for idx, row in enumerate(rows, start=2):
        sid = row.get("skill_id")
        if not sid:
            errors.append(f"Missing skill_id at row {idx}")
        elif sid in seen:
            errors.append(f"Duplicate skill_id in metadata: {sid}")
        else:
            seen.add(sid)
        for k, v in row.items():
            if v is None or str(v).strip() == "":
                errors.append(f"Missing value '{k}' in metadata for {sid}")
    return errors


def validate_student_rows(rows: List[dict], all_skill_ids: List[str]) -> List[str]:
    errors: List[str] = []
    if len(rows) != N_STUDENTS:
        errors.append(f"Expected {N_STUDENTS} student rows, got {len(rows)}")

    seen_ids = set()
    skill_names = [SKILLS[sid]["skill_name"] for sid in all_skill_ids]
    expected_cols = {"student_id", "target_role", *skill_names}
    valid_roles = {r.role_id for r in ROLES}

    for idx, row in enumerate(rows, start=2):
        student_id = row.get("student_id")
        if not student_id:
            errors.append(f"Missing student_id at row {idx}")
        elif student_id in seen_ids:
            errors.append(f"Duplicate student_id: {student_id}")
        else:
            seen_ids.add(student_id)

        role = row.get("target_role")
        if role not in valid_roles:
            errors.append(f"Invalid target_role for {student_id}: {role}")

        row_cols = set(row.keys())
        missing_cols = expected_cols - row_cols
        extra_cols = row_cols - expected_cols
        if missing_cols:
            errors.append(f"Missing columns for {student_id}: {sorted(list(missing_cols))[:5]}")
        if extra_cols:
            errors.append(f"Unexpected columns for {student_id}: {sorted(list(extra_cols))[:5]}")

        for sname in skill_names:
            val = row.get(sname)
            if val is None or str(val).strip() == "":
                errors.append(f"Missing proficiency for {student_id}.{sname}")
                continue
            try:
                num = float(val)
            except Exception:
                errors.append(f"Non-numeric proficiency for {student_id}.{sname}: {val}")
                continue
            if not (0.0 <= num <= 100.0):
                errors.append(f"Proficiency out of range for {student_id}.{sname}: {num}")

    # diversity sanity checks (avoid uniform/almost identical profiles)
    # compare first skill column distribution roughly
    if rows:
        first_skill = skill_names[0]
        vals = [float(r[first_skill]) for r in rows]
        if max(vals) - min(vals) < 10:
            errors.append(f"Low diversity detected in '{first_skill}' scores")

    return errors


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    role_rows, role_skill_ids = build_role_rows()
    all_skill_ids = sorted({sid for sids in role_skill_ids.values() for sid in sids})
    metadata_rows = build_metadata_rows(all_skill_ids)
    student_rows = generate_student_profiles(role_skill_ids, role_rows, all_skill_ids)

    errors: List[str] = []
    errors.extend(validate_role_rows(role_rows))
    errors.extend(validate_metadata_rows(metadata_rows))
    errors.extend(validate_student_rows(student_rows, all_skill_ids))

    # consistency: every skill in role requirements has metadata
    meta_ids = {r["skill_id"] for r in metadata_rows}
    req_ids = {r["skill_id"] for r in role_rows}
    if not req_ids.issubset(meta_ids):
        errors.append(f"Missing metadata for skills: {sorted(req_ids - meta_ids)}")

    if errors:
        print("VALIDATION FAILED")
        for err in errors[:60]:
            print(f" - {err}")
        if len(errors) > 60:
            print(f" ... and {len(errors) - 60} more error(s)")
        return 1

    role_path = OUT_DIR / "role_skill_requirements.csv"
    meta_path = OUT_DIR / "skill_metadata.csv"
    students_path = OUT_DIR / "student_skill_profiles.csv"

    role_fields = [
        "role_id",
        "role_name",
        "skill_id",
        "skill_name",
        "required_proficiency",
        "importance_weight",
        "skill_category",
        "is_core_skill",
    ]
    meta_fields = [
        "skill_id",
        "skill_name",
        "skill_category",
        "description",
        "beginner_description",
        "intermediate_description",
        "advanced_description",
    ]
    student_fields = ["student_id", "target_role"] + [SKILLS[sid]["skill_name"] for sid in all_skill_ids]

    write_csv(role_path, role_fields, role_rows)
    write_csv(meta_path, meta_fields, metadata_rows)
    write_csv(students_path, student_fields, student_rows)

    print("Skill Gap datasets generated successfully.")
    print(f"Output directory: {OUT_DIR}")
    print(f"Roles: {len(role_skill_ids)}")
    for role in ROLES:
        print(f"  - {role.role_id} ({role.role_name}): {len(role.skills)} skills")
    print(f"Unique skills in requirements: {len(all_skill_ids)}")
    print(f"Rows -> role_skill_requirements.csv: {len(role_rows)}")
    print(f"Rows -> skill_metadata.csv: {len(metadata_rows)}")
    print(f"Rows -> student_skill_profiles.csv: {len(student_rows)}")
    print("Validation: OK (missing values, duplicates, score ranges, role skill counts, and per-role importance sums checked)")
    print("Note: Datasets are synthetic and illustrative (not verified industry standards / not real student records).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
