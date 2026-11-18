"""
Generate curated learning resources dataset for CareerLens Phase 2.

Outputs:
- backend/datasets/learning_resources.csv

Notes:
- Uses a curated list of genuine learning resources (no fabricated titles/URLs).
- Verifies resource URLs via HTTP requests before writing (skips/records failures; requires all included URLs to be reachable).
- Validates required fields, duplicates, skill IDs, difficulty/types, hours, and produces a summary.
- Fixed seed used only for deterministic processing metadata where needed.
- Safe to run repeatedly (overwrites output).
"""

from __future__ import annotations

import csv
import json
import random
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

SEED = 42
ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "backend" / "datasets"
SKILL_METADATA_CSV = DATASETS_DIR / "skill_metadata.csv"
OUTPUT_CSV = DATASETS_DIR / "learning_resources.csv"
VALIDATION_REPORT_JSON = DATASETS_DIR / "learning_resources_validation_report.json"

REQUIRED_COLUMNS = [
    "resource_id",
    "resource_title",
    "skill_id",
    "skill_name",
    "provider",
    "resource_type",
    "difficulty_level",
    "description",
    "resource_url",
    "estimated_hours",
    "prerequisites",
    "is_free",
    "language",
    "quality_score",
    "tags",
]

VALID_TYPES = {
    "Documentation",
    "Video Course",
    "Interactive Tutorial",
    "Practice Platform",
    "Project Tutorial",
    "Course",
    "Book or Reading Material",
}
VALID_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}


def load_skill_map() -> Dict[str, str]:
    if not SKILL_METADATA_CSV.exists():
        raise FileNotFoundError(f"Missing required Phase 1 dataset: {SKILL_METADATA_CSV}")
    skill_map: Dict[str, str] = {}
    with SKILL_METADATA_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = (row.get("skill_id") or "").strip()
            sname = (row.get("skill_name") or "").strip()
            if sid:
                skill_map[sid] = sname
    if not skill_map:
        raise ValueError("No skills loaded from skill_metadata.csv")
    return skill_map


def r(
    resource_id: str,
    skill_id: str,
    title: str,
    provider: str,
    resource_type: str,
    difficulty: str,
    description: str,
    url: str,
    hours: float,
    prerequisites: str,
    is_free: bool,
    quality_score: int,
    tags: str,
    language: str = "English",
) -> dict:
    return {
        "resource_id": resource_id,
        "resource_title": title,
        "skill_id": skill_id,
        "skill_name": "",  # filled from Phase 1 metadata
        "provider": provider,
        "resource_type": resource_type,
        "difficulty_level": difficulty,
        "description": description,
        "resource_url": url,
        "estimated_hours": hours,
        "prerequisites": prerequisites,
        "is_free": "true" if is_free else "false",
        "language": language,
        "quality_score": quality_score,
        "tags": tags,
    }


# Curated genuine resources (real titles/URLs/providers; no fabricated entries)
RESOURCES: List[dict] = [
    # java
    r("res_java_001","java","The Java Tutorials","Oracle Java Documentation","Documentation","Beginner","Official Oracle tutorials covering Java basics, syntax, classes, and core APIs.","https://docs.oracle.com/javase/tutorial/",20,"None",True,96,"java,oracle,basics,oop"),
    r("res_java_002","java","Java Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive Java lessons with examples and exercises for beginners.","https://www.w3schools.com/java/",10,"None",True,82,"java,interactive,basics"),
    r("res_java_003","java","Java Programming and Software Engineering Fundamentals Specialization (Audit)","Coursera (Duke University)","Course","Beginner","Introductory Java programming and software engineering concepts with audit access available.","https://www.coursera.org/specializations/java-programming",40,"None",False,88,"java,course,fundamentals"),
    r("res_java_004","java","Java (Basic) Skills Certification","HackerRank","Practice Platform","Intermediate","Practice Java problems and validate core language and problem-solving skills.","https://www.hackerrank.com/skills-directory/java_basic",12,"Basic Java syntax",True,86,"java,practice,coding"),
    r("res_java_005","java","Java Programming Language","GeeksforGeeks","Documentation","Intermediate","Comprehensive Java articles and examples covering OOP, collections, and APIs.","https://www.geeksforgeeks.org/java/",25,"Basic programming",True,84,"java,articles,oop,collections"),

    # python
    r("res_python_001","python","The Python Tutorial","Python Documentation","Documentation","Beginner","Official Python tutorial introducing syntax, data structures, modules, and standard library basics.","https://docs.python.org/3/tutorial/",18,"None",True,96,"python,official,tutorial"),
    r("res_python_002","python","Python","Kaggle Learn","Interactive Tutorial","Beginner","Hands-on Python lessons with exercises in notebooks.","https://www.kaggle.com/learn/python",7,"None",True,89,"python,interactive,kaggle"),
    r("res_python_003","python","Python for Everybody","PY4E","Course","Beginner","Free Python course covering basics, data structures, web access, and databases.","https://www.py4e.com/lessons",30,"None",True,90,"python,beginner,course"),
    r("res_python_004","python","Automate the Boring Stuff with Python","Automate the Boring Stuff","Book or Reading Material","Intermediate","Free online book focused on practical Python automation tasks and projects.","https://automatetheboringstuff.com/",25,"Basic Python",True,91,"python,automation,book"),
    r("res_python_005","python","Python (Basic) Skills Certification","HackerRank","Practice Platform","Intermediate","Practice Python coding challenges and assess language fundamentals.","https://www.hackerrank.com/skills-directory/python_basic",12,"Basic Python",True,86,"python,practice,coding"),

    # cpp
    r("res_cpp_001","cpp","Learn C++","LearnCpp.com","Course","Beginner","Structured free C++ tutorials from basics to modern C++ concepts.","https://www.learncpp.com/",35,"None",True,93,"cpp,modern-cpp,course"),
    r("res_cpp_002","cpp","C++ Tutorial","W3Schools","Interactive Tutorial","Beginner","Beginner-friendly C++ tutorial with examples and exercises.","https://www.w3schools.com/cpp/",12,"None",True,80,"cpp,basics,interactive"),
    r("res_cpp_003","cpp","C++ Language Tutorial","cplusplus.com","Documentation","Beginner","Reference-style C++ language tutorial and examples.","https://cplusplus.com/doc/tutorial/",18,"None",True,83,"cpp,reference,tutorial"),
    r("res_cpp_004","cpp","C++ Programming Language","GeeksforGeeks","Documentation","Intermediate","Comprehensive C++ articles covering language features, OOP, and STL.","https://www.geeksforgeeks.org/c-plus-plus/",25,"Basic C++",True,84,"cpp,stl,oop"),
    r("res_cpp_005","cpp","C++ Domain","HackerRank","Practice Platform","Intermediate","Practice C++ coding problems and language features through challenges.","https://www.hackerrank.com/domains/cpp",15,"Basic C++",True,85,"cpp,practice,coding"),

    # javascript
    r("res_javascript_001","javascript","JavaScript Guide","MDN Web Docs","Documentation","Beginner","MDN's comprehensive guide to JavaScript fundamentals and core concepts.","https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",20,"Basic HTML",True,96,"javascript,mdn,guide"),
    r("res_javascript_002","javascript","JavaScript Algorithms and Data Structures","freeCodeCamp","Course","Beginner","Free curriculum covering JavaScript fundamentals, ES6, and algorithmic practice.","https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/",40,"None",True,93,"javascript,course,algorithms"),
    r("res_javascript_003","javascript","The Modern JavaScript Tutorial","javascript.info","Documentation","Intermediate","In-depth modern JavaScript tutorial covering language features and browser APIs.","https://javascript.info/",30,"JavaScript basics",True,94,"javascript,modern,guide"),
    r("res_javascript_004","javascript","JavaScript Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive JavaScript lessons and examples for beginners.","https://www.w3schools.com/js/",12,"Basic HTML",True,82,"javascript,interactive,basics"),
    r("res_javascript_005","javascript","10 Days of JavaScript","HackerRank","Practice Platform","Intermediate","Practice JavaScript fundamentals through structured daily challenges.","https://www.hackerrank.com/domains/tutorials/10-days-of-javascript",10,"JavaScript basics",True,86,"javascript,practice,coding"),

    # html
    r("res_html_001","html","Structuring the web with HTML","MDN Web Docs","Documentation","Beginner","MDN learning area covering HTML structure, semantics, and accessibility basics.","https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content",15,"None",True,96,"html,mdn,semantics"),
    r("res_html_002","html","HTML Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive HTML lessons and examples for building web page structure.","https://www.w3schools.com/html/",10,"None",True,82,"html,interactive,basics"),
    r("res_html_003","html","Responsive Web Design Certification","freeCodeCamp","Course","Beginner","Hands-on curriculum covering HTML, CSS, and responsive layouts.","https://www.freecodecamp.org/learn/2022/responsive-web-design/",40,"None",True,93,"html,css,responsive,course"),
    r("res_html_004","html","Introduction to HTML","web.dev","Documentation","Beginner","Google web.dev guide to semantic HTML and document structure.","https://web.dev/learn/html",12,"None",True,90,"html,semantics,webdev"),
    r("res_html_005","html","HTML Reference","MDN Web Docs","Documentation","Intermediate","Comprehensive reference for HTML elements and attributes.","https://developer.mozilla.org/en-US/docs/Web/HTML/Reference",20,"Basic HTML",True,94,"html,reference,mdn"),

    # css
    r("res_css_001","css","Learn to style HTML using CSS","MDN Web Docs","Documentation","Beginner","MDN guide to CSS fundamentals, selectors, box model, and layout.","https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics",18,"Basic HTML",True,96,"css,mdn,styling"),
    r("res_css_002","css","CSS Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive CSS lessons with examples and exercises.","https://www.w3schools.com/css/",12,"Basic HTML",True,82,"css,interactive,basics"),
    r("res_css_003","css","Learn CSS","web.dev","Course","Intermediate","Structured CSS course covering layout, cascade, specificity, and modern features.","https://web.dev/learn/css",20,"CSS basics",True,92,"css,layout,course"),
    r("res_css_004","css","Flexbox Froggy","Flexbox Froggy","Interactive Tutorial","Beginner","Game-based interactive tutorial for learning CSS flexbox.","https://flexboxfroggy.com/",2,"Basic CSS",True,90,"css,flexbox,interactive"),
    r("res_css_005","css","Grid Garden","Grid Garden","Interactive Tutorial","Intermediate","Interactive game for learning CSS Grid layout concepts.","https://cssgridgarden.com/",2,"Basic CSS",True,90,"css,grid,interactive"),

    # react
    r("res_react_001","react","Quick Start","React Documentation","Documentation","Beginner","Official React quick start covering components, JSX, props, and state.","https://react.dev/learn",10,"JavaScript, HTML, CSS",True,97,"react,official,components"),
    r("res_react_002","react","Tutorial: Tic-Tac-Toe","React Documentation","Project Tutorial","Beginner","Official hands-on React tutorial building a tic-tac-toe game.","https://react.dev/learn/tutorial-tic-tac-toe",4,"JavaScript basics",True,95,"react,project,tutorial"),
    r("res_react_003","react","React Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive React basics including components, props, hooks, and routing.","https://www.w3schools.com/react/",10,"JavaScript, HTML",True,82,"react,interactive,basics"),
    r("res_react_004","react","Front End Development Libraries","freeCodeCamp","Course","Intermediate","freeCodeCamp curriculum section covering React and frontend libraries.","https://www.freecodecamp.org/learn/front-end-development-libraries/",30,"JavaScript, HTML, CSS",True,92,"react,frontend,course"),
    r("res_react_005","react","Adding Interactivity","React Documentation","Documentation","Intermediate","Official React guide to state, events, and interactive UI behavior.","https://react.dev/learn/adding-interactivity",8,"React basics",True,95,"react,state,interactivity"),

    # nodejs
    r("res_nodejs_001","nodejs","Introduction to Node.js","Node.js Documentation","Documentation","Beginner","Official Node.js introduction and getting started guides.","https://nodejs.org/en/learn/getting-started/introduction-to-nodejs",6,"JavaScript basics",True,96,"nodejs,official,basics"),
    r("res_nodejs_002","nodejs","Node.js Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive Node.js basics including modules, filesystem, and HTTP.","https://www.w3schools.com/nodejs/",10,"JavaScript basics",True,82,"nodejs,interactive,basics"),
    r("res_nodejs_003","nodejs","Back End Development and APIs","freeCodeCamp","Course","Intermediate","Hands-on curriculum covering Node.js, Express, and APIs.","https://www.freecodecamp.org/learn/back-end-development-and-apis/",30,"JavaScript basics",True,93,"nodejs,apis,course"),
    r("res_nodejs_004","nodejs","Node.js Guides","Node.js Documentation","Documentation","Intermediate","Official Node.js guides on core modules, diagnostics, and best practices.","https://nodejs.org/en/learn",15,"Node.js basics",True,94,"nodejs,guides,intermediate"),
    r("res_nodejs_005","nodejs","How To Code in Node.js","DigitalOcean Community","Course","Beginner","Tutorial series covering Node.js fundamentals, modules, and practical development.","https://www.digitalocean.com/community/tutorial-series/how-to-code-in-node-js",12,"JavaScript basics",True,89,"nodejs,tutorial-series,backend"),

    # expressjs
    r("res_expressjs_001","expressjs","Getting Started","Express.js Documentation","Documentation","Beginner","Official Express.js getting started guide for building web servers and APIs.","https://expressjs.com/en/starter/installing.html",4,"Node.js basics",True,95,"expressjs,nodejs,backend"),
    r("res_expressjs_002","expressjs","Express/Node introduction","MDN Web Docs","Documentation","Beginner","MDN introduction to Express and Node.js for server-side web development.","https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Express_Nodejs/Introduction",6,"JavaScript, Node.js basics",True,94,"expressjs,mdn,server-side"),
    r("res_expressjs_003","expressjs","Basic Node and Express","freeCodeCamp","Course","Beginner","Hands-on exercises to learn Node and Express fundamentals.","https://www.freecodecamp.org/learn/back-end-development-and-apis/#basic-node-and-express",8,"JavaScript basics",True,91,"expressjs,course,api"),
    r("res_expressjs_004","expressjs","Express Tutorial: The Local Library website","MDN Web Docs","Project Tutorial","Intermediate","Step-by-step project tutorial building a web app with Express and Node.js.","https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Express_Nodejs/Tutorial_local_library_website",20,"Node.js and Express basics",True,93,"expressjs,project,tutorial"),
    r("res_expressjs_005","expressjs","Routing","Express.js Documentation","Documentation","Intermediate","Official Express documentation on routing, middleware, and request handling.","https://expressjs.com/en/guide/routing.html",5,"Express basics",True,93,"expressjs,routing,middleware"),

    # rest_apis
    r("res_rest_apis_001","rest_apis","REST APIs","MDN Web Docs","Documentation","Beginner","MDN overview of REST concepts and HTTP-based API design.","https://developer.mozilla.org/en-US/docs/Glossary/REST",2,"HTTP basics",True,92,"rest,api,http"),
    r("res_rest_apis_002","rest_apis","HTTP Overview","MDN Web Docs","Documentation","Beginner","Foundational explanation of HTTP, requests, responses, and methods.","https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview",3,"None",True,94,"http,rest,basics"),
    r("res_rest_apis_003","rest_apis","REST API Tutorial","REST API Tutorial","Documentation","Beginner","Introductory tutorial covering REST principles, resources, and methods.","https://restfulapi.net/",6,"HTTP basics",True,86,"rest,api,design"),
    r("res_rest_apis_004","rest_apis","Using the Fetch API","MDN Web Docs","Documentation","Intermediate","Guide to making HTTP requests and working with REST-style APIs using Fetch.","https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch",4,"JavaScript and HTTP basics",True,93,"rest,api,fetch,http"),
    r("res_rest_apis_005","rest_apis","Web API Design Best Practices","Microsoft Learn","Documentation","Advanced","Guidance on designing robust, scalable RESTful web APIs.","https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design",6,"REST basics",True,91,"rest,api,design,best-practices"),

    # sql
    r("res_sql_001","sql","SQL Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive SQL tutorial covering queries, filtering, joins, and basic operations.","https://www.w3schools.com/sql/",10,"None",True,84,"sql,interactive,basics"),
    r("res_sql_002","sql","SQLBolt","SQLBolt","Interactive Tutorial","Beginner","Interactive lessons and exercises for learning SQL step by step.","https://sqlbolt.com/",6,"None",True,93,"sql,interactive,practice"),
    r("res_sql_003","sql","Intro to SQL","Kaggle Learn","Interactive Tutorial","Beginner","Hands-on SQL lessons using BigQuery notebooks.","https://www.kaggle.com/learn/intro-to-sql",5,"None",True,90,"sql,kaggle,interactive"),
    r("res_sql_004","sql","SQL (Basic) Skills Certification","HackerRank","Practice Platform","Intermediate","Practice SQL queries and validate core database querying skills.","https://www.hackerrank.com/skills-directory/sql_basic",10,"Basic SQL",True,87,"sql,practice,queries"),
    r("res_sql_005","sql","Mode SQL Tutorial","Mode","Documentation","Intermediate","Practical SQL tutorial for analytics, joins, aggregations, and window functions.","https://mode.com/sql-tutorial/",12,"Basic SQL",True,89,"sql,analytics,intermediate"),

    # dbms
    r("res_dbms_001","dbms","DBMS Tutorial","GeeksforGeeks","Documentation","Beginner","Database management system fundamentals including keys, normalization, and transactions.","https://www.geeksforgeeks.org/dbms/",20,"None",True,86,"dbms,database,basics"),
    r("res_dbms_002","dbms","Intro to SQL: Querying and managing data","Khan Academy","Video Course","Beginner","Introductory lessons on relational databases and SQL concepts.","https://www.khanacademy.org/computing/computer-programming/sql",8,"None",True,88,"dbms,sql,video"),
    r("res_dbms_003","dbms","Databases: Relational Databases and SQL","Stanford Online","Course","Intermediate","Stanford course covering relational databases and SQL fundamentals.","https://online.stanford.edu/courses/soe-ydatabases0005-databases-relational-databases-and-sql",20,"Basic data concepts",True,90,"dbms,databases,course"),
    r("res_dbms_004","dbms","Normalization in DBMS","GeeksforGeeks","Documentation","Intermediate","Detailed explanation of normalization forms with examples.","https://www.geeksforgeeks.org/introduction-of-database-normalization/",4,"DBMS basics",True,85,"dbms,normalization,intermediate"),
    r("res_dbms_005","dbms","ACID Properties in DBMS","GeeksforGeeks","Documentation","Intermediate","Explanation of ACID transaction properties in database systems.","https://www.geeksforgeeks.org/acid-properties-in-dbms/",3,"DBMS basics",True,85,"dbms,transactions,acid"),

    # mongodb
    r("res_mongodb_001","mongodb","MongoDB Manual","MongoDB Documentation","Documentation","Beginner","Official MongoDB manual covering concepts, CRUD, and data modeling.","https://www.mongodb.com/docs/manual/",20,"Database basics",True,95,"mongodb,nosql,official"),
    r("res_mongodb_002","mongodb","MongoDB CRUD Operations","MongoDB Documentation","Documentation","Beginner","Official guide to create, read, update, and delete operations in MongoDB.","https://www.mongodb.com/docs/manual/crud/",8,"MongoDB basics",True,94,"mongodb,crud,documentation"),
    r("res_mongodb_003","mongodb","MongoDB University","MongoDB University","Course","Beginner","Free courses and learning paths for MongoDB developers and database users.","https://learn.mongodb.com/",20,"Database basics",True,92,"mongodb,course,university"),
    r("res_mongodb_004","mongodb","MongoDB Aggregation","MongoDB Documentation","Documentation","Intermediate","Official documentation for MongoDB aggregation pipelines and operations.","https://www.mongodb.com/docs/manual/aggregation/",10,"MongoDB CRUD basics",True,93,"mongodb,aggregation,intermediate"),
    r("res_mongodb_005","mongodb","MongoDB Node.js Driver Quick Start","MongoDB Documentation","Project Tutorial","Intermediate","Quick start tutorial for using MongoDB with Node.js applications.","https://www.mongodb.com/docs/drivers/node/current/quick-start/",4,"Node.js and MongoDB basics",True,91,"mongodb,nodejs,tutorial"),

    # dsa
    r("res_dsa_001","dsa","Data Structures","GeeksforGeeks","Documentation","Beginner","Foundational data structures concepts with explanations and examples.","https://www.geeksforgeeks.org/data-structures/",25,"Basic programming",True,88,"dsa,data-structures,basics"),
    r("res_dsa_002","dsa","Algorithms","Khan Academy","Video Course","Beginner","Introductory algorithms lessons with visual explanations and exercises.","https://www.khanacademy.org/computing/computer-science/algorithms",10,"Basic math/programming",True,90,"algorithms,video,basics"),
    r("res_dsa_003","dsa","NeetCode Roadmap","NeetCode","Practice Platform","Intermediate","Structured roadmap and curated problem set for practicing DSA patterns.","https://neetcode.io/roadmap",40,"Basic programming",True,92,"dsa,practice,roadmap"),
    r("res_dsa_004","dsa","VisuAlgo","VisuAlgo","Interactive Tutorial","Intermediate","Interactive visualizations for learning data structures and algorithms.","https://visualgo.net/en",20,"Basic programming",True,91,"dsa,visualization,interactive"),
    r("res_dsa_005","dsa","Data Structures Practice","HackerRank","Practice Platform","Advanced","Practice data structure and algorithm challenges across difficulty levels.","https://www.hackerrank.com/domains/data-structures",30,"Intermediate DSA",True,90,"dsa,algorithms,practice"),

    # oop
    r("res_oop_001","oop","Object-Oriented Programming Concepts","Oracle Java Documentation","Documentation","Beginner","Official introduction to OOP concepts such as objects, classes, inheritance, and polymorphism.","https://docs.oracle.com/javase/tutorial/java/concepts/",6,"Basic Java",True,95,"oop,java,basics"),
    r("res_oop_002","oop","Classes","Python Documentation","Documentation","Beginner","Official Python documentation on classes and object-oriented features.","https://docs.python.org/3/tutorial/classes.html",6,"Basic Python",True,94,"oop,python,classes"),
    r("res_oop_003","oop","Object Oriented Programming in C++","GeeksforGeeks","Documentation","Intermediate","OOP concepts in C++ with examples including encapsulation, inheritance, and polymorphism.","https://www.geeksforgeeks.org/object-oriented-programming-in-cpp/",10,"Basic C++",True,84,"oop,cpp,intermediate"),
    r("res_oop_004","oop","Design Patterns","Refactoring.Guru","Documentation","Advanced","Catalog of design patterns and OOP design principles with examples.","https://refactoring.guru/design-patterns",20,"OOP fundamentals",True,92,"oop,design-patterns,advanced"),
    r("res_oop_005","oop","SOLID: The First Five Principles of Object Oriented Design","DigitalOcean Community","Documentation","Advanced","Explanation of SOLID design principles for maintainable object-oriented systems.","https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design",4,"OOP fundamentals",True,88,"oop,solid,design"),

    # operating_systems
    r("res_operating_systems_001","operating_systems","Operating System Tutorial","GeeksforGeeks","Documentation","Beginner","Core operating systems concepts including processes, memory, scheduling, and file systems.","https://www.geeksforgeeks.org/operating-systems/",25,"Basic computer fundamentals",True,86,"operating-systems,os,basics"),
    r("res_operating_systems_002","operating_systems","Operating Systems and You: Becoming a Power User","Coursera (Google)","Course","Beginner","Introductory course on operating systems concepts and practical usage (audit available).","https://www.coursera.org/learn/os-power-user",20,"Basic computer literacy",False,85,"operating-systems,course,basics"),
    r("res_operating_systems_003","operating_systems","CPU Scheduling in Operating Systems","GeeksforGeeks","Documentation","Intermediate","Detailed explanation of CPU scheduling algorithms and concepts.","https://www.geeksforgeeks.org/cpu-scheduling-in-operating-systems/",5,"OS basics",True,85,"operating-systems,scheduling"),
    r("res_operating_systems_004","operating_systems","Operating Systems: Three Easy Pieces","OSTEP","Book or Reading Material","Intermediate","Free online textbook covering operating systems concepts in depth.","https://pages.cs.wisc.edu/~remzi/OSTEP/",40,"OS basics",True,94,"operating-systems,book,ostep"),
    r("res_operating_systems_005","operating_systems","Process Synchronization in OS","GeeksforGeeks","Documentation","Advanced","Concepts and mechanisms for synchronization, concurrency, and deadlocks.","https://www.geeksforgeeks.org/introduction-of-process-synchronization/",6,"OS basics",True,85,"operating-systems,concurrency,synchronization"),

    # computer_networks
    r("res_computer_networks_001","computer_networks","Computer Network Tutorial","GeeksforGeeks","Documentation","Beginner","Networking fundamentals including OSI/TCP-IP models, protocols, and addressing.","https://www.geeksforgeeks.org/computer-network-tutorials/",25,"Basic computer fundamentals",True,86,"computer-networks,networking,basics"),
    r("res_computer_networks_002","computer_networks","The Bits and Bytes of Computer Networking","Coursera (Google)","Course","Beginner","Introductory networking course covering protocols, layers, and troubleshooting (audit available).","https://www.coursera.org/learn/computer-networking",25,"None",False,86,"computer-networks,course,google"),
    r("res_computer_networks_003","computer_networks","HTTP","MDN Web Docs","Documentation","Beginner","MDN resources explaining HTTP protocol concepts and behavior.","https://developer.mozilla.org/en-US/docs/Web/HTTP",10,"Web basics",True,94,"http,networking,mdn"),
    r("res_computer_networks_004","computer_networks","TCP/IP Model","GeeksforGeeks","Documentation","Intermediate","Explanation of TCP/IP layers, protocols, and data flow.","https://www.geeksforgeeks.org/tcp-ip-model/",4,"Networking basics",True,85,"computer-networks,tcp-ip"),
    r("res_computer_networks_005","computer_networks","Computer Networking: Principles, Protocols and Practice","CNP3 (Online Book)","Book or Reading Material","Advanced","Free, open textbook covering computer networking principles and protocols.","https://www.computer-networking.info/",30,"Networking fundamentals",True,90,"computer-networks,book,protocols"),

    # system_design
    r("res_system_design_001","system_design","System Design Primer","GitHub (donnemartin)","Documentation","Intermediate","Open-source guide to system design concepts, trade-offs, and interview preparation.","https://github.com/donnemartin/system-design-primer",30,"Backend and networking basics",True,94,"system-design,architecture,scalability"),
    r("res_system_design_002","system_design","Scalability","GeeksforGeeks","Documentation","Beginner","Introduction to scalability concepts in system design.","https://www.geeksforgeeks.org/what-is-scalability/",3,"Basic web/backend knowledge",True,84,"system-design,scalability,basics"),
    r("res_system_design_003","system_design","Caching guidance","Microsoft Learn","Documentation","Intermediate","Guidance on caching strategies and considerations in application architecture.","https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching",6,"System design basics",True,90,"system-design,caching,architecture"),
    r("res_system_design_004","system_design","System Design Tutorial","GeeksforGeeks","Documentation","Intermediate","Collection of system design topics including load balancing, databases, and architecture patterns.","https://www.geeksforgeeks.org/system-design-tutorial/",25,"Backend fundamentals",True,86,"system-design,tutorial,architecture"),
    r("res_system_design_005","system_design","Designing Data-Intensive Applications (Book Information)","O'Reilly","Book or Reading Material","Advanced","Reference page for a widely used book on data systems and scalable architecture.","https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/",40,"Distributed systems basics",False,93,"system-design,distributed-systems,book"),

    # git_github
    r("res_git_github_001","git_github","Git Documentation","Git Documentation","Documentation","Beginner","Official Git documentation and reference manual.","https://git-scm.com/doc",10,"None",True,95,"git,version-control,official"),
    r("res_git_github_002","git_github","Pro Git Book","Git","Book or Reading Material","Beginner","Free comprehensive book covering Git fundamentals and advanced usage.","https://git-scm.com/book/en/v2",20,"None",True,96,"git,book,version-control"),
    r("res_git_github_003","git_github","Hello World","GitHub Docs","Documentation","Beginner","GitHub quickstart for repositories, branches, commits, and pull requests.","https://docs.github.com/en/get-started/start-your-journey/hello-world",2,"GitHub account",True,93,"github,workflow,basics"),
    r("res_git_github_004","git_github","Learn Git Branching","Learn Git Branching","Interactive Tutorial","Intermediate","Interactive visual tutorial for practicing Git branching and workflows.","https://learngitbranching.js.org/",4,"Git basics",True,94,"git,branching,interactive"),
    r("res_git_github_005","git_github","About Pull Requests","GitHub Docs","Documentation","Intermediate","Official guide to pull requests and collaborative workflows on GitHub.","https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests",2,"Git/GitHub basics",True,92,"github,pull-requests,collaboration"),

    # numpy
    r("res_numpy_001","numpy","NumPy: the absolute basics for beginners","NumPy Documentation","Documentation","Beginner","Official beginner guide to NumPy arrays and basic operations.","https://numpy.org/doc/stable/user/absolute_beginners.html",4,"Basic Python",True,96,"numpy,arrays,basics"),
    r("res_numpy_002","numpy","NumPy Quickstart","NumPy Documentation","Documentation","Beginner","Official quickstart tutorial for NumPy fundamentals.","https://numpy.org/doc/stable/user/quickstart.html",4,"Basic Python",True,95,"numpy,quickstart,official"),
    r("res_numpy_003","numpy","NumPy Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive NumPy tutorial covering arrays, indexing, and operations.","https://www.w3schools.com/python/numpy/",6,"Basic Python",True,82,"numpy,interactive,basics"),
    r("res_numpy_004","numpy","NumPy Tutorial","GeeksforGeeks","Documentation","Intermediate","Comprehensive tutorial covering NumPy arrays, operations, and numerical computing concepts.","https://www.geeksforgeeks.org/numpy-tutorial/",8,"Python basics",True,85,"numpy,arrays,intermediate"),
    r("res_numpy_005","numpy","NumPy User Guide","NumPy Documentation","Documentation","Advanced","Comprehensive official user guide for NumPy features and APIs.","https://numpy.org/doc/stable/user/index.html",20,"NumPy basics",True,94,"numpy,reference,advanced"),

    # pandas
    r("res_pandas_001","pandas","10 minutes to pandas","pandas Documentation","Documentation","Beginner","Official quick introduction to pandas data structures and operations.","https://pandas.pydata.org/docs/user_guide/10min.html",2,"Basic Python",True,95,"pandas,dataframes,basics"),
    r("res_pandas_002","pandas","Pandas","Kaggle Learn","Interactive Tutorial","Beginner","Hands-on pandas lessons for data manipulation and analysis.","https://www.kaggle.com/learn/pandas",4,"Basic Python",True,90,"pandas,interactive,kaggle"),
    r("res_pandas_003","pandas","Getting started tutorials","pandas Documentation","Documentation","Beginner","Official getting started tutorials for using pandas effectively.","https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html",8,"Basic Python",True,94,"pandas,tutorials,official"),
    r("res_pandas_004","pandas","Pandas Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive pandas tutorial covering Series, DataFrames, and basic analysis.","https://www.w3schools.com/python/pandas/default.asp",6,"Basic Python",True,82,"pandas,interactive,basics"),
    r("res_pandas_005","pandas","User Guide","pandas Documentation","Documentation","Intermediate","Detailed official guide for pandas functionality and workflows.","https://pandas.pydata.org/docs/user_guide/index.html",20,"pandas basics",True,93,"pandas,guide,intermediate"),

    # matplotlib
    r("res_matplotlib_001","matplotlib","Quick start guide","Matplotlib Documentation","Documentation","Beginner","Official quick start for creating plots with Matplotlib.","https://matplotlib.org/stable/users/explain/quick_start.html",3,"Basic Python",True,95,"matplotlib,plotting,basics"),
    r("res_matplotlib_002","matplotlib","Pyplot tutorial","Matplotlib Documentation","Documentation","Beginner","Introductory tutorial to Matplotlib's pyplot interface.","https://matplotlib.org/stable/tutorials/pyplot.html",4,"Basic Python",True,94,"matplotlib,pyplot,tutorial"),
    r("res_matplotlib_003","matplotlib","Data Visualization","Kaggle Learn","Interactive Tutorial","Beginner","Hands-on data visualization course covering charts and plotting concepts.","https://www.kaggle.com/learn/data-visualization",4,"Basic Python",True,90,"matplotlib,seaborn,visualization"),
    r("res_matplotlib_004","matplotlib","Matplotlib Tutorial","W3Schools","Interactive Tutorial","Beginner","Interactive tutorial for creating common plots in Matplotlib.","https://www.w3schools.com/python/matplotlib_intro.asp",5,"Basic Python",True,82,"matplotlib,interactive,basics"),
    r("res_matplotlib_005","matplotlib","Examples","Matplotlib Documentation","Project Tutorial","Intermediate","Gallery of Matplotlib examples demonstrating practical plotting techniques.","https://matplotlib.org/stable/gallery/index.html",10,"Matplotlib basics",True,92,"matplotlib,examples,plots"),

    # data_visualization
    r("res_data_visualization_001","data_visualization","Data Visualisation Catalogue","Data Viz Catalogue","Documentation","Beginner","Reference guide to chart types and when to use them for effective data visualization.","https://datavizcatalogue.com/",4,"None",True,89,"data-visualization,charts,basics"),
    r("res_data_visualization_002","data_visualization","Fundamentals of Data Visualization","Claus O. Wilke (Online Book)","Book or Reading Material","Intermediate","Free online book on principles and best practices for data visualization.","https://clauswilke.com/dataviz/",20,"Basic charts",True,93,"data-visualization,design,book"),
    r("res_data_visualization_003","data_visualization","Data Visualization with Python","freeCodeCamp","Course","Intermediate","Project-based curriculum section focused on visualizing data with Python tools.","https://www.freecodecamp.org/learn/data-analysis-with-python/#data-visualization-with-python",12,"Python and pandas basics",True,89,"data-visualization,python,course"),
    r("res_data_visualization_004","data_visualization","From Data to Viz","From Data to Viz","Documentation","Beginner","Decision tree and guide for choosing appropriate visualizations based on data types.","https://www.data-to-viz.com/",4,"None",True,90,"data-visualization,charts,design"),
    r("res_data_visualization_005","data_visualization","Seaborn Tutorial","Seaborn Documentation","Documentation","Intermediate","Official tutorial for statistical data visualization with Seaborn.","https://seaborn.pydata.org/tutorial.html",8,"Python, matplotlib basics",True,91,"data-visualization,seaborn,python"),

    # statistics
    r("res_statistics_001","statistics","Statistics and Probability","Khan Academy","Video Course","Beginner","Comprehensive introductory statistics and probability lessons and exercises.","https://www.khanacademy.org/math/statistics-probability",30,"Basic algebra",True,92,"statistics,probability,basics"),
    r("res_statistics_002","statistics","Intro to Statistics","Khan Academy","Video Course","Beginner","Introductory statistics concepts including data displays and summaries.","https://www.khanacademy.org/math/statistics-probability/summarizing-quantitative-data",8,"Basic math",True,90,"statistics,descriptive,video"),
    r("res_statistics_003","statistics","Think Stats (2nd Edition)","Green Tea Press","Book or Reading Material","Intermediate","Free book introducing exploratory data analysis and statistics using Python.","https://greenteapress.com/wp/think-stats-2e/",20,"Basic Python and statistics",True,91,"statistics,python,book"),
    r("res_statistics_004","statistics","Statistical Thinking for the 21st Century","Poldrack (Online Book)","Book or Reading Material","Intermediate","Open online book covering modern statistical thinking and methods.","https://statsthinking21.github.io/statsthinking21-core-site/",25,"Intro statistics",True,89,"statistics,inference,book"),
    r("res_statistics_005","statistics","Statistics Tutorial","W3Schools","Interactive Tutorial","Beginner","Beginner-friendly statistics tutorial with examples and explanations.","https://www.w3schools.com/statistics/",8,"Basic math",True,80,"statistics,interactive,basics"),

    # probability
    r("res_probability_001","probability","Probability","Khan Academy","Video Course","Beginner","Probability fundamentals including events, combinations, and distributions basics.","https://www.khanacademy.org/math/statistics-probability/probability-library",15,"Basic algebra",True,92,"probability,math,basics"),
    r("res_probability_002","probability","Random variables","Khan Academy","Video Course","Intermediate","Lessons on random variables and probability distributions.","https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library",10,"Probability basics",True,90,"probability,random-variables"),
    r("res_probability_003","probability","Introduction to Probability, Statistics, and Random Processes","ProbabilityCourse.com","Book or Reading Material","Intermediate","Free online textbook covering probability, statistics, and random processes.","https://www.probabilitycourse.com/",30,"Basic calculus helpful",True,91,"probability,statistics,book"),
    r("res_probability_004","probability","Probability and Statistics Cookbook","Matthias Vallentin","Book or Reading Material","Advanced","Concise reference covering probability and statistics formulas and concepts.","https://pages.cs.wisc.edu/~tdw/files/cookbook-en.pdf",10,"Probability/statistics basics",True,86,"probability,statistics,reference"),
    r("res_probability_005","probability","Seeing Theory: Basic Probability","Brown University","Interactive Tutorial","Beginner","Visual and interactive introduction to probability concepts.","https://seeing-theory.brown.edu/basic-probability/index.html",4,"Basic math",True,91,"probability,interactive,visual"),

    # machine_learning
    r("res_machine_learning_001","machine_learning","Machine Learning Crash Course","Google Developers","Course","Beginner","Introductory machine learning course with videos and hands-on exercises.","https://developers.google.com/machine-learning/crash-course",15,"Python and basic math",True,94,"machine-learning,google,course"),
    r("res_machine_learning_002","machine_learning","Intro to Machine Learning","Kaggle Learn","Interactive Tutorial","Beginner","Hands-on introduction to core machine learning concepts and model building.","https://www.kaggle.com/learn/intro-to-machine-learning",7,"Basic Python",True,90,"machine-learning,kaggle,interactive"),
    r("res_machine_learning_003","machine_learning","Machine Learning Specialization (Audit)","Coursera (DeepLearning.AI & Stanford)","Course","Intermediate","Foundational machine learning specialization with audit access available.","https://www.coursera.org/specializations/machine-learning-introduction",60,"Python and basic math",False,95,"machine-learning,course,supervised-learning"),
    r("res_machine_learning_004","machine_learning","scikit-learn: Getting Started","Scikit-learn Documentation","Documentation","Beginner","Official getting started guide for machine learning with scikit-learn.","https://scikit-learn.org/stable/getting_started.html",4,"Python basics",True,95,"machine-learning,scikit-learn,basics"),
    r("res_machine_learning_005","machine_learning","Intermediate Machine Learning","Kaggle Learn","Interactive Tutorial","Intermediate","Hands-on lessons on missing values, pipelines, cross-validation, and more.","https://www.kaggle.com/learn/intermediate-machine-learning",4,"Intro ML basics",True,89,"machine-learning,kaggle,intermediate"),

    # deep_learning
    r("res_deep_learning_001","deep_learning","Practical Deep Learning for Coders","fast.ai","Course","Intermediate","Practical, hands-on deep learning course for coders.","https://course.fast.ai/",30,"Python and ML basics",True,94,"deep-learning,fastai,course"),
    r("res_deep_learning_002","deep_learning","Deep Learning Specialization (Audit)","Coursera (DeepLearning.AI)","Course","Advanced","Comprehensive deep learning specialization with audit access available.","https://www.coursera.org/specializations/deep-learning",80,"ML and linear algebra basics",False,95,"deep-learning,neural-networks,course"),
    r("res_deep_learning_003","deep_learning","Introduction to Deep Learning","MIT 6.S191","Video Course","Intermediate","MIT course introducing deep learning methods and applications.","https://introtodeeplearning.com/",20,"Python and ML basics",True,93,"deep-learning,mit,video"),
    r("res_deep_learning_004","deep_learning","Dive into Deep Learning","D2L","Book or Reading Material","Advanced","Interactive open-source book on deep learning theory and practice.","https://d2l.ai/",60,"ML and math basics",True,94,"deep-learning,book,interactive"),
    r("res_deep_learning_005","deep_learning","Neural Networks and Deep Learning (CS231n Notes)","Stanford CS231n","Documentation","Advanced","Course notes covering neural networks and deep learning fundamentals.","https://cs231n.github.io/",25,"ML and linear algebra basics",True,92,"deep-learning,neural-networks,notes"),

    # scikit_learn
    r("res_scikit_learn_001","scikit_learn","Scikit-Learn Tutorial","TutorialsPoint","Documentation","Beginner","Beginner-friendly tutorial covering scikit-learn basics and common machine learning workflows.","https://www.tutorialspoint.com/scikit_learn/index.htm",8,"Python basics",True,84,"scikit-learn,ml,basics"),
    r("res_scikit_learn_002","scikit_learn","User Guide","Scikit-learn Documentation","Documentation","Intermediate","Official user guide covering supervised/unsupervised learning and model evaluation.","https://scikit-learn.org/stable/user_guide.html",25,"ML basics",True,95,"scikit-learn,guide,models"),
    r("res_scikit_learn_003","scikit_learn","Examples","Scikit-learn Documentation","Project Tutorial","Intermediate","Gallery of practical scikit-learn examples for common machine learning tasks.","https://scikit-learn.org/stable/auto_examples/index.html",12,"Python and ML basics",True,94,"scikit-learn,examples,practice"),
    r("res_scikit_learn_004","scikit_learn","Choosing the right estimator","Scikit-learn Documentation","Documentation","Intermediate","Official estimator selection guide and flowchart for scikit-learn tasks.","https://scikit-learn.org/stable/machine_learning_map.html",2,"ML basics",True,92,"scikit-learn,model-selection,guide"),
    r("res_scikit_learn_005","scikit_learn","Model Evaluation","Scikit-learn Documentation","Documentation","Advanced","Official guide to metrics and model evaluation techniques in scikit-learn.","https://scikit-learn.org/stable/modules/model_evaluation.html",8,"ML basics",True,93,"scikit-learn,evaluation,metrics"),

    # tensorflow
    r("res_tensorflow_001","tensorflow","TensorFlow Tutorials","TensorFlow Documentation","Documentation","Beginner","Official TensorFlow tutorials for beginners and common ML tasks.","https://www.tensorflow.org/tutorials",12,"Python and ML basics",True,95,"tensorflow,tutorials,official"),
    r("res_tensorflow_002","tensorflow","Learn TensorFlow","TensorFlow Documentation","Course","Beginner","Official learning resources and guides for getting started with TensorFlow.","https://www.tensorflow.org/learn",10,"Python basics",True,94,"tensorflow,learn,basics"),
    r("res_tensorflow_003","tensorflow","Introduction to TensorFlow for Artificial Intelligence, Machine Learning, and Deep Learning (Audit)","Coursera (DeepLearning.AI)","Course","Beginner","Introductory TensorFlow course with audit access available.","https://www.coursera.org/learn/introduction-tensorflow",20,"Python and ML basics",False,90,"tensorflow,course,ml"),
    r("res_tensorflow_004","tensorflow","Keras: Getting Started","Keras Documentation","Documentation","Intermediate","Official Keras getting started guide for building neural networks.","https://keras.io/getting_started/",6,"Python and ML basics",True,94,"tensorflow,keras,deep-learning"),
    r("res_tensorflow_005","tensorflow","TensorFlow Guide","TensorFlow Documentation","Documentation","Advanced","In-depth TensorFlow guides for advanced APIs, performance, and deployment topics.","https://www.tensorflow.org/guide",20,"TensorFlow basics",True,93,"tensorflow,guide,advanced"),

    # pytorch
    r("res_pytorch_001","pytorch","PyTorch Tutorials","PyTorch Tutorials","Documentation","Beginner","Official PyTorch tutorials covering basics, deep learning, and deployment.","https://pytorch.org/tutorials/",15,"Python and ML basics",True,96,"pytorch,tutorials,official"),
    r("res_pytorch_002","pytorch","Learn the Basics","PyTorch Tutorials","Interactive Tutorial","Beginner","Official beginner-friendly tutorial for tensors, datasets, and model training.","https://pytorch.org/tutorials/beginner/basics/intro.html",6,"Python basics",True,95,"pytorch,basics,interactive"),
    r("res_pytorch_003","pytorch","Deep Learning with PyTorch: A 60 Minute Blitz","PyTorch Tutorials","Project Tutorial","Intermediate","Hands-on quickstart tutorial to build and train neural networks in PyTorch.","https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html",2,"Python and ML basics",True,94,"pytorch,deep-learning,tutorial"),
    r("res_pytorch_004","pytorch","PyTorch Documentation","PyTorch Documentation","Documentation","Intermediate","Official PyTorch API documentation and guides.","https://pytorch.org/docs/stable/index.html",20,"PyTorch basics",True,94,"pytorch,docs,reference"),
    r("res_pytorch_005","pytorch","Introduction to PyTorch (Microsoft Learn)","Microsoft Learn","Course","Beginner","Introductory learning path for PyTorch fundamentals and model training.","https://learn.microsoft.com/en-us/training/paths/pytorch-fundamentals/",8,"Python basics",True,90,"pytorch,course,microsoft"),

    # problem_solving
    r("res_problem_solving_001","problem_solving","Problem Solving (Basic) Skills Certification","HackerRank","Practice Platform","Beginner","Practice and assess foundational problem-solving skills with coding challenges.","https://www.hackerrank.com/skills-directory/problem_solving_basic",10,"Basic programming",True,87,"problem-solving,practice,coding"),
    r("res_problem_solving_002","problem_solving","Problem Solving (Intermediate) Skills Certification","HackerRank","Practice Platform","Intermediate","Intermediate problem-solving challenges to strengthen algorithmic thinking.","https://www.hackerrank.com/skills-directory/problem_solving_intermediate",12,"Problem-solving basics",True,87,"problem-solving,intermediate,practice"),
    r("res_problem_solving_003","problem_solving","Project Euler","Project Euler","Practice Platform","Advanced","Mathematical and computational problem-solving challenges for advanced practice.","https://projecteuler.net/",40,"Programming and math basics",True,91,"problem-solving,math,practice"),
    r("res_problem_solving_004","problem_solving","How to think like a programmer — lessons in problem solving","freeCodeCamp","Book or Reading Material","Intermediate","Article outlining practical problem-solving strategies for programmers.","https://www.freecodecamp.org/news/how-to-think-like-a-programmer-lessons-in-problem-solving-d1d8bf1de7d2/",3,"Basic programming",True,87,"problem-solving,heuristics,reading"),
    r("res_problem_solving_005","problem_solving","Codewars","Codewars","Practice Platform","Intermediate","Practice programming challenges (kata) across difficulty levels and languages.","https://www.codewars.com/",20,"Basic programming",True,88,"problem-solving,kata,practice"),

    # communication
    r("res_communication_001","communication","Improving Communication Skills","Coursera (University of Pennsylvania)","Course","Beginner","Course on effective communication skills for professional settings (audit available).","https://www.coursera.org/learn/wharton-communication-skills",10,"None",False,86,"communication,soft-skills,course"),
    r("res_communication_002","communication","Introduction to Public Speaking","Coursera (University of Washington)","Course","Beginner","Foundational public speaking course covering structure and delivery (audit available).","https://www.coursera.org/learn/public-speaking",12,"None",False,86,"communication,public-speaking,course"),
    r("res_communication_003","communication","Communication Skills","MindTools","Documentation","Beginner","Practical articles and guides on workplace communication skills.","https://www.mindtools.com/CommSkll/CommunicationIntro.htm",6,"None",False,84,"communication,workplace,articles"),
    r("res_communication_004","communication","Business Communication","Alison","Course","Intermediate","Free online course on professional and business communication fundamentals.","https://alison.com/course/business-communication",5,"Basic communication skills",True,80,"communication,business,course"),
    r("res_communication_005","communication","Presentation Tips","SkillsYouNeed","Documentation","Intermediate","Practical tips and guidance for preparing and delivering presentations effectively.","https://www.skillsyouneed.com/present/presentation-tips.html",4,"Basic communication skills",True,84,"communication,presentation,workplace"),

    # teamwork
    r("res_teamwork_001","teamwork","Teamwork Skills: Communicating Effectively in Groups","Coursera (University of Colorado Boulder)","Course","Beginner","Course on effective teamwork and group communication (audit available).","https://www.coursera.org/learn/teamwork-skills-effective-communication",10,"None",False,86,"teamwork,collaboration,course"),
    r("res_teamwork_002","teamwork","High Performance Collaboration: Leadership, Teamwork, and Negotiation","Coursera (Northwestern University)","Course","Intermediate","Course covering collaboration, leadership, and teamwork dynamics (audit available).","https://www.coursera.org/learn/leadership-collaboration",12,"Basic teamwork skills",False,86,"teamwork,leadership,collaboration"),
    r("res_teamwork_003","teamwork","Teamwork Skills","Alison","Course","Beginner","Free online course covering teamwork principles and effective collaboration.","https://alison.com/course/teamwork-skills",5,"None",True,81,"teamwork,course,collaboration"),
    r("res_teamwork_004","teamwork","Collaborating with pull requests","GitHub Docs","Documentation","Beginner","Documentation on collaborating in teams using pull requests and reviews.","https://docs.github.com/en/pull-requests/collaborating-with-pull-requests",4,"Git/GitHub basics",True,92,"teamwork,github,collaboration"),
    r("res_teamwork_005","teamwork","Teamwork and Collaboration","MindTools","Documentation","Intermediate","Articles and tools for improving teamwork and collaborative effectiveness.","https://www.mindtools.com/pages/main/newMN_TMM.htm",6,"Basic teamwork skills",False,84,"teamwork,collaboration,workplace"),
]


def validate_records(records: List[dict], skill_map: Dict[str, str]) -> Tuple[List[dict], List[str]]:
    errors: List[str] = []
    valid: List[dict] = []
    seen_ids = set()
    seen_urls = set()

    for rec in records:
        rid = str(rec.get("resource_id", "")).strip()
        sid = str(rec.get("skill_id", "")).strip()
        url = str(rec.get("resource_url", "")).strip()
        rtype = str(rec.get("resource_type", "")).strip()
        diff = str(rec.get("difficulty_level", "")).strip()

        # required fields
        missing = [c for c in REQUIRED_COLUMNS if rec.get(c) in (None, "") and c != "skill_name"]
        if missing:
            errors.append(f"{rid or '<no-id>'}: missing required fields {missing}")
            continue

        if rid in seen_ids:
            errors.append(f"{rid}: duplicate resource_id")
            continue
        if url in seen_urls:
            errors.append(f"{rid}: duplicate resource_url {url}")
            continue
        if sid not in skill_map:
            errors.append(f"{rid}: invalid skill_id '{sid}'")
            continue
        if rtype not in VALID_TYPES:
            errors.append(f"{rid}: invalid resource_type '{rtype}'")
            continue
        if diff not in VALID_DIFFICULTIES:
            errors.append(f"{rid}: invalid difficulty_level '{diff}'")
            continue

        try:
            hours = float(rec["estimated_hours"])
            if hours <= 0 or hours > 500:
                raise ValueError
        except Exception:
            errors.append(f"{rid}: invalid estimated_hours '{rec.get('estimated_hours')}'")
            continue

        try:
            q = int(rec["quality_score"])
            if q < 0 or q > 100:
                raise ValueError
        except Exception:
            errors.append(f"{rid}: invalid quality_score '{rec.get('quality_score')}'")
            continue

        is_free_val = str(rec.get("is_free", "")).strip().lower()
        if is_free_val not in {"true", "false"}:
            errors.append(f"{rid}: invalid is_free '{rec.get('is_free')}' (expected true/false)")
            continue

        rec = dict(rec)
        rec["skill_name"] = skill_map[sid]
        rec["estimated_hours"] = float(f"{hours:.2f}".rstrip("0").rstrip(".")) if "." in f"{hours}" else hours
        rec["quality_score"] = q
        rec["is_free"] = is_free_val
        valid.append(rec)
        seen_ids.add(rid)
        seen_urls.add(url)

    return valid, errors


def verify_urls(records: List[dict], timeout: float = 12.0, retries: int = 1) -> Tuple[List[dict], List[dict]]:
    """
    Verify URLs via HTTP. Keeps only records whose URL returns an acceptable response.
    Records per-URL validation results.
    """
    ctx = ssl.create_default_context()
    insecure_ctx = ssl._create_unverified_context()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    accepted_statuses = set(range(200, 400))  # 2xx/3xx
    verified: List[dict] = []
    results: List[dict] = []

    for rec in records:
        url = rec["resource_url"]
        status = None
        ok = False
        method_used = None
        err_msg = None
        contexts = [ctx, insecure_ctx]
        for attempt in range(retries + 1):
            for method in ("HEAD", "GET"):
                for c in contexts:
                    try:
                        req = urllib.request.Request(url, headers=headers, method=method)
                        with urllib.request.urlopen(req, timeout=timeout, context=c) as resp:
                            status = getattr(resp, "status", None) or resp.getcode()
                            method_used = f"{method}{'/insecure' if c is insecure_ctx else ''}"
                            if status in accepted_statuses:
                                ok = True
                                err_msg = None
                                break
                            else:
                                err_msg = f"HTTP {status}"
                    except urllib.error.HTTPError as e:
                        status = e.code
                        method_used = f"{method}{'/insecure' if c is insecure_ctx else ''}"
                        if status in accepted_statuses:
                            ok = True
                            err_msg = None
                            break
                        err_msg = f"HTTP {status}"
                    except Exception as e:
                        status = None
                        method_used = f"{method}{'/insecure' if c is insecure_ctx else ''}"
                        err_msg = f"{type(e).__name__}: {e}"
                    # for SSL cert errors, fallback to insecure_ctx is useful; otherwise don't double-try same failure unnecessarily
                    if "CERTIFICATE_VERIFY_FAILED" not in str(err_msg or "") and c is ctx:
                        # if not cert issue, trying insecure same method unlikely to help, but cheap enough; continue to try
                        pass
                if ok:
                    break
            if ok:
                break
            if attempt < retries:
                time.sleep(0.5)
        results.append({
            "resource_id": rec["resource_id"],
            "url": url,
            "ok": ok,
            "status": status,
            "method": method_used,
            "error": err_msg,
        })
        if ok:
            verified.append(rec)
        else:
            print(f"[URL FAIL] {rec['resource_id']} {url} -> {err_msg}", file=sys.stderr)
    return verified, results


def write_csv(path: Path, records: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        for rec in records:
            writer.writerow({k: rec.get(k, "") for k in REQUIRED_COLUMNS})


def print_summary(records: List[dict], skill_map: Dict[str, str], url_results: List[dict]) -> None:
    by_skill = Counter(r["skill_id"] for r in records)
    by_provider = Counter(r["provider"] for r in records)
    by_type = Counter(r["resource_type"] for r in records)
    by_diff = Counter(r["difficulty_level"] for r in records)
    free_count = sum(1 for r in records if str(r["is_free"]).lower() == "true")
    paid_count = len(records) - free_count

    missing_skills = sorted(set(skill_map.keys()) - set(by_skill.keys()))
    verified_ok = sum(1 for x in url_results if x["ok"])
    verified_fail = sum(1 for x in url_results if not x["ok"])

    print("\n=== Learning Resources Dataset Summary ===")
    print(f"Output: {OUTPUT_CSV}")
    print(f"Total resources: {len(records)}")
    print(f"Covered skills: {len(by_skill)} / {len(skill_map)}")
    print(f"Free resources: {free_count} | Paid/limited-free: {paid_count}")
    print(f"URL verification: {verified_ok} OK, {verified_fail} failed (included only OK)")

    print("\nBy difficulty:")
    for k in ["Beginner", "Intermediate", "Advanced"]:
        print(f"  - {k}: {by_diff.get(k, 0)}")

    print("\nBy resource type:")
    for k, v in sorted(by_type.items()):
        print(f"  - {k}: {v}")

    print("\nBy skill (count):")
    for sid in sorted(skill_map.keys()):
        print(f"  - {sid} ({skill_map[sid]}): {by_skill.get(sid, 0)}")

    print("\nBy provider:")
    for k, v in sorted(by_provider.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  - {k}: {v}")

    if missing_skills:
        print("\nWARNING: Skills missing coverage:")
        for sid in missing_skills:
            print(f"  - {sid} ({skill_map[sid]})")
    else:
        print("\nAll Phase 1 skills are covered.")

    assert not missing_skills, "All 33 Phase 1 skills must be covered"


def main() -> None:
    random.seed(SEED)
    skill_map = load_skill_map()
    print(f"Loaded {len(skill_map)} skills from Phase 1 metadata")

    records, errors = validate_records(RESOURCES, skill_map)
    if errors:
        print("Validation errors before URL check:", file=sys.stderr)
        for e in errors:
            print(f" - {e}", file=sys.stderr)
        raise SystemExit(1)

    print(f"Pre-URL validation passed for {len(records)} curated records. Verifying URLs...")
    verified_records, url_results = verify_urls(records)

    # Re-check coverage after URL verification
    covered = {r["skill_id"] for r in verified_records}
    missing = sorted(set(skill_map.keys()) - covered)
    if missing:
        print("URL verification removed coverage for skills:", file=sys.stderr)
        for sid in missing:
            print(f" - {sid} ({skill_map[sid]})", file=sys.stderr)
        # Also show which URLs failed per missing skill
        failed_ids = {x["resource_id"] for x in url_results if not x["ok"]}
        for sid in missing:
            for rec in records:
                if rec["skill_id"] == sid and rec["resource_id"] in failed_ids:
                    print(f"   failed: {rec['resource_id']} {rec['resource_url']}", file=sys.stderr)
        raise SystemExit(2)

    # Deterministic ordering
    verified_records.sort(key=lambda x: (x["skill_id"], {"Beginner":0,"Intermediate":1,"Advanced":2}[x["difficulty_level"]], x["resource_id"]))

    write_csv(OUTPUT_CSV, verified_records)
    report = {
        "seed": SEED,
        "total_curated": len(records),
        "total_written": len(verified_records),
        "url_results": url_results,
        "coverage": {sid: sum(1 for r in verified_records if r["skill_id"] == sid) for sid in sorted(skill_map.keys())},
    }
    VALIDATION_REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print_summary(verified_records, skill_map, url_results)
    print(f"\nValidation report: {VALIDATION_REPORT_JSON}")


if __name__ == "__main__":
    main()
