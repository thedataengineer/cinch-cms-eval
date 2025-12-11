"""
CINCH CMS Evaluation Framework – Streamlit PoC
Interactive tool to evaluate and score CMS platforms against CINCH requirements
"""

import json
import asyncio
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from llm_providers import get_provider, get_available_providers, OllamaProvider, AnthropicProvider

# ============================================================================
# ONTOLOGY & DATA
# ============================================================================

CMS_ONTOLOGY = {
    "capabilities": {
        "content_modeling": {
            "label": "Content Modeling",
            "facets": [
                "schema_flexibility",
                "relationship_support",
                "versioning",
                "multi_channel_support"
            ],
            "scale": "0-3",
            "importance": "critical"
        },
        "delivery": {
            "label": "Delivery & API",
            "facets": [
                "api_maturity",
                "headless_support",
                "cdn_integration",
                "performance_optimization"
            ],
            "scale": "0-3",
            "importance": "critical"
        },
        "personalization": {
            "label": "Personalization & Testing",
            "facets": [
                "native_ab_testing",
                "native_personalization",
                "segment_targeting",
                "real_time_decisioning"
            ],
            "scale": "0-3",
            "importance": "critical"
        },
        "workflow": {
            "label": "Workflow & Governance",
            "facets": [
                "content_approval_flows",
                "role_based_access",
                "versioning_control",
                "audit_logging"
            ],
            "scale": "0-3",
            "importance": "high"
        },
        "integrations": {
            "label": "Integration Ecosystem",
            "facets": [
                "crm_integration",
                "analytics_integration",
                "martech_ecosystem",
                "api_first_design"
            ],
            "scale": "0-3",
            "importance": "high"
        },
        "performance": {
            "label": "Performance & SEO",
            "facets": [
                "page_speed_optimization",
                "cdn_caching",
                "seo_metadata",
                "image_optimization"
            ],
            "scale": "0-3",
            "importance": "high"
        },
        "operational": {
            "label": "Operational & Support",
            "facets": [
                "vendor_stability",
                "documentation_quality",
                "support_tier",
                "community_maturity"
            ],
            "scale": "0-3",
            "importance": "medium"
        }
    },
    "use_cases": {
        "paid_landing_pages": {
            "label": "High-velocity paid landing pages",
            "required_capabilities": {
                "personalization": 2,
                "delivery": 2,
                "integrations": 2
            }
        },
        "enrollment_funnel": {
            "label": "Multi-step enrollment funnel with conversions",
            "required_capabilities": {
                "content_modeling": 2,
                "personalization": 3,
                "integrations": 3
            }
        },
        "multi_property": {
            "label": "Multi-property content management (3+ brand properties)",
            "required_capabilities": {
                "content_modeling": 3,
                "workflow": 2,
                "delivery": 2
            }
        },
        "consolidation": {
            "label": "Consolidate 5 legacy CMS into 3 platforms",
            "required_capabilities": {
                "integrations": 3,
                "workflow": 2,
                "operational": 2
            }
        }
    },
    "business_outcomes": {
        "conversion_lift": {
            "label": "Conversion rate lift (target: 10%+)",
            "weight": 0.25
        },
        "time_to_market": {
            "label": "Time to launch new experiments (target: <24h)",
            "weight": 0.25
        },
        "operational_efficiency": {
            "label": "Content ops efficiency (consolidation)",
            "weight": 0.20
        },
        "flexibility": {
            "label": "Flexibility for future innovation",
            "weight": 0.15
        },
        "cost_efficiency": {
            "label": "Cost efficiency & TCO",
            "weight": 0.15
        }
    }
}

PLATFORMS_DATA = {
    "HubSpot": {
        "type": "Traditional CMS + CRM",
        "category": "coupled",
        "deployment": "SaaS",
        "traffic_band": "20K+/day",
        "cost_band": "$$$",
        "summary": "Integrated CRM + CMS, strong marketing automation, limited content modeling flexibility",
        "capabilities": {
            "content_modeling": 1,
            "delivery": 1,
            "personalization": 2,
            "workflow": 2,
            "integrations": 3,
            "performance": 1,
            "operational": 3
        }
    },
    "Contentful": {
        "type": "Headless CMS",
        "category": "headless",
        "deployment": "SaaS",
        "traffic_band": "20K+/day",
        "cost_band": "$$",
        "summary": "Pure headless, rich schema, API-first, modern DX, requires front-end layer",
        "capabilities": {
            "content_modeling": 3,
            "delivery": 3,
            "personalization": 1,
            "workflow": 2,
            "integrations": 2,
            "performance": 3,
            "operational": 3
        }
    },
    "Liferay": {
        "type": "Hybrid Portal/CMS",
        "category": "hybrid",
        "deployment": "On-prem/Cloud",
        "traffic_band": "20K+/day",
        "cost_band": "$$$$",
        "summary": "Portal + CMS, enterprise workflows, steep learning curve, heavyweight",
        "capabilities": {
            "content_modeling": 2,
            "delivery": 2,
            "personalization": 2,
            "workflow": 3,
            "integrations": 2,
            "performance": 2,
            "operational": 2
        }
    },
    "Sitecore": {
        "type": "Enterprise DXP + CMS",
        "category": "monolith",
        "deployment": "On-prem/Cloud",
        "traffic_band": "20K+/day+",
        "cost_band": "$$$$$",
        "summary": "All-in-one enterprise CMS + personalization + commerce, expensive, vendor lock-in risk",
        "capabilities": {
            "content_modeling": 3,
            "delivery": 2,
            "personalization": 3,
            "workflow": 3,
            "integrations": 3,
            "performance": 2,
            "operational": 2
        }
    },
    "Sanity": {
        "type": "Headless CMS",
        "category": "headless",
        "deployment": "SaaS",
        "traffic_band": "20K+/day",
        "cost_band": "$$",
        "summary": "Rich schema + custom desk/plugins, structured content, growing ecosystem",
        "capabilities": {
            "content_modeling": 3,
            "delivery": 3,
            "personalization": 1,
            "workflow": 2,
            "integrations": 2,
            "performance": 3,
            "operational": 2
        }
    },
    "Composable (Acquia/Agility)": {
        "type": "Composable CMS",
        "category": "composable",
        "deployment": "SaaS",
        "traffic_band": "20K+/day",
        "cost_band": "$$$",
        "summary": "Best-of-breed headless + best-of-breed personalization/testing, flexible stack",
        "capabilities": {
            "content_modeling": 3,
            "delivery": 3,
            "personalization": 3,
            "workflow": 2,
            "integrations": 3,
            "performance": 3,
            "operational": 2
        }
    }
}

# ============================================================================
# STREAMLIT UI
# ============================================================================

st.set_page_config(page_title="CINCH CMS Evaluation", layout="wide", initial_sidebar_state="expanded")

st.title("🎯 CINCH CMS Evaluation Framework")
st.markdown("**Interactive tool to evaluate and score CMS platforms for CINCH's consolidation strategy**")

# Sidebar: Controls
with st.sidebar:
    st.header("⚙️ Evaluation Settings")
    
    selected_use_cases = st.multiselect(
        "Select CINCH Use Cases:",
        options=list(CMS_ONTOLOGY["use_cases"].keys()),
        default=list(CMS_ONTOLOGY["use_cases"].keys()),
        format_func=lambda x: CMS_ONTOLOGY["use_cases"][x]["label"]
    )
    
    st.markdown("---")
    st.subheader("Business Driver Weights")
    
    weights = {}
    for outcome_key, outcome in CMS_ONTOLOGY["business_outcomes"].items():
        weights[outcome_key] = st.slider(
            outcome["label"],
            min_value=0.0,
            max_value=1.0,
            value=outcome["weight"],
            step=0.05,
            key=f"weight_{outcome_key}"
        )
    
    # Normalize weights
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}
    
    st.markdown("---")
    
    eval_method = st.radio(
        "Evaluation Method:",
        options=["Quick Score (Local)", "AI-Powered Analysis"],
        help="Local: Use pre-populated data. AI: Use LLM to generate detailed assessments."
    )
    
    # Provider selection (only show if AI analysis selected)
    if eval_method == "AI-Powered Analysis":
        st.markdown("---")
        st.subheader("🤖 LLM Provider")
        
        provider_type = st.radio(
            "Select Provider:",
            options=["OpenAI (Cloud)", "Ollama (Local)", "Claude (API)"],
            help="OpenAI: Cloud API (recommended). Ollama: Run locally. Claude: Anthropic API."
        )
        
        if provider_type == "Ollama (Local)":
            ollama_model = st.text_input(
                "Ollama Model:",
                value="llama3.1",
                help="Model to use (e.g., llama3.1, mistral, codellama)"
            )
            ollama_host = st.text_input(
                "Ollama Host:",
                value="http://localhost:11444",
                help="Ollama server URL"
            )
            # Check availability
            try:
                test_provider = OllamaProvider(model=ollama_model, host=ollama_host)
                if test_provider.is_available():
                    st.success(f"✅ Connected to Ollama")
                else:
                    st.warning("⚠️ Ollama running but model may need to be pulled")
            except Exception:
                st.error("❌ Cannot connect to Ollama. Is it running?")
        elif provider_type == "OpenAI (Cloud)":
            from llm_providers import OpenAIProvider
            test_provider = OpenAIProvider()
            if test_provider.is_available():
                st.success("✅ OpenAI API key configured")
            else:
                st.warning("⚠️ Set OPENAI_API_KEY in Streamlit secrets or environment")
        else:
            # Check Claude availability
            test_provider = AnthropicProvider()
            if test_provider.is_available():
                st.success("✅ Claude API key configured")
            else:
                st.warning("⚠️ Set ANTHROPIC_API_KEY environment variable")

# Main content: Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Platform Scores", "🌐 Live Data", "📋 Ontology", "🏗️ Recommended Stacks", "📄 Report"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: Platform Scores
# ─────────────────────────────────────────────────────────────────────────────

with tab1:
    st.header("Platform Capability Scores")
    
    if eval_method == "Quick Score (Local)":
        st.info("Using pre-populated capability scores. Adjust in sidebar to see impact.")
        
        # Calculate composite scores
        scores_df = []
        for platform_name, platform_data in PLATFORMS_DATA.items():
            capability_scores = platform_data["capabilities"]
            
            # Weighted score across selected use cases
            use_case_fit = 0
            for uc_key in selected_use_cases:
                uc_data = CMS_ONTOLOGY["use_cases"][uc_key]
                uc_score = 0
                count = 0
                for cap_key, required_level in uc_data["required_capabilities"].items():
                    actual_level = capability_scores.get(cap_key, 0)
                    uc_score += (actual_level / required_level) if required_level > 0 else 0
                    count += 1
                use_case_fit += (uc_score / count) if count > 0 else 0
            
            use_case_fit = (use_case_fit / len(selected_use_cases)) if selected_use_cases else 0
            
            # Business outcome fit (simplified: average capabilities)
            avg_capability = sum(capability_scores.values()) / len(capability_scores)
            business_fit = min(avg_capability / 3.0, 1.0)  # Normalize to 0-1
            
            composite_score = (use_case_fit * 0.6 + business_fit * 0.4)
            
            scores_df.append({
                "Platform": platform_name,
                "Type": platform_data["type"],
                "Category": platform_data["category"],
                "Use Case Fit": round(use_case_fit, 2),
                "Business Fit": round(business_fit, 2),
                "Composite Score": round(composite_score, 2),
                "Cost Band": platform_data["cost_band"],
                "Support": platform_data["capabilities"]["operational"]
            })
        
        scores_df = pd.DataFrame(scores_df).sort_values("Composite Score", ascending=False)
        
        # Display in columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(
                scores_df.style.format({
                    "Use Case Fit": "{:.2f}",
                    "Business Fit": "{:.2f}",
                    "Composite Score": "{:.2f}"
                }).highlight_max(subset=["Composite Score"], color="lightgreen"),
                use_container_width=True
            )
        
        with col2:
            st.markdown("### Top 3 Platforms")
            for idx, row in scores_df.head(3).iterrows():
                st.metric(
                    row["Platform"],
                    f"{row['Composite Score']:.2f}",
                    f"{row['Category']}"
                )
    
    else:  # AI-Powered Analysis
        # Get provider based on sidebar selection
        if provider_type == "Ollama (Local)":
            provider = get_provider("ollama", model=ollama_model, host=ollama_host)
        elif provider_type == "OpenAI (Cloud)":
            provider = get_provider("openai")
        else:  # Claude
            provider = get_provider("anthropic")
        st.info(f"🤖 Using {provider.name} for structured assessments...")
        
        if st.button("Run AI Analysis"):
            with st.spinner(f"Analyzing with {provider.name}..."):
                try:
                    assessment_schema = {
                        "type": "object",
                        "properties": {
                            "platform": {"type": "string"},
                            "overall_fit_score": {"type": "number"},
                            "strengths": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "weaknesses": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "best_for_use_case": {"type": "string"}
                        },
                        "required": ["platform", "overall_fit_score", "strengths", "weaknesses", "best_for_use_case"]
                    }
                    
                    prompt = f"""
You are a CMS evaluation expert. Assess the following CMS platform against CINCH's requirements:
- 20K+ paid views/day, 6K-7K unique visitors
- Need to improve conversions and drive enrollments
- Currently spread across 5 CMS (HubSpot, Liferay, Ion, Starmark, Surefire)
- Want to consolidate but accept 3-platform reality
- Avoid Sitecore-scale monolith, avoid lightweight/free tools
- Interested in headless/composable approach

Platforms to assess: {', '.join(PLATFORMS_DATA.keys())}

For each platform:
1. Provide an overall fit score (0-1) where 1 is perfect fit
2. List 3 key strengths relative to CINCH needs
3. List 3 key weaknesses
4. Identify the best use case it supports for CINCH

Return as structured JSON matching the schema provided.
"""
                    
                    response = provider.chat(prompt, assessment_schema)
                    assessments = response.content
                    
                    st.success(f"✅ AI Analysis Complete (via {response.provider})")
                    st.json(assessments)
                    
                except Exception as e:
                    st.error(f"Error calling {provider.name}: {e}")
                    if provider_type == "Ollama (Local)":
                        st.info("💡 Tips: Make sure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull " + ollama_model + "`).")
                    else:
                        st.info("💡 Tip: Make sure your ANTHROPIC_API_KEY is set as an environment variable.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: Live Data Fetching
# ─────────────────────────────────────────────────────────────────────────────

with tab2:
    st.header("🌐 Fetch Live Vendor Data")
    st.markdown("**Scrape real vendor documentation and extract capabilities using AI**")
    
    # Initialize session state for fetched data
    if 'live_vendor_data' not in st.session_state:
        st.session_state.live_vendor_data = {}
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        vendor_to_fetch = st.selectbox(
            "Select vendor to fetch:",
            options=["contentful", "sanity", "hubspot", "sitecore", "acquia"],
            help="Choose a vendor to scrape documentation from"
        )
    
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        fetch_button = st.button("🔍 Fetch Live Data", type="primary")
    
    if fetch_button:
        try:
            from data_agents import CMSDataAgent
            
            # Progress bar with steps
            progress = st.progress(0, text="Initializing...")
            status = st.empty()
            
            # Step 1: Initialize
            status.info("🚀 Starting browser...")
            progress.progress(10, text="Launching Playwright browser...")
            
            # Get provider
            if eval_method == "AI-Powered Analysis" and provider_type == "Ollama (Local)":
                agent_provider = get_provider("ollama", model=ollama_model, host=ollama_host)
            else:
                agent_provider = get_provider("ollama")
            
            agent = CMSDataAgent(provider=agent_provider)
            
            # Step 2: Scrape
            progress.progress(25, text=f"Scraping {vendor_to_fetch} documentation...")
            status.info(f"🌐 Scraping {vendor_to_fetch} website...")
            
            raw_content = asyncio.run(agent.scrape_vendor(vendor_to_fetch))
            
            # Step 3: AI Extraction
            progress.progress(60, text="AI extracting capabilities (this takes ~30s)...")
            status.info("🤖 Ollama analyzing content...")
            
            extracted = agent.extract_capabilities(vendor_to_fetch, raw_content)
            
            # Step 4: Package results
            progress.progress(90, text="Packaging results...")
            
            from data_agents import VendorData
            data = VendorData(
                platform=vendor_to_fetch,
                capabilities=extracted.get("capabilities", {}),
                pricing_info=extracted.get("pricing_tier", "Unknown"),
                features=extracted.get("key_features", []),
                source_urls=agent.VENDOR_DOCS.get(vendor_to_fetch.lower(), []),
                raw_content=raw_content[:5000]
            )
            
            # Done
            progress.progress(100, text="✅ Complete!")
            status.success(f"✅ Fetched live data for {vendor_to_fetch}!")
            
            # Store in session state
            st.session_state.live_vendor_data[vendor_to_fetch] = data
            
            # Cleanup
            asyncio.run(agent.close())
            
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            st.info("💡 Make sure Ollama is running and Playwright browsers are installed.")
    
    # Display fetched data
    if st.session_state.live_vendor_data:
        st.markdown("---")
        st.subheader("📊 Fetched Vendor Data")
        
        for vendor, data in st.session_state.live_vendor_data.items():
            with st.expander(f"**{vendor.title()}** - Live Data", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Capabilities (0-3):**")
                    caps_df = pd.DataFrame([
                        {"Capability": k.replace("_", " ").title(), "Score": v}
                        for k, v in data.capabilities.items()
                    ])
                    st.dataframe(caps_df, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("**Key Features:**")
                    for feat in data.features[:5]:
                        st.write(f"• {feat[:100]}..." if len(feat) > 100 else f"• {feat}")
                
                st.markdown(f"**Sources:** {', '.join(data.source_urls)}")
        
        # Option to use live data in scoring
        if st.button("📥 Use Live Data in Platform Scores"):
            for vendor, data in st.session_state.live_vendor_data.items():
                vendor_key = vendor.title()
                if vendor_key in PLATFORMS_DATA:
                    PLATFORMS_DATA[vendor_key]["capabilities"] = data.capabilities
                    st.success(f"Updated {vendor_key} with live data!")
            st.info("👈 Switch to 'Platform Scores' tab to see updated rankings.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: Ontology Browser
# ─────────────────────────────────────────────────────────────────────────────

with tab3:
    st.header("CMS Ontology")
    st.markdown("**Structured capability model used for evaluation**")
    
    ontology_view = st.radio("View:", ["Capabilities", "Use Cases", "Business Outcomes"])
    
    if ontology_view == "Capabilities":
        for cap_key, cap_data in CMS_ONTOLOGY["capabilities"].items():
            with st.expander(f"🔹 {cap_data['label']} (Importance: {cap_data['importance']})"):
                st.markdown(f"**Scale:** {cap_data['scale']}")
                st.markdown(f"**Facets:**")
                for facet in cap_data["facets"]:
                    st.write(f"  • {facet.replace('_', ' ').title()}")
    
    elif ontology_view == "Use Cases":
        for uc_key, uc_data in CMS_ONTOLOGY["use_cases"].items():
            with st.expander(f"📌 {uc_data['label']}"):
                st.markdown("**Required Capabilities:**")
                for cap, level in uc_data["required_capabilities"].items():
                    cap_name = CMS_ONTOLOGY["capabilities"][cap]["label"]
                    st.write(f"  • {cap_name}: Level {level}/3")
    
    else:  # Business Outcomes
        outcome_weights_df = pd.DataFrame([
            {
                "Outcome": outcome["label"],
                "Weight": outcome["weight"],
                "Normalized": f"{(outcome['weight'] / sum(o['weight'] for o in CMS_ONTOLOGY['business_outcomes'].values())) * 100:.1f}%"
            }
            for outcome in CMS_ONTOLOGY["business_outcomes"].values()
        ])
        st.dataframe(outcome_weights_df, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: Recommended Stacks
# ─────────────────────────────────────────────────────────────────────────────

with tab4:
    st.header("Recommended Architecture Patterns")
    
    st.markdown("### Option A: HubSpot + Headless CMS for Experimentation")
    col1, col2 = st.columns(2)
    with col1:
        st.write("""
**Stack:**
- HubSpot: CRM + marketing automation
- Contentful/Sanity: Headless CMS for enrollment content
- Optimizely/VWO: Dedicated A/B testing layer

**Pros:**
✅ Leverage HubSpot CRM investment
✅ Fast experimentation on landing pages
✅ Decoupled front-end = flexible design

**Cons:**
❌ 3-platform coordination
❌ Content still fragmented
        """)
    with col2:
        st.metric("Fit Score", "0.72", "Good fit for paid funnel")
    
    st.markdown("---")
    
    st.markdown("### Option B: Pure Headless + Personalization Platform")
    col1, col2 = st.columns(2)
    with col1:
        st.write("""
**Stack:**
- Contentful: Primary headless CMS
- Segment/mParticle: CDP for personalization
- Any front-end (Next.js, etc.)
- HubSpot: CRM only

**Pros:**
✅ True headless architecture
✅ Best content flexibility
✅ Omnichannel ready
✅ Modern DX for developers

**Cons:**
❌ Requires front-end team
❌ No native A/B testing
        """)
    with col2:
        st.metric("Fit Score", "0.85", "Best for long-term flexibility")
    
    st.markdown("---")
    
    st.markdown("### Option C: Composable CMS (All-in-one modern approach)")
    col1, col2 = st.columns(2)
    with col1:
        st.write("""
**Stack:**
- Composable CMS (Acquia/Agility): Headless + native personalization
- HubSpot: CRM + marketing automation
- CDN: Performance layer

**Pros:**
✅ Unified content + experimentation
✅ SaaS simplicity
✅ Omnichannel by design
✅ Strong vendor support

**Cons:**
❌ Higher cost
❌ Newer ecosystem
        """)
    with col2:
        st.metric("Fit Score", "0.88", "Balanced & modern")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: Report
# ─────────────────────────────────────────────────────────────────────────────

with tab5:
    st.header("📄 Evaluation Report")
    
    report_format = st.radio("Export Format:", ["View in Streamlit", "Generate DOCX"])
    
    if report_format == "View in Streamlit":
        st.markdown(f"""
## CINCH CMS Evaluation Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Executive Summary
CINCH is evaluating headless and composable CMS solutions to consolidate 5 legacy platforms (HubSpot, Liferay, Ion, Starmark, Surefire) into 3 unified platforms. The primary goal is to improve conversion optimization and enrollment rates for a site receiving ~20K paid views/day.

### Key Findings
- **Best overall fit: Composable CMS + HubSpot CRM**
- **Best headless-only fit: Contentful**
- **Best for quick wins: HubSpot + Headless hybrid**

### Selected Use Cases
{', '.join(CMS_ONTOLOGY['use_cases'][uc]['label'] for uc in selected_use_cases)}

### Recommendation
Pursue **Option B (Pure Headless)** for long-term flexibility and modern DX, with a phased migration from legacy systems.
        """)
    
    else:
        st.info("📥 DOCX export feature coming soon. Use 'View in Streamlit' to see the report content.")
        if st.button("Generate DOCX Report"):
            st.write("Install python-docx to enable DOCX export: `pip install python-docx`")

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("""
**Built with:** Python, Streamlit, Ollama, Playwright  
**Ontology Version:** 1.0  
**Last Updated:** 2025-12-11
""")
