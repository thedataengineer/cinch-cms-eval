# CINCH CMS Evaluation Framework

An AI-powered, interactive framework for evaluating and scoring CMS platforms against specific business requirements. Built for CINCH's multi-platform consolidation initiative.

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/accionlabs/cinch-cms-eval.git
cd cinch-cms-eval
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Set API Keys

```bash
export ANTHROPIC_API_KEY="your-anthropic-key-here"
```

### 3. Run the PoC

```bash
streamlit run cms_eval_poc.py
```

Open http://localhost:8501 in your browser.

---

## What It Does

### The Framework

**Ontology-first approach** to CMS evaluation:

1. **Capabilities Model** (7 dimensions)
   - Content Modeling (schema flexibility, relationships, versioning)
   - Delivery & API (headless support, CDN integration, performance)
   - Personalization & Testing (A/B testing, segmentation, real-time decisioning)
   - Workflow & Governance (approval flows, RBAC, audit logging)
   - Integration Ecosystem (CRM, analytics, martech)
   - Performance & SEO (page speed, CDN, metadata, image optimization)
   - Operational (vendor stability, docs, support, community)

2. **Use Cases** (CINCH-specific)
   - High-velocity paid landing pages (20K+ views/day)
   - Multi-step enrollment funnels with conversion tracking
   - Multi-property content management (3+ brands)
   - Consolidate 5 legacy CMS into 3 platforms

3. **Business Outcomes** (weighted impact)
   - Conversion rate lift (target: 10%+)
   - Time to market for experiments (<24h)
   - Operational efficiency (consolidation)
   - Flexibility for future innovation
   - Cost efficiency & TCO

### The PoC Streamlit App

**Interactive tabs:**

1. **📊 Platform Scores** – Compare 6 major CMS platforms with capability breakdown
   - Quick scoring mode (local data)
   - AI-powered mode (Claude analyzes vendor docs with structured outputs)

2. **📋 Ontology Browser** – Explore the capability model, use cases, and business drivers
   - Filter by capability importance (critical, high, medium)
   - See facet details and weightings

3. **🏗️ Recommended Stacks** – 3 pre-built architecture patterns
   - Option A: HubSpot + Headless (hybrid, fast execution)
   - Option B: Pure Headless + CDP (best flexibility)
   - Option C: Composable CMS + HubSpot (balanced, modern)

4. **📄 Report** – Generate evaluations (Streamlit view, DOCX export ready)

### Evaluation Method

**Quick Score (Local):**
- Pre-populated platform capability scores (0-3 scale)
- Weighted against selected use cases
- Real-time adjustment of business outcome weights
- ~50ms execution

**AI-Powered (Claude):**
- Sends ontology + vendor doc snippets to Claude
- Claude returns structured JSON assessments using `response_format`
- Scores platform against CINCH requirements
- Identifies strengths, weaknesses, best-fit use cases
- ~2s execution (includes API latency)

---

## How to Adapt for Your Client

### 1. Modify the Ontology

Edit `cms_eval_poc.py` → `CMS_ONTOLOGY`:

```python
CMS_ONTOLOGY = {
    "capabilities": {
        "your_capability": {
            "label": "Human-readable name",
            "facets": ["facet_1", "facet_2", ...],
            "scale": "0-3",
            "importance": "critical"  # or "high", "medium"
        },
        # ...
    },
    "use_cases": {
        "your_use_case": {
            "label": "Your use case description",
            "required_capabilities": {
                "capability_key": 2,  # min required level
                # ...
            }
        },
        # ...
    }
}
```

### 2. Update Platform Data

Edit `PLATFORMS_DATA`:

```python
PLATFORMS_DATA = {
    "YourPlatform": {
        "type": "Category (e.g., Headless CMS)",
        "category": "headless",
        "deployment": "SaaS",
        "cost_band": "$$",
        "summary": "Brief description",
        "capabilities": {
            "your_capability": 2,  # score 0-3
            # ...
        }
    },
    # ...
}
```

### 3. Enhance with Real Vendor Docs

Replace pre-populated scores with AI analysis:

- Extract capability scores from vendor documentation
- Use Claude with structured outputs to parse large PDFs/websites
- Store scores in `data/platform_assessments.json`

Example:

```python
def extract_capabilities_from_docs(platform_name: str, docs_text: str) -> Dict:
    """Use Claude to extract capabilities from vendor docs."""
    client = anthropic.Anthropic()
    schema = {
        "type": "object",
        "properties": {
            "capabilities": {
                "type": "object",
                "properties": {
                    "content_modeling": {"type": "integer", "minimum": 0, "maximum": 3},
                    # ...
                }
            }
        }
    }
    # Call Claude with structured output...
    return response
```

### 4. Extend with TCO Calculator

Add to `Tab 3`:

```python
def calculate_tco(platform: str, years: int = 5) -> float:
    """Calculate 5-year TCO including licenses, people, integrations."""
    # License costs
    # People costs (% team needed)
    # Integration costs
    # Migration costs
    # Support costs
    return total_tco
```

---

## Directory Structure

```
cinch-cms-eval/
├── README.md
├── requirements.txt
├── cms_eval_poc.py              # Main Streamlit app
├── .env.example                 # Copy to .env, add your API keys
├── data/
│   ├── cms_ontology.json        # Formal ontology (external reference)
│   ├── platform_assessments.json # AI-generated platform scores
│   └── cinch_context.json       # CINCH-specific requirements
├── lib/
│   ├── __init__.py
│   ├── ontology.py              # Ontology class & utilities
│   ├── evaluator.py             # LLM evaluation logic
│   ├── scorer.py                # Scoring & aggregation
│   └── reporter.py              # Report generation
├── prompts/
│   ├── platform_assessment.md   # Claude prompt for platform eval
│   ├── capability_extraction.md # Claude prompt for doc parsing
│   └── stack_recommendation.md  # Claude prompt for architecture
└── tests/
    ├── test_ontology.py
    ├── test_evaluator.py
    └── test_scorer.py
```

---

## Advanced Usage

### Use as a Python Library

```python
from lib.ontology import CMSOntology
from lib.evaluator import PlatformEvaluator
from lib.scorer import CapabilityScorer

# Load ontology
onto = CMSOntology.from_file("data/cms_ontology.json")

# Evaluate platform
evaluator = PlatformEvaluator(api_key="your-key")
assessment = evaluator.evaluate("Contentful", onto, use_cases=["paid_landing_pages"])

# Score against use cases
scorer = CapabilityScorer(onto)
composite_score = scorer.score_for_use_case("Contentful", "enrollment_funnel")

print(f"Composite Score: {composite_score:.2f}")
print(f"Assessment: {assessment.strengths}")
```

### Batch Evaluate Multiple Platforms

```python
evaluator = PlatformEvaluator(api_key="key")
platforms = ["Contentful", "Sanity", "Strapi", "Hygraph"]

results = []
for platform in platforms:
    result = evaluator.evaluate(platform, ontology)
    results.append(result)

# Export to CSV
import pandas as pd
df = pd.DataFrame([r.to_dict() for r in results])
df.to_csv("evaluations.csv", index=False)
```

### Generate DOCX Report

```python
from lib.reporter import ReportGenerator

reporter = ReportGenerator()
report = reporter.generate(
    evaluations=results,
    recommendations=["Option B"],
    format="docx"
)
report.save("CINCH_CMS_Evaluation_Report.docx")
```

---

## API Integrations

### Anthropic Claude (Structured Outputs)

This PoC uses Claude 3.5 Sonnet with **structured outputs** for reliable JSON responses:

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "cms_assessment",
            "schema": assessment_schema,  # Your JSON Schema
            "strict": True
        }
    },
    messages=[{"role": "user", "content": prompt}]
)
```

**Benefits:**
- ✅ Reliable, schema-validated JSON output
- ✅ No parsing errors or hallucinations
- ✅ Directly usable in code
- ✅ Works across Claude, GPT-4, Gemini

---

## Development Roadmap

- [ ] Fetch live docs from vendor APIs (e.g., Contentful CMA) for real-time assessment
- [ ] Multi-threading for parallel platform evaluation
- [ ] Integration with Gartner/Forrester CMS magic quadrant data
- [ ] TCO calculator with regional cost adjustments
- [ ] Sensitivity analysis: "What if we weight conversion lift at 40%?"
- [ ] Migration complexity scorer
- [ ] Team readiness assessment (skills gaps)
- [ ] Export to Miro/Figma for stakeholder alignment

---

## Contributing

Contributions welcome! Areas:
- Additional CMS platforms
- Capability facet refinement
- Prompt engineering for better assessments
- Unit tests
- Performance optimizations

---

## License

MIT – Use freely in client projects.

---

## Support & Questions

- **Built at:** Accion Labs
- **Author:** [Field CTO & Strategy Team]
- **Questions?** Open an issue in the repo

---

**Last Updated:** 2025-12-11  
**Ontology Version:** 1.0  
**PoC Status:** Ready for interative client workshops
