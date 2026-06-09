"""
Configuration for the Redrob Hackathon Candidate Ranking System.
JD: Senior AI Engineer (Founding Team) at Redrob AI
"""

# --- JD-Relevant Keywords ---

# Career titles that align with Senior AI Engineer role (Tier A - highest match)
TIER_A_TITLES = [
    "ai engineer", "ml engineer", "machine learning engineer",
    "applied scientist", "research scientist", "applied ml engineer",
    "nlp engineer", "recommendation engineer", "search engineer",
    "relevance engineer", "ranking engineer", "ai architect",
    "deep learning engineer", "computer vision engineer",
    "data scientist", "staff ml engineer", "senior ml engineer",
    "lead ai engineer", "senior ai engineer",
]

# Tier B titles (good background but not directly AI/ML)
TIER_B_TITLES = [
    "data engineer", "backend engineer", "backend developer",
    "software engineer", "software developer", "full stack developer",
    "full stack engineer", "platform engineer", "infrastructure engineer",
    "python developer", "data analyst", "analytics engineer",
    "mlops engineer", "devops engineer", "cloud engineer",
]

# Tier C titles (non-technical - penalize)
TIER_C_TITLES = [
    "operations manager", "hr manager", "accountant", "accounting",
    "marketing manager", "content writer", "customer support",
    "sales executive", "mechanical engineer", "civil engineer",
    "electrical engineer", "hr executive", "recruiter",
    "business analyst", "project manager", "operations executive",
]

# Production AI Evidence keywords (what the JD REALLY wants)
# The JD stresses: retrieval, ranking, recommendation, search systems
PRODUCTION_AI_KEYWORDS = [
    "retrieval", "information retrieval", "retrieval augmented",
    "ranking", "learning to rank", "reranking", "rank", "ranker",
    "recommendation", "recommender", "search relevance",
    "semantic search", "vector search", "neural search",
    "embeddings", "embedding", "vector database", "vector db",
    "faiss", "pinecone", "qdrant", "weaviate", "chroma", "milvus",
    "elasticsearch", "opensearch", "solr",
    "ndcg", "mrr", "map", "precision@k", "recall@k",
    "evaluation", "a/b testing", "online evaluation",
    "production ml", "model deployment", "model serving",
    "pytorch", "tensorflow", "transformers",
    "python", "ml system", "ml pipeline",
]

# Dedicated Retrieval & Ranking keywords (separate component per winning strategy)
# JD specifically stresses: retrieval, ranking, recommendation, search systems
# These get their OWN weight as they are the JD's #1 signal
RETRIEVAL_RANKING_KEYWORDS = [
    "retrieval", "information retrieval", "retrieval augmented generation",
    "ranking", "learning to rank", "reranking", "ranker",
    "recommendation", "recommender system", "recommendation engine",
    "search relevance", "semantic search", "neural search",
    "hybrid search", "dense retrieval", "sparse retrieval",
    "vector search", "vector similarity",
    "ndcg", "mrr", "map", "precision@k", "recall@k",
    "online evaluation", "offline evaluation",
    "a/b testing", "ab test",
    "embedding", "embeddings", "sentence transformer",
    "faiss", "pinecone", "milvus", "weaviate", "chromadb", "chroma",
    "elasticsearch", "opensearch",
]

# General AI/ML keywords (still relevant but less specific)
GENERAL_AI_KEYWORDS = [
    "machine learning", "deep learning", "neural network",
    "nlp", "natural language processing", "computer vision",
    "speech recognition", "llm", "large language model",
    "fine-tuning", "rag", "generative ai",
    "data pipeline", "feature engineering", "mlops",
    "airflow", "spark", "kubeflow", "docker", "kubernetes",
    "aws", "gcp", "azure", "cloud",
    "ci/cd", "api", "microservices",
]

# Large consulting/services firms (penalize if entire career is here)
CONSULTING_FIRMS = {
    "tcs", "infosys", "wipro", "accenture", "capgemini",
    "cognizant", "hcl", "tech mahindra", "ltimindtree",
    "mindtree", "ibm", "deloitte", "pwc", "kpmg",
}

# --- Skill Relevance Mapping (now MINIMAL weight as per JD warning) ---

# AI/ML core skills (small bonus if present)
AI_CORE_SKILLS = {
    "NLP", "Fine-tuning LLMs", "LLM", "Large Language Models",
    "Object Detection", "Image Classification", "Computer Vision",
    "Speech Recognition", "TTS", "GANs", "Deep Learning",
    "Machine Learning", "Transfer Learning", "Reinforcement Learning",
    "Recommendation System", "Ranking", "Learning to Rank",
    "Information Retrieval", "Semantic Search", "Vector Search",
    "Embeddings", "RAG", "Retrieval Augmented Generation",
    "Neural Networks", "Transformer", "BERT", "GPT",
    "PyTorch", "TensorFlow", "Keras", "scikit-learn", "JAX",
    "MLflow", "Weights & Biases", "WandB",
}

# ML infrastructure/data skills (moderate bonus)
AI_INFRA_SKILLS = {
    "Python", "Data Pipelines", "ETL", "Feature Engineering",
    "Apache Spark", "Spark", "PySpark", "Apache Beam",
    "Airflow", "Kafka", "Data Engineering",
    "MLflow", "MLOps", "Docker", "Kubernetes", "Kubeflow",
    "FastAPI", "Flask", "REST API", "GraphQL", "gRPC",
    "SQL", "NoSQL", "PostgreSQL", "MongoDB", "Redis",
    "Milvus", "Pinecone", "Weaviate", "ChromaDB",
    "AWS", "GCP", "Azure", "Databricks",
    "Terraform", "CI/CD", "Git",
    "Statistical Modeling", "A/B Testing", "Experimental Design",
    "Evaluation", "NDCG", "MRR",
}

# General tech skills (minimal bonus)
GENERAL_TECH_SKILLS = {
    "JavaScript", "TypeScript", "React", "Angular", "Vue.js",
    "Node.js", "Java", "Spring", "Spring Boot",
    "C++", "C#", "Go", "Rust", "Scala",
    "HTML", "CSS", "Tailwind", "Bootstrap",
    "Redux", "Webpack", "Babel",
    "SAP", "Excel", "Tableau", "Power BI",
}

# --- Experience Fit Parameters ---
IDEAL_EXPERIENCE_YEARS = 7  # Peak of ideal range 5-9
EXPERIENCE_MIN = 3
EXPERIENCE_MAX = 15

# --- Education Weights ---
TIER_WEIGHTS = {
    "tier_1": 4.0,
    "tier_2": 3.0,
    "tier_3": 2.0,
    "tier_4": 1.0,
}

RELEVANT_FIELDS = [
    "artificial intelligence", "machine learning", "data science",
    "computer science", "computer engineering", "software engineering",
    "information technology", "data engineering", "statistics",
    "mathematics", "physics", "electrical engineering",
    "electronics", "robotics", "information science",
]

# --- Redrob Signals Weights ---
SIGNAL_WEIGHTS = {
    "profile_completeness_score": 0.10,
    "recruiter_response_rate": 0.20,
    "interview_completion_rate": 0.15,
    "search_appearance_30d": 0.10,
    "saved_by_recruiters_30d": 0.15,
    "github_activity_score": 0.10,
    "connection_count": 0.05,
    "endorsements_received": 0.05,
    "willing_to_relocate": 0.05,
    "verified_email": 0.03,
    "verified_phone": 0.02,
}

# --- Feature Weights (final scoring) ---
# Based on strategic analysis: Career History >> Skills
# JD explicitly warns against keyword-matching on skills
# Winning strategy (from challenge docs): career history > skills + retrieval/ranking experience >> everything else
WEIGHTS = {
    "career_relevance": 0.35,           # Title tiers + industry fit + consulting penalty (JD's top signal)
    "role_relevance": 0.20,             # Current title match to AI/ML (advice: 20% - find the needles)
    "production_ai_evidence": 0.14,      # General AI/ML production exp (JD: not just keywords, actually built things)
    "retrieval_ranking_experience": 0.10, # DEDICATED: retrieval/ranking/search/rec (JD's #1 specific ask)
    "behavioral_signals": 0.10,          # Redrob signals (JD: inactive candidates = not hireable)
    "experience_fit": 0.05,              # Years of experience (5-9yr sweet spot)
    "skills_match": 0.03,                # Minimal - EDA: skills artificially distributed
    "education_score": 0.03,              # Tier + field relevance
}

# Location preferences (JD says Pune/Noida preferred, open to relocation)
PREFERRED_LOCATIONS = ["pune", "noida"]
SECONDARY_LOCATIONS = ["hyderabad", "mumbai", "bangalore", "bengaluru", "chennai", "kochi", "trivandrum", "indore", "kolkata", "jaipur", "chandigarh", "coimbatore", "vizag", "bhubaneswar", "ahmedabad"]
TIER_1_CITIES = ["pune", "noida", "delhi", "gurgaon", "gurugram", "mumbai", "hyderabad", "bangalore", "bengaluru", "chennai"]

# Start-up vs Consulting bonus/penalty
PRODUCT_COMPANY_KEYWORDS = ["ai", "software", "fintech", "technology", "internet", "saas", "product"]
STARTUP_SIZE_KEYWORDS = ["1-10", "11-50", "51-200", "201-500"]

