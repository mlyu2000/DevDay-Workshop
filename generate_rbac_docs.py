#!/usr/bin/env python3
"""
generate_rbac_docs.py
=====================
Generates 12 mixed-classification documents + JWT tokens for LAB 4A.

Run this BEFORE launching the notebook:
    python generate_rbac_docs.py
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — edit these to match your environment
# ══════════════════════════════════════════════════════════════════════════════
DOCS_DIR   = Path("/mnt/shared/workshop/rbac_docs")
TOKENS_DIR = Path("/mnt/shared/workshop/tokens")
JWT_SECRET = "hpe-workshop-secret-2026"
JWT_ALGO   = "HS256"
# ══════════════════════════════════════════════════════════════════════════════

DOCS_DIR.mkdir(parents=True, exist_ok=True)
TOKENS_DIR.mkdir(parents=True, exist_ok=True)

DOCUMENTS = [
    # ── Level 1 — Public ──────────────────────────────────────────────────────
    {
        "filename": "doc_01_public_product_overview.txt",
        "access_level": 1, "department": "public",
        "classification": "public", "owner": "marketing-team",
        "content": (
            "Product Overview — Public Edition\n\n"
            "Our platform provides cloud-native AI solutions for enterprise customers. "
            "Key features include automated model deployment, real-time inference, and "
            "integrated monitoring dashboards. All public-tier users can access product "
            "documentation, release notes, and community forums. "
            "Contact sales@company.com for pricing information."
        ),
    },
    {
        "filename": "doc_02_public_faq.txt",
        "access_level": 1, "department": "public",
        "classification": "public", "owner": "support-team",
        "content": (
            "Frequently Asked Questions — Public\n\n"
            "Q: What is the free tier limit?\n"
            "A: The free tier allows up to 1,000 API calls per month.\n\n"
            "Q: How do I reset my password?\n"
            "A: Visit the login page and click 'Forgot Password'.\n\n"
            "Q: Is there a mobile app?\n"
            "A: Yes, available on iOS and Android.\n\n"
            "Q: What SLA do you offer?\n"
            "A: Public tier has 99.5% uptime SLA."
        ),
    },
    {
        "filename": "doc_03_public_release_notes.txt",
        "access_level": 1, "department": "public",
        "classification": "public", "owner": "engineering-team",
        "content": (
            "Release Notes v3.2.0 — Public\n\n"
            "New Features:\n"
            "- Improved dashboard load time by 40%\n"
            "- Added support for Python 3.12\n"
            "- New REST API endpoints for batch processing\n\n"
            "Bug Fixes:\n"
            "- Fixed authentication timeout issue\n"
            "- Resolved CSV export encoding bug\n\n"
            "Deprecations:\n"
            "- Legacy v1 API endpoints will be removed in v4.0"
        ),
    },
    # ── Level 2 — Internal ────────────────────────────────────────────────────
    {
        "filename": "doc_04_internal_engineering_roadmap.txt",
        "access_level": 2, "department": "engineering",
        "classification": "internal", "owner": "engineering-team",
        "content": (
            "Engineering Roadmap — Internal Use Only\n\n"
            "Q1 2025: Complete migration to Kubernetes 1.29. "
            "Introduce multi-region failover for inference endpoints.\n\n"
            "Q2 2025: Launch internal developer portal. "
            "Integrate automated security scanning in CI/CD pipeline.\n\n"
            "Q3 2025: Begin evaluation of next-generation GPU clusters. "
            "Target: 3x throughput improvement for batch inference jobs.\n\n"
            "Q4 2025: Full rollout of internal observability stack using OpenTelemetry."
        ),
    },
    {
        "filename": "doc_05_internal_product_strategy.txt",
        "access_level": 2, "department": "product",
        "classification": "internal", "owner": "product-team",
        "content": (
            "Product Strategy 2025 — Internal\n\n"
            "Strategic Pillars:\n"
            "1. Expand enterprise AI adoption through simplified onboarding.\n"
            "2. Build a partner ecosystem with 50+ integrations by EOY.\n"
            "3. Achieve SOC2 Type II certification by Q2 2025.\n\n"
            "Target Markets: Financial services, healthcare, and government sectors.\n\n"
            "Competitive Positioning: Focus on data residency and compliance "
            "as primary differentiators against hyperscaler offerings."
        ),
    },
    {
        "filename": "doc_06_internal_hr_policies.txt",
        "access_level": 2, "department": "engineering",
        "classification": "internal", "owner": "hr-team",
        "content": (
            "HR Policies — Internal Staff Reference\n\n"
            "Leave Policy: All full-time employees receive 20 days PTO annually. "
            "Unused PTO rolls over up to 5 days.\n\n"
            "Remote Work: Employees may work remotely up to 3 days per week "
            "with manager approval.\n\n"
            "Performance Reviews: Conducted bi-annually in June and December.\n\n"
            "Training Budget: Each employee receives $2,000 annually for "
            "professional development."
        ),
    },
    # ── Level 3 — Confidential ────────────────────────────────────────────────
    {
        "filename": "doc_07_confidential_finance_budget.txt",
        "access_level": 3, "department": "finance",
        "classification": "confidential", "owner": "finance-team",
        "content": (
            "Annual Budget Report 2025 — Confidential\n\n"
            "Total Operating Budget: $48.5M\n"
            "R&D Allocation: $12.2M (25.2%)\n"
            "Sales & Marketing: $9.8M (20.2%)\n"
            "Infrastructure & Cloud: $7.1M (14.6%)\n"
            "Headcount Costs: $19.4M (40%)\n\n"
            "Q1 Burn Rate: $11.2M (within 3% of forecast)\n"
            "Projected EBITDA: $6.3M by Q4 2025\n\n"
            "Note: This document is restricted to Finance, HR, and Engineering "
            "leadership only."
        ),
    },
    {
        "filename": "doc_08_confidential_hr_compensation_bands.txt",
        "access_level": 3, "department": "hr",
        "classification": "confidential", "owner": "hr-team",
        "content": (
            "Compensation Bands 2025 — Confidential\n\n"
            "Engineering Compensation Ranges:\n"
            "- Junior Engineer  (L1): $75,000  – $95,000\n"
            "- Mid-level Engineer (L2): $95,000 – $125,000\n"
            "- Senior Engineer  (L3): $125,000 – $160,000\n"
            "- Staff Engineer   (L4): $160,000 – $200,000\n\n"
            "Product Management:\n"
            "- Associate PM: $80,000 – $105,000\n"
            "- Senior PM:    $120,000 – $155,000\n\n"
            "Engineering compensation ranges from $75,000 to $200,000 "
            "depending on level and specialization."
        ),
    },
    {
        "filename": "doc_09_confidential_engineering_security.txt",
        "access_level": 3, "department": "engineering",
        "classification": "confidential", "owner": "security-team",
        "content": (
            "Security Architecture — Confidential\n\n"
            "Authentication: All internal services use mTLS with 90-day cert rotation.\n"
            "Secrets Management: HashiCorp Vault with dynamic secrets for DB credentials.\n"
            "Network Segmentation: Production environment isolated in dedicated VPC "
            "with zero-trust network access policy.\n\n"
            "Vulnerability Management: Weekly automated scans via Trivy and Snyk. "
            "Critical CVEs patched within 24 hours.\n\n"
            "Incident Response: SOC team on-call 24/7 with 15-minute response SLA."
        ),
    },
    # ── Level 4 — Restricted ──────────────────────────────────────────────────
    {
        "filename": "doc_10_restricted_executive_compensation.txt",
        "access_level": 4, "department": "hr",
        "classification": "restricted", "owner": "executive-team",
        "content": (
            "Executive Compensation Policy 2025 — RESTRICTED\n\n"
            "C-Suite Base Salaries:\n"
            "- Chief Executive Officer: $420,000 base + 40% performance bonus\n"
            "- Chief Technology Officer: $380,000 base + 35% performance bonus\n"
            "- Chief Financial Officer: $360,000 base + 35% performance bonus\n\n"
            "Senior Engineer Band (Executive Track):\n"
            "The Senior Engineer band is $145,000–$185,000 with equity grants "
            "of 0.05%–0.15% vesting over 4 years.\n\n"
            "Board-approved equity pool: 12% of fully diluted shares.\n"
            "Long-term incentive plan (LTIP): Top 5% performers eligible for "
            "additional RSU grants of $50,000–$200,000 annually."
        ),
    },
    {
        "filename": "doc_11_restricted_ma_strategy.txt",
        "access_level": 4, "department": "finance",
        "classification": "restricted", "owner": "executive-team",
        "content": (
            "M&A Strategy 2025 — RESTRICTED — Board Eyes Only\n\n"
            "Target Acquisition Profile:\n"
            "- AI infrastructure companies with ARR $5M–$50M\n"
            "- Data annotation and synthetic data generation platforms\n"
            "- Vertical AI solutions in healthcare and fintech\n\n"
            "Budget Allocated for Acquisitions: $85M (approved by board Q4 2024)\n\n"
            "Pipeline (Confidential):\n"
            "- Target A: Due diligence in progress, estimated valuation $22M\n"
            "- Target B: Initial conversations, ARR $8M, strong IP portfolio\n\n"
            "This document must not be shared outside the executive team and "
            "legal counsel."
        ),
    },
    {
        "filename": "doc_12_restricted_legal_compliance.txt",
        "access_level": 4, "department": "hr",
        "classification": "restricted", "owner": "legal-team",
        "content": (
            "Legal & Compliance Report — RESTRICTED\n\n"
            "Active Litigation: 2 cases in arbitration (details sealed).\n\n"
            "Regulatory Compliance Status:\n"
            "- GDPR: Compliant as of March 2025 audit\n"
            "- SOC2 Type II: Certification in progress, expected Q2 2025\n"
            "- HIPAA: BAA signed with 3 healthcare clients\n\n"
            "IP Portfolio: 14 patents filed, 6 granted.\n\n"
            "Employment Law: 0 open EEOC complaints. Last audit: January 2025.\n\n"
            "This document is restricted to HR leadership, Legal, and C-Suite only."
        ),
    },
]


def generate_documents():
    ingested_at = datetime.now(timezone.utc).isoformat()
    level_label = {1: "PUBLIC", 2: "INTERNAL", 3: "CONFIDENTIAL", 4: "RESTRICTED"}
    for doc in DOCUMENTS:
        (DOCS_DIR / doc["filename"]).write_text(doc["content"], encoding="utf-8")
        meta = {
            "access_level":   doc["access_level"],
            "department":     doc["department"],
            "classification": doc["classification"],
            "owner":          doc["owner"],
            "ingested_at":    ingested_at,
            "source_file":    doc["filename"],
        }
        meta_path = DOCS_DIR / doc["filename"].replace(".txt", ".meta.json")
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print(f"  📄 [{level_label[doc['access_level']]:>12}]  "
              f"dept={doc['department']:<12}  {doc['filename']}")
    print(f"\n  ✅ {len(DOCUMENTS)} documents written to {DOCS_DIR}")


def generate_tokens():
    try:
        import jwt as pyjwt
    except ImportError:
        print("⚠  PyJWT not installed. Run: pip install PyJWT")
        return

    roles = [
        {"user_id": "user_admin_001",    "role": "admin",    "dept": "all"},
        {"user_id": "user_manager_002",  "role": "manager",  "dept": "finance"},
        {"user_id": "user_employee_003", "role": "employee", "dept": "engineering"},
        {"user_id": "user_guest_004",    "role": "guest",    "dept": "public"},
    ]
    for payload in roles:
        token = pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        token_path = TOKENS_DIR / f"{payload['role']}_token.jwt"
        token_path.write_text(token)
        print(f"  ✅ Token written: {token_path}")
    print(f"\n  🔑 JWT Secret : {JWT_SECRET}")
    print("  ⚠  Workshop use only — never use this secret in production.\n")


if __name__ == "__main__":
    print("\n" + "=" * 62)
    print("  LAB 4A — RBAC Document & Token Generator")
    print("=" * 62 + "\n")
    print("📁 Generating documents...")
    generate_documents()
    print("\n🔑 Generating JWT tokens...")
    generate_tokens()
    print("=" * 62)
    print("  ✅ Setup complete. Launch 04_lab.ipynb to begin.")
    print("=" * 62 + "\n")
