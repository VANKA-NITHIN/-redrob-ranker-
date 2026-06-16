"""
Configuration for the Redrob Hackathon Candidate Ranking System.
JD: Senior AI Engineer (Founding Team) at Redrob AI

Version 3.0 — NDCG-optimized architecture with TF-IDF semantic matching,
negative signal detection, multi-stage pipeline, and 20 honeypot checks.
"""

# =============================================================================
# JD Intent Text (used for TF-IDF semantic matching)
# =============================================================================

JD_INTENT_TEXT = (
    "Senior AI Engineer founding team building retrieval ranking matching embeddings "
    "search recommendation vector database LLM production ranking systems. "
    "Build ranking and retrieval systems for intelligent candidate discovery. "
    "Production machine learning ranking models for matching candidates to jobs. "
    "Search relevance information retrieval semantic vector search. "
    "Recommender system and personalization engine for talent marketplace. "
    "End-to-end ML system design deployment monitoring A/B testing. "
    "Startup environment fast-paced product company early-stage."
)

# =============================================================================
# Multi-Query JD Expansion (captures different JD semantic facets)
# =============================================================================

JD_QUERIES = [
    (
        "Senior AI Engineer founding team building retrieval ranking matching embeddings "
        "search recommendation vector database LLM production ranking systems. "
        "Build ranking and retrieval systems for intelligent candidate discovery. "
        "Production machine learning ranking models for matching candidates to jobs. "
        "Search relevance information retrieval semantic vector search. "
        "Recommender system and personalization engine for talent marketplace. "
        "End-to-end ML system design deployment monitoring A/B testing. "
        "Startup environment fast-paced product company early-stage."
    ),
    (
        "Machine Learning Engineer building production recommender systems and ranking models. "
        "Information retrieval semantic search and vector similarity at scale. "
        "NDCG MRR precision recall evaluation metrics for search relevance. "
        "Feature engineering model deployment A/B testing online evaluation. "
        "Python PyTorch scikit-learn ML infrastructure and pipelines."
    ),
    (
        "Search relevance engineer improving candidate-job matching through ML. "
        "Build embeddings dense retrieval and hybrid search systems. "
        "FAISS vector database ANN approximate nearest neighbor for billion-scale retrieval. "
        "Fine-tune LLMs for matching and ranking using RAG and retrieval-augmented generation. "
        "Data-driven optimization of recruitment marketplace platform."
    ),
    (
        "Data scientist applied ML engineer building ranking recommendation systems. "
        "End-to-end ML lifecycle from data exploration to model serving and monitoring. "
        "A/B testing experimental design causal inference for product improvements. "
        "Cross-functional collaboration with product engineering and design teams. "
        "Iterate rapidly on models in a fast-paced startup environment."
    ),
    (
        "Software engineer with ML expertise building production systems at a talent platform. "
        "Design and implement ranking retrieval and recommendation algorithms. "
        "Scale ML infrastructure to handle millions of candidate-job pairs. "
        "Work on the intersection of HR technology AI and marketplace dynamics. "
        "Full-stack ML engineer who owns model development and deployment."
    ),
]

# =============================================================================
# Career Titles
# =============================================================================

TIER_A_TITLES = [
    "ai engineer", "ml engineer", "machine learning engineer",
    "applied scientist", "research scientist", "applied ml engineer",
    "nlp engineer", "recommendation engineer", "search engineer",
    "relevance engineer", "ranking engineer", "ai architect",
    "deep learning engineer", "computer vision engineer",
    "data scientist", "staff ml engineer", "senior ml engineer",
    "lead ai engineer", "senior ai engineer",
]

TIER_B_TITLES = [
    "data engineer", "backend engineer", "backend developer",
    "software engineer", "software developer", "full stack developer",
    "full stack engineer", "platform engineer", "infrastructure engineer",
    "python developer", "data analyst", "analytics engineer",
    "mlops engineer", "devops engineer", "cloud engineer",
]

TIER_C_TITLES = [
    "operations manager", "hr manager", "accountant", "accounting",
    "marketing manager", "content writer", "customer support",
    "sales executive", "mechanical engineer", "civil engineer",
    "electrical engineer", "hr executive", "recruiter",
    "business analyst", "project manager", "operations executive",
]

# =============================================================================
# Keyword Lists (reduced weight — TF-IDF handles semantic matching)
# =============================================================================

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

# =============================================================================
# Rare Skill Diamond Set (unicorn bonus)
# =============================================================================

DIAMOND_SKILL_SET = {
    "Ranking", "Learning to Rank", "Information Retrieval",
    "Semantic Search", "Vector Search", "Embeddings",
    "FAISS", "Pinecone", "Milvus", "Weaviate", "ChromaDB",
    "Recommendation System", "Recommender System",
    "NDCG", "MRR", "Evaluation", "A/B Testing",
    "RAG", "Retrieval Augmented Generation",
}

# =============================================================================
# Talent Platform Industry Keywords (HR tech bonus)
# =============================================================================

TALENT_PLATFORM_KEYWORDS = [
    "recruit", "recruiting", "recruitment", "recruiter",
    "talent", "talent acquisition", "talent marketplace",
    "hr", "hr tech", "human resources", "people operations",
    "hiring", "workforce", "people analytics",
    "candidate", "candidate discovery", "candidate matching",
    "job", "job search", "job matching",
    "ats", "applicant tracking", "application tracking",
    "redrob", "workday", "greenhouse", "lever", "breezy",
    "smartrecruiters", "icims", "jobvite", "ceipal",
]

# =============================================================================
# Profile Consistency Thresholds
# =============================================================================

CONSISTENCY_CAREER_RATIO_MIN = 0.5
CONSISTENCY_CAREER_RATIO_MAX = 1.8
CONSISTENCY_MAX_SKILL_INCONSISTENCY_RATIO = 0.3

# =============================================================================
# Company Classification
# =============================================================================

CONSULTING_FIRMS = {
    "tcs", "infosys", "wipro", "accenture", "capgemini",
    "cognizant", "hcl", "tech mahindra", "ltimindtree",
    "mindtree", "ibm", "deloitte", "pwc", "kpmg",
}

FICTIONAL_COMPANIES = {
    "dunder mifflin", "initech", "globex inc", "pied piper",
    "hooli", "stark industries", "acme corp", "wayne enterprises",
    "oscorp", "umbrella corporation", "sprockets",
    "wonka industries", "cyberdyne systems", "tyrell corporation",
    "massive dynamic", "gringotts", "wally",
}

COMPANY_TIER_1 = {
    "google", "meta", "microsoft", "amazon", "apple", "netflix",
    "linkedin", "uber", "airbnb", "twitter", "openai", "deepmind",
    "anthropic", "stripe", "square", "pinterest", "spotify",
    "nvidia", "intel", "amd", "salesforce", "adobe",
}

COMPANY_TIER_2 = {
    "zomato", "razorpay", "flipkart", "swiggy", "ola", "paytm",
    "freshworks", "zoho", "byju's", "unacademy", "phonepe",
    "cred", "dream11", "nykaa", "policybazaar", "upgrad",
    "meesho", "groww", "zerodha", "bharatpe", "postman", "chargebee",
}

COMPANY_TIER_3 = {
    "sarvam ai", "yellow.ai", "rephrase.ai", "mad street den",
    "haptik", "verloop", "krutrim", "saarthi.ai", "wysa",
    "locobuzz", "niramai", "glance", "inmobi", "practo",
    "pharmeasy", "vedantu", "zolo", "locus.sh", "innovaccer",
    "observe.ai", "uniphore", "artius", "niki.ai", "sigtuple",
}

# =============================================================================
# Negative Signal Patterns
# =============================================================================

ASPIRANT_PHRASES = [
    "self-learner", "self learner", "self taught", "self-taught",
    "self-directed", "transitioning toward", "transitioning to",
    "interested in transitioning", "curious about how ai",
    "curious about ai", "explored chatgpt", "experimented with chatgpt",
    "playing with", "tinkered with", "dabbled in",
    "side project", "side-project", "personal project",
    "haven't done it professionally",
    "haven\'t done it in a professional",
    "not the core of my day", "not my primary focus",
    "lightweight ml", "lightweight ai",
    "kaggle competition", "online course", "mooc",
    "building competence on the ml side",
    "if the team is open to it",
    "start contributing to ml-adjacent",
    "i've been keeping up with ai/ml",
]

GENERIC_DESCRIPTION_FRAGMENTS = [
    "business diagnostics", "process re-engineering",
    "digital transformation strategy", "stakeholder management",
    "structured problem-solving", "consulting toolkit",
    "slide-craft", "excel modeling", "executive communication",
    "month-end close", "financial reporting", "statutory compliance",
    "audit-readiness function", "managed a team of",
    "enterprise sales", "carried a quota",
]

# =============================================================================
# Skill Relevance Mapping
# =============================================================================

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

RR_SPECIFIC_SKILLS = {
    "FAISS", "Pinecone", "Milvus", "Weaviate", "ChromaDB", "Qdrant",
    "Elasticsearch", "OpenSearch", "Solr",
    "Information Retrieval", "Ranking", "Learning to Rank",
    "Semantic Search", "Vector Search", "Embeddings",
    "NDCG", "MRR", "Evaluation", "A/B Testing",
    "Recommendation System", "Recommender System",
}

# =============================================================================
# Education
# =============================================================================

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

# =============================================================================
# Feature Weights (NDCG-optimized)
# =============================================================================

WEIGHTS = {
    "career_relevance": 0.35,               # Career history relevance (Cfg11 sweep optimum)
    "role_relevance": 0.18,                 # Current title match to AI/ML
    "production_ai_evidence": 0.14,          # General AI/ML production exp
    "retrieval_ranking_experience": 0.15,    # JD's #1 specific ask (balanced: Cfg11 RR=11 vs original RR=18)
    "experience_fit": 0.05,                  # Years of experience
    "skills_match": 0.03,                    # Minimal — EDA confirms trap
    "education_score": 0.03,                 # Minimal
}

BEHAVIORAL_MULTIPLIER_MIN = 0.80
BEHAVIORAL_MULTIPLIER_MAX = 1.15

# =============================================================================
# Location & Notice Period Bonuses
# =============================================================================

PREFERRED_LOCATIONS = ["pune", "noida"]

# =============================================================================
# Pipeline Configuration
# =============================================================================

FAST_FILTER_TOP_K = 500    # Stage 1: keep top N for deep analysis
FINAL_TOP_K = 100           # Stage 3: final submission size

TFIDF_MAX_FEATURES = 5000       # Reduced: top 5000 features capture the most discriminative terms
TFIDF_NGRAM_RANGE = (1, 2)       # Reduced from (1,3): bigrams are ~10x faster to fit
TFIDF_MAX_DF = 0.8               # Increased to allow more common terms through
TFIDF_MIN_DF = 3
TFIDF_SAMPLE_SIZE = 20000        # Fit IDF on first 20K docs; estimates stabilize fast

SCURVE_STEEPNESS = 10.0      # More aggressive: creates 0.20+ gaps at top for better NDCG@10
SCURVE_MIDPOINT = 0.52       # Lower midpoint means more candidates get amplified

# =============================================================================
# NDCG@10 Optimization — Strategic score shaping
# =============================================================================

# Staged S-curve parameters: different curves for top tiers
# This creates a tiered score structure where elite candidates get amplified more
SCURVE_STAGE_1_STEEPNESS = 12.0   # For top 10 (NDCG@10 optimization)
SCURVE_STAGE_1_MIDPOINT = 0.48
SCURVE_STAGE_2_STEEPNESS = 8.0    # For ranks 11-50 (NDCG@50 optimization)
SCURVE_STAGE_2_MIDPOINT = 0.52

# Minimum score gap enforced between adjacent ranked candidates
# Prevents score ties and creates clean separation for NDCG
MIN_SCORE_GAP = 0.002

# =============================================================================
# Honeypot Statistical Detection Thresholds
# =============================================================================

# Z-score threshold for statistical anomaly detection
# Values derived from EDA: mean skills=9.6, std ~4.0; mean exp=7.2, std ~4.5
STAT_ANOMALY_Z_SCORE = 2.5      # Flag candidates >2.5 std from mean
HONEYPOT_CONTINUOUS_ALPHA = 0.7  # Blending factor for continuous vs discrete scoring

# =============================================================================
# Startup Fit Scoring
# =============================================================================

# Phrases indicating genuine startup experience (building from scratch)
STARTUP_OWNERSHIP_PHRASES = [
    "built from scratch", "built the", "designed and built",
    "architected", "founded", "co-founded", "cofounder", "co-founder",
    "first engineer", "founding engineer", "early engineer",
    "0 to 1", "zero to one", "from concept",
    "sole responsibility", "end-to-end ownership",
    "led the development", "led the design",
    "built the platform", "built the system",
    "owned the", "took ownership",
    "established the", "set up the",
    "greenfield", "ground up",
]

PRODUCT_OWNERSHIP_PHRASES = [
    "product", "user", "customer", "feature",
    "roadmap", "sprint", "iteration",
    "shipped", "launched", "released",
    "metrics", "impact", "growth",
    "A/B test", "experiment", "optimization",
    "cross-functional", "stakeholder",
]

TECHNICAL_DEPTH_PHRASES = [
    "system design", "architecture", "scalability",
    "latency", "throughput", "performance",
    "distributed", "microservices", "event-driven",
    "high availability", "fault tolerance",
    "monitoring", "observability", "telemetry",
    "data pipeline", "real-time", "streaming",
]

LATENT_ROLE_SIGNALS = {
    "search_retrieval_engineer": [
        "search", "retrieval", "information retrieval", "index",
        "query understanding", "query expansion", "query rewriting",
        "result ranking", "search relevance", "search quality",
        "web search", "enterprise search", "site search",
        "typo tolerance", "did you mean", "autocomplete",
        "suggestions", "personalized search", "faceted search",
        "inverted index", "search index", "indexing pipeline",
        "tf-idf", "bm25", "semantic search", "hybrid search",
        "sparse retrieval", "dense retrieval", "embedding",
        "re-ranking", "two-stage retrieval", "candidate generation",
    ],
    "recommendation_ranking_engineer": [
        "recommendation", "recommender", "personalization",
        "ranking", "learning to rank", "lambda rank", "lambdamart",
        "ctr prediction", "click-through rate", "conversion",
        "candidate selection", "candidate generation",
        "user-item", "collaborative filtering", "matrix factorization",
        "content-based", "hybrid recommendation",
        "feature engineering", "online learning",
        "exploration-exploitation", "multi-armed bandit",
        "relevance feedback", "implicit feedback",
    ],
    "applied_ml_engineer": [
        "production ml", "model deployment", "model serving",
        "training pipeline", "inference", "model monitoring",
        "feature store", "model registry", "versioning",
        "a/b testing", "online evaluation", "offline evaluation",
        "model performance", "model optimization", "quantization",
        "distributed training", "model parallelism",
        "pytorch", "tensorflow", "scikit-learn", "xgboost",
        "hyperparameter tuning", "cross-validation",
    ],
    "ml_platform_infra_engineer": [
        "ml platform", "ml infrastructure", "mlops",
        "data pipeline", "feature engineering", "feature pipeline",
        "airflow", "kubeflow", "mlflow", "tensorflow extended",
        "model lifecycle", "ci/cd", "automation",
        "kubernetes", "docker", "containerization",
        "monitoring", "alerting", "observability",
        "data warehouse", "data lake", "etl",
    ],
    "search_relevance_scientist": [
        "evaluation", "relevance", "user satisfaction",
        "ndcg", "mrr", "map", "precision@k", "recall@k",
        "online metrics", "offline metrics", "judgment list",
        "rater", "annotation", "ground truth",
        "win/loss analysis", "side-by-side evaluation",
        "user study", "click model", "session analysis",
        "query log analysis", "behavioral analysis",
    ],
}

