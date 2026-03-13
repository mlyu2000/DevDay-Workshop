#!/usr/bin/env python3
"""
generate_query_log.py
=====================
Generates a realistic synthetic query_log.csv file for Lab 3A.

The dataset simulates 500 queries submitted to an enterprise RAG system
covering HPE Private Cloud AI documentation. It contains deliberate
content gaps in 3 topic clusters to ensure the lab analysis produces
meaningful diagnostic results.

Usage:
    python generate_query_log.py
    python generate_query_log.py --output /data/workshop/query_log.csv
    python generate_query_log.py --rows 500 --seed 42 --output ./query_log.csv

Output columns:
    query_text       - Raw query string
    timestamp        - UTC ISO-8601 timestamp
    user_id          - Anonymised user identifier (usr_XXXX)
    retrieval_score  - Top-1 cosine similarity score (0.0-1.0)
    session_id       - Session grouping identifier (ses_XXXX)
"""

import argparse
import csv
import os
import random
import uuid
from datetime import datetime, timedelta, timezone


# ============================================================
# TOPIC DEFINITIONS
# Each topic has:
#   - queries     : list of realistic query strings
#   - score_range : (min, max) retrieval score range
#   - weight      : relative frequency in the dataset
#   - gap         : True = deliberate content gap cluster
# ============================================================

TOPICS = [
    # ----------------------------------------------------------------
    # TOPIC 0 — HPE Hardware Installation (WELL COVERED — high scores)
    # ----------------------------------------------------------------
    {
        "name": "HPE Hardware Installation",
        "gap": False,
        "weight": 12,
        "score_range": (0.72, 0.97),
        "queries": [
            "How do I install a DL380 Gen10 in a rack?",
            "What are the steps to seat a DIMM in a ProLiant server?",
            "How do I connect the iLO management port on a DL360?",
            "What torque setting should I use for HPE rack screws?",
            "How do I install a hot-plug drive in an MSA storage array?",
            "What is the correct procedure for replacing a power supply in a DL380?",
            "How do I install the HPE Smart Array controller?",
            "What cables are needed for HPE Synergy frame interconnects?",
            "How do I mount the HPE ProLiant DL20 in a short-depth rack?",
            "What is the process for installing an HPE NVMe drive?",
            "How do I replace a fan module in a ProLiant ML350?",
            "What are the rack unit requirements for an HPE Apollo server?",
            "How do I install HPE Persistent Memory DIMMs?",
            "What is the correct orientation for HPE hot-plug drive bays?",
            "How do I connect dual power supplies for redundancy on a DL580?",
            "What is the process for installing an HPE FlexibleLOM adapter?",
            "How do I install a GPU in an HPE ProLiant DL380 Gen10 Plus?",
            "What are the steps to install HPE SmartMemory?",
            "How do I replace the system board in a ProLiant DL360 Gen10?",
            "What is the procedure for installing an HPE OCP NIC?",
        ],
    },
    # ----------------------------------------------------------------
    # TOPIC 1 — iLO Configuration (WELL COVERED — high scores)
    # ----------------------------------------------------------------
    {
        "name": "iLO Configuration",
        "gap": False,
        "weight": 12,
        "score_range": (0.68, 0.95),
        "queries": [
            "How do I configure iLO 5 for remote management?",
            "What is the default iLO username and password?",
            "How do I enable iLO Advanced features?",
            "How do I configure iLO SNMP alerts?",
            "What is the process for updating iLO firmware?",
            "How do I set up iLO federation for multiple servers?",
            "How do I configure iLO for Active Directory authentication?",
            "What ports does iLO use for remote console access?",
            "How do I generate an iLO SSL certificate?",
            "How do I configure iLO power capping?",
            "What is the iLO RESTful API endpoint for server health?",
            "How do I enable iLO virtual media?",
            "How do I configure iLO IPMI over LAN?",
            "What is the process for resetting iLO to factory defaults?",
            "How do I configure iLO email alerting?",
            "How do I enable iLO Agentless Management?",
            "What is the iLO Amplifier Pack and how do I install it?",
            "How do I configure iLO for two-factor authentication?",
            "How do I access the iLO Integrated Remote Console?",
            "What are the iLO network configuration best practices?",
        ],
    },
    # ----------------------------------------------------------------
    # TOPIC 2 — HPE Greenlake Cloud (WELL COVERED — high scores)
    # ----------------------------------------------------------------
    {
        "name": "HPE GreenLake Cloud",
        "gap": False,
        "weight": 11,
        "score_range": (0.65, 0.93),
        "queries": [
            "How do I provision a new workload in HPE GreenLake?",
            "What is the HPE GreenLake Central dashboard?",
            "How do I set up HPE GreenLake for Private Cloud?",
            "What consumption metrics does HPE GreenLake track?",
            "How do I add a new user to HPE GreenLake Central?",
            "What is the HPE GreenLake service catalog?",
            "How do I configure HPE GreenLake billing alerts?",
            "What SLAs are available in HPE GreenLake?",
            "How do I connect on-premises infrastructure to HPE GreenLake?",
            "What is the HPE GreenLake edge-to-cloud platform?",
            "How do I deploy a VM in HPE GreenLake for Private Cloud?",
            "What is the HPE GreenLake Flex Capacity model?",
            "How do I monitor resource utilisation in HPE GreenLake?",
            "What is the process for scaling up HPE GreenLake capacity?",
            "How do I configure HPE GreenLake networking?",
            "What security certifications does HPE GreenLake hold?",
            "How do I integrate HPE GreenLake with ServiceNow?",
            "What is HPE GreenLake for Compute Ops Management?",
            "How do I set up role-based access control in HPE GreenLake?",
            "What is the HPE GreenLake for ML Ops service?",
        ],
    },
    # ----------------------------------------------------------------
    # TOPIC 3 — Kubernetes on HPE (WELL COVERED — high scores)
    # ----------------------------------------------------------------
    {
        "name": "Kubernetes on HPE",
        "gap": False,
        "weight": 11,
        "score_range": (0.63, 0.92),
        "queries": [
            "How do I deploy a Kubernetes cluster on HPE Ezmeral?",
            "What is HPE Ezmeral Runtime Enterprise?",
            "How do I configure persistent storage for Kubernetes on HPE?",
            "What is the process for upgrading an HPE Ezmeral cluster?",
            "How do I integrate HPE Ezmeral with Active Directory?",
            "What networking CNI plugins are supported on HPE Ezmeral?",
            "How do I configure autoscaling in HPE Ezmeral?",
            "What is the HPE CSI driver for Kubernetes?",
            "How do I deploy a GPU workload on HPE Ezmeral?",
            "What monitoring tools are available for HPE Ezmeral?",
            "How do I configure ingress on an HPE Ezmeral cluster?",
            "What is the HPE Ezmeral Data Fabric?",
            "How do I back up an HPE Ezmeral Kubernetes cluster?",
            "What is the process for adding worker nodes to HPE Ezmeral?",
            "How do I configure RBAC in HPE Ezmeral Runtime?",
            "What is the HPE Ezmeral unified analytics platform?",
            "How do I deploy Spark on HPE Ezmeral?",
            "What is the HPE Ezmeral MLOps pipeline?",
            "How do I configure namespace isolation in HPE Ezmeral?",
            "What are the HPE Ezmeral system requirements?",
        ],
    },
    # ----------------------------------------------------------------
    # TOPIC 4 — Storage Administration (WELL COVERED — high scores)
    # ----------------------------------------------------------------
    {
        "name": "Storage Administration",
        "gap": False,
        "weight": 10,
        "score_range": (0.61, 0.91),
        "queries": [
            "How do I create a volume on HPE Nimble Storage?",
            "What is the process for expanding an HPE 3PAR volume?",
            "How do I configure replication on HPE Primera?",
            "What is HPE InfoSight and how does it work?",
            "How do I set up tiered storage on HPE Alletra?",
            "What is the process for taking a snapshot on HPE Nimble?",
            "How do I configure iSCSI on HPE MSA storage?",
            "What are the best practices for HPE 3PAR zoning?",
            "How do I monitor HPE Primera performance?",
            "What is the HPE Alletra dHCI architecture?",
            "How do I configure HPE Nimble replication groups?",
            "What is the process for HPE Primera array upgrade?",
            "How do I set up HPE StoreOnce for backup?",
            "What is the HPE Nimble Storage predictive flash platform?",
            "How do I configure QoS policies on HPE Alletra?",
            "What is the process for HPE MSA volume migration?",
            "How do I configure HPE Primera for VMware integration?",
            "What are the HPE Nimble Storage best practices for SQL Server?",
            "How do I set up HPE Alletra for Kubernetes persistent volumes?",
            "What is the HPE Primera peer persistence feature?",
        ],
    },
    # ----------------------------------------------------------------
    # TOPIC 5 — FINANCIAL REPORTING (GAP CLUSTER 1 — low scores)
    # Corpus has no financial documents.
    # ----------------------------------------------------------------
    {
        "name": "Financial Reporting",
        "gap": True,
        "weight": 8,
        "score_range": (0.18, 0.46),
        "queries": [
            "What was HPE revenue in Q3 fiscal year 2024?",
            "How do I access the HPE annual report for 2023?",
            "What is HPE gross margin for the last fiscal quarter?",
            "Where can I find HPE earnings per share data?",
            "What is the HPE dividend payment schedule?",
            "How do I download the HPE 10-K filing?",
            "What is HPE operating income for fiscal year 2024?",
            "Where are HPE investor relations contacts listed?",
            "What is the HPE stock buyback programme value?",
            "How do I find HPE segment revenue breakdown by business unit?",
            "What is HPE free cash flow for the last four quarters?",
            "Where can I find the HPE proxy statement for 2024?",
            "What is the HPE capital expenditure forecast?",
            "How do I access HPE earnings call transcripts?",
            "What is HPE debt-to-equity ratio?",
            "Where can I find HPE financial guidance for next fiscal year?",
            "What is the HPE return on invested capital?",
            "How do I find HPE revenue by geographic region?",
            "What is HPE EBITDA for the most recent quarter?",
            "Where can I find HPE pension liability disclosures?",
        ],
    },
    # ----------------------------------------------------------------
    # TOPIC 6 — HR AND EMPLOYEE POLICIES (GAP CLUSTER 2 — low scores)
    # Corpus has no HR policy documents.
    # ----------------------------------------------------------------
    {
        "name": "HR and Employee Policies",
        "gap": True,
        "weight": 8,
        "score_range": (0.15, 0.44),
        "queries": [
            "What is the HPE parental leave policy?",
            "How many vacation days do HPE employees receive?",
            "What is the HPE remote work policy for 2024?",
            "How do I submit an expense report in HPE Workday?",
            "What is the HPE employee stock purchase plan?",
            "How do I request a leave of absence at HPE?",
            "What is the HPE performance review cycle?",
            "How do I access HPE employee benefits portal?",
            "What is the HPE tuition reimbursement policy?",
            "How do I update my direct deposit information in HPE HR?",
            "What is the HPE code of conduct policy?",
            "How do I report a workplace concern at HPE?",
            "What is the HPE health insurance open enrollment period?",
            "How do I access my HPE pay stub online?",
            "What is the HPE 401k matching contribution rate?",
            "How do I apply for an internal transfer at HPE?",
            "What is the HPE flexible working hours policy?",
            "How do I access HPE learning and development courses?",
            "What is the HPE sabbatical leave eligibility?",
            "How do I nominate a colleague for an HPE recognition award?",
        ],
    },
    # ----------------------------------------------------------------
    # TOPIC 7 — LEGAL AND COMPLIANCE (GAP CLUSTER 3 — low scores)
    # Corpus has no legal or compliance documents.
    # ----------------------------------------------------------------
    {
        "name": "Legal and Compliance",
        "gap": True,
        "weight": 8,
        "score_range": (0.17, 0.43),
        "queries": [
            "What is the HPE data privacy policy under GDPR?",
            "How do I submit a GDPR data subject access request to HPE?",
            "What is the HPE supplier code of conduct?",
            "How do I report an HPE export control concern?",
            "What certifications does HPE hold for ISO 27001?",
            "What is the HPE anti-bribery and corruption policy?",
            "How do I access the HPE master purchase agreement template?",
            "What is the HPE software licence compliance process?",
            "How do I report an HPE intellectual property concern?",
            "What is the HPE conflict minerals policy?",
            "How do I access HPE terms and conditions for cloud services?",
            "What is the HPE data retention and destruction policy?",
            "How do I submit a legal hold request at HPE?",
            "What is the HPE whistleblower protection policy?",
            "How do I access HPE's standard contractual clauses for data transfer?",
            "What is the HPE modern slavery statement?",
            "How do I find HPE's CCPA privacy notice?",
            "What is the HPE acceptable use policy for IT systems?",
            "How do I access HPE's security vulnerability disclosure policy?",
            "What is the HPE third-party risk management process?",
        ],
    },
    # ----------------------------------------------------------------
    # TOPIC 8 — Networking (MODERATE COVERAGE — medium scores)
    # ----------------------------------------------------------------
    {
        "name": "HPE Networking",
        "gap": False,
        "weight": 10,
        "score_range": (0.55, 0.85),
        "queries": [
            "How do I configure VLANs on an HPE Aruba switch?",
            "What is the process for updating HPE Aruba firmware?",
            "How do I set up HPE Aruba ClearPass for NAC?",
            "What is the HPE Aruba Central cloud management platform?",
            "How do I configure OSPF on an HPE FlexFabric switch?",
            "What is the process for HPE Aruba mesh network deployment?",
            "How do I configure QoS on HPE Aruba switches?",
            "What is the HPE Aruba SD-WAN solution?",
            "How do I set up HPE Aruba 802.1X authentication?",
            "What is the HPE Aruba AirWave network management system?",
            "How do I configure HPE Aruba dynamic segmentation?",
            "What is the process for HPE Aruba access point provisioning?",
            "How do I configure HPE Comware MSTP?",
            "What is the HPE Aruba ESP architecture?",
            "How do I configure HPE Aruba VPN tunnels?",
            "What are the HPE Aruba switch stacking best practices?",
            "How do I configure HPE Aruba for IoT device segmentation?",
            "What is the HPE Aruba network analytics engine?",
            "How do I set up HPE Aruba user role policies?",
            "What is the HPE Aruba IntroSpect UEBA solution?",
        ],
    },
    # ----------------------------------------------------------------
    # TOPIC 9 — Private Cloud AI / ML Ops (WELL COVERED — high scores)
    # ----------------------------------------------------------------
    {
        "name": "Private Cloud AI and MLOps",
        "gap": False,
        "weight": 10,
        "score_range": (0.66, 0.94),
        "queries": [
            "How do I deploy an LLM on HPE Private Cloud AI?",
            "What is the HPE Machine Learning Development Environment?",
            "How do I configure a GPU cluster for training on HPE?",
            "What is the process for model serving on HPE Private Cloud AI?",
            "How do I set up a RAG pipeline on HPE infrastructure?",
            "What vector databases are supported on HPE Private Cloud AI?",
            "How do I monitor model inference latency on HPE?",
            "What is the HPE AI Essentials software stack?",
            "How do I configure distributed training on HPE Ezmeral?",
            "What is the HPE MLDE hyperparameter tuning feature?",
            "How do I deploy Qdrant on HPE Private Cloud AI?",
            "What is the process for fine-tuning an LLM on HPE?",
            "How do I set up model versioning on HPE Private Cloud AI?",
            "What is the HPE AI observability stack?",
            "How do I configure Langfuse on HPE Private Cloud AI?",
            "What is the HPE Private Cloud AI reference architecture?",
            "How do I deploy an embedding model on HPE?",
            "What is the HPE AI model registry?",
            "How do I configure GPU time-slicing on HPE?",
            "What is the HPE Private Cloud AI networking topology?",
        ],
    },
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _weighted_topic_choice(rng: random.Random) -> dict:
    """Select a topic according to its weight."""
    population = []
    for topic in TOPICS:
        population.extend([topic] * topic["weight"])
    return rng.choice(population)


def _generate_score(rng: random.Random, score_range: tuple) -> float:
    """
    Generate a retrieval score within the given range.
    Uses a beta-like distribution to avoid perfectly uniform scores.
    """
    lo, hi = score_range
    # Skew toward the upper end for non-gap topics, lower for gap topics
    raw = rng.betavariate(2.0, 1.5) if hi > 0.55 else rng.betavariate(1.5, 2.5)
    score = lo + raw * (hi - lo)
    return round(min(max(score, 0.0), 1.0), 6)


def _generate_timestamp(
    rng: random.Random,
    start: datetime,
    end: datetime,
) -> str:
    """Generate a random UTC timestamp between start and end."""
    delta   = end - start
    seconds = int(delta.total_seconds())
    offset  = timedelta(seconds=rng.randint(0, seconds))
    ts      = start + offset
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _generate_user_id(rng: random.Random, n_users: int = 40) -> str:
    """Generate an anonymised user ID from a pool of N users."""
    uid = rng.randint(1000, 1000 + n_users - 1)
    return f"usr_{uid}"


def _generate_session_id(rng: random.Random, n_sessions: int = 120) -> str:
    """Generate a session ID from a pool of N sessions."""
    sid = rng.randint(2000, 2000 + n_sessions - 1)
    return f"ses_{sid}"


def _add_query_variation(rng: random.Random, query: str) -> str:
    """
    Apply lightweight surface-form variation to a query so repeated
    queries from the same template look different in the log.
    """
    prefixes = [
        "", "", "",  # most queries have no prefix (natural)
        "Can you explain ",
        "I need help with ",
        "What is the best way to ",
        "Please help me understand ",
        "Quick question: ",
        "How exactly do I ",
        "Could you clarify ",
    ]
    suffixes = [
        "", "", "", "",  # most queries have no suffix
        " — urgent",
        " for production",
        " in our environment",
        " on Gen10 hardware",
        " step by step",
        " using the CLI",
        " via the GUI",
    ]
    prefix = rng.choice(prefixes)
    suffix = rng.choice(suffixes)

    # Lowercase first letter if prefix is added
    if prefix and query[0].isupper():
        query = query[0].lower() + query[1:]

    return f"{prefix}{query}{suffix}"


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_query_log(
    n_rows: int = 500,
    seed: int = 42,
    start_date: str = "2024-09-01",
    end_date: str = "2024-11-30",
) -> list[dict]:
    """
    Generate a synthetic query log as a list of row dicts.

    Parameters
    ----------
    n_rows     : Number of rows to generate (default 500)
    seed       : Random seed for reproducibility
    start_date : Earliest query timestamp (YYYY-MM-DD)
    end_date   : Latest query timestamp (YYYY-MM-DD)

    Returns
    -------
    List of dicts with keys:
        query_text, timestamp, user_id, retrieval_score, session_id
    """
    rng = random.Random(seed)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(
        tzinfo=timezone.utc
    )
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
        tzinfo=timezone.utc
    )

    rows = []

    # Pre-build a pool of (topic, query) pairs with variation applied
    # so we don't repeat identical strings too often
    query_pool = []
    for topic in TOPICS:
        for q in topic["queries"]:
            # Add each query 2-3 times with different surface variations
            for _ in range(rng.randint(2, 4)):
                query_pool.append((topic, _add_query_variation(rng, q)))

    # Shuffle pool
    rng.shuffle(query_pool)
    pool_idx = 0

    for _ in range(n_rows):
        # Alternate between pool draw and fresh weighted selection
        # to ensure good topic coverage without pure repetition
        if pool_idx < len(query_pool) and rng.random() < 0.65:
            topic, query_text = query_pool[pool_idx]
            pool_idx += 1
        else:
            topic = _weighted_topic_choice(rng)
            raw_q = rng.choice(topic["queries"])
            query_text = _add_query_variation(rng, raw_q)

        rows.append({
            "query_text"     : query_text,
            "timestamp"      : _generate_timestamp(rng, start_dt, end_dt),
            "user_id"        : _generate_user_id(rng),
            "retrieval_score": _generate_score(rng, topic["score_range"]),
            "session_id"     : _generate_session_id(rng),
        })

    # Sort by timestamp ascending (realistic log ordering)
    rows.sort(key=lambda r: r["timestamp"])

    return rows


# ============================================================
# VALIDATION
# ============================================================

def validate_query_log(rows: list[dict]) -> None:
    """
    Run basic sanity checks on the generated dataset.
    Raises AssertionError with a descriptive message on failure.
    """
    assert len(rows) > 0, "Dataset is empty."

    required_cols = {"query_text", "timestamp", "user_id",
                     "retrieval_score", "session_id"}
    assert required_cols == set(rows[0].keys()), (
        f"Column mismatch. Expected {required_cols}, got {set(rows[0].keys())}"
    )

    scores = [r["retrieval_score"] for r in rows]
    assert all(0.0 <= s <= 1.0 for s in scores), (
        "One or more retrieval scores are outside [0.0, 1.0]."
    )

    miss_rate = sum(1 for s in scores if s < 0.50) / len(scores)
    assert miss_rate > 0.10, (
        f"Miss rate too low ({miss_rate:.1%}). "
        "Gap clusters may not be detectable."
    )
    assert miss_rate < 0.60, (
        f"Miss rate too high ({miss_rate:.1%}). "
        "Dataset may be unrealistically poor."
    )

    gap_topic_names = [t["name"] for t in TOPICS if t["gap"]]
    gap_queries_in_data = sum(
        1 for r in rows
        if any(
            kw.lower() in r["query_text"].lower()
            for kw in ["revenue", "fiscal", "parental leave",
                       "GDPR", "vacation", "earnings", "10-K",
                       "expense report", "data subject"]
        )
    )
    assert gap_queries_in_data > 20, (
        f"Too few gap-topic queries found ({gap_queries_in_data}). "
        "Check topic weights."
    )

    unique_users = len({r["user_id"] for r in rows})
    assert unique_users >= 10, (
        f"Too few unique users ({unique_users}). "
        "Dataset may not reflect realistic usage patterns."
    )

    print(f"  \u2705 Row count          : {len(rows)}")
    print(f"  \u2705 Columns            : {list(rows[0].keys())}")
    print(f"  \u2705 Score range        : "
          f"{min(scores):.4f} – {max(scores):.4f}")
    print(f"  \u2705 Miss rate (< 0.50) : {miss_rate:.1%}")
    print(f"  \u2705 Unique users       : {unique_users}")
    print(f"  \u2705 Unique sessions    : "
          f"{len({r['session_id'] for r in rows})}")
    print(f"  \u2705 Gap topic queries  : {gap_queries_in_data}")
    print(f"  \u2705 Gap topics         : {gap_topic_names}")
    print(f"  \u2705 Date range         : "
          f"{rows[0]['timestamp']} – {rows[-1]['timestamp']}")


# ============================================================
# WRITE CSV
# ============================================================

def write_csv(rows: list[dict], output_path: str) -> None:
    """Write the row list to a CSV file."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fieldnames = ["query_text", "timestamp", "user_id",
                  "retrieval_score", "session_id"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"  \u2705 Written to         : {output_path}")
    print(f"  \u2705 File size          : {size_kb:.1f} KB")


# ============================================================
# SUMMARY STATISTICS
# ============================================================

def print_topic_summary(rows: list[dict]) -> None:
    """Print per-topic score statistics for verification."""
    print()
    print("=" * 68)
    print("  TOPIC SCORE SUMMARY")
    print("=" * 68)
    print(
        f"  {'Topic':<30} {'N':>5}  {'Mean':>6}  "
        f"{'Min':>6}  {'Max':>6}  {'Gap?':>5}"
    )
    print("  " + "-" * 64)

    # Map topic names to their gap flag for display
    topic_gap_map = {t["name"]: t["gap"] for t in TOPICS}

    # Assign each row to a topic by score range proximity
    # (simple heuristic: use score thresholds)
    topic_buckets: dict[str, list[float]] = {
        t["name"]: [] for t in TOPICS
    }

    for topic in TOPICS:
        lo, hi = topic["score_range"]
        for r in rows:
            s = r["retrieval_score"]
            if lo - 0.05 <= s <= hi + 0.05:
                # Rough bucket assignment — good enough for summary
                pass

    # Better: re-generate with topic labels attached for summary only
    rng_summary = random.Random(42)
    topic_score_samples: dict[str, list[float]] = {
        t["name"]: [] for t in TOPICS
    }
    for r in rows:
        s = r["retrieval_score"]
        # Find which topic's score range this score most likely belongs to
        best_topic = None
        best_dist  = float("inf")
        for t in TOPICS:
            lo, hi  = t["score_range"]
            midpoint = (lo + hi) / 2
            dist     = abs(s - midpoint)
            if dist < best_dist:
                best_dist  = dist
                best_topic = t["name"]
        if best_topic:
            topic_score_samples[best_topic].append(s)

    for topic in TOPICS:
        name   = topic["name"]
        scores = topic_score_samples[name]
        if not scores:
            continue
        mean_s = sum(scores) / len(scores)
        gap    = "\u274c GAP" if topic["gap"] else "\u2705 OK "
        print(
            f"  {name:<30} {len(scores):>5}  {mean_s:>6.3f}  "
            f"{min(scores):>6.3f}  {max(scores):>6.3f}  {gap:>5}"
        )

    print("=" * 68)


# ============================================================
# CLI ENTRY POINT
# ============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic query_log.csv for Lab 3A.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--output", "-o",
        default="/data/workshop/query_log.csv",
        help="Output CSV path (default: /data/workshop/query_log.csv)",
    )
    parser.add_argument(
        "--rows", "-n",
        type=int,
        default=500,
        help="Number of rows to generate (default: 500)",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--start-date",
        default="2024-09-01",
        help="Earliest timestamp YYYY-MM-DD (default: 2024-09-01)",
    )
    parser.add_argument(
        "--end-date",
        default="2024-11-30",
        help="Latest timestamp YYYY-MM-DD (default: 2024-11-30)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print()
    print("=" * 68)
    print("  Lab 3A — Query Log Generator")
    print("=" * 68)
    print(f"  Rows       : {args.rows}")
    print(f"  Seed       : {args.seed}")
    print(f"  Date range : {args.start_date} → {args.end_date}")
    print(f"  Output     : {args.output}")
    print()

    print("Generating rows...")
    rows = generate_query_log(
        n_rows     = args.rows,
        seed       = args.seed,
        start_date = args.start_date,
        end_date   = args.end_date,
    )
    print(f"  Generated {len(rows)} rows.")
    print()

    print("Validating dataset...")
    validate_query_log(rows)
    print()

    print("Writing CSV...")
    write_csv(rows, args.output)
    print()

    print_topic_summary(rows)

    print()
    print("=" * 68)
    print("  \U0001f389 Done! query_log.csv is ready for Lab 3A.")
    print("=" * 68)
    print()
    print("  Expected Lab 3A behaviour:")
    print("  - Miss rate (score < 0.50) should be 20-35%")
    print("  - K-means elbow should be visible near k=8")
    print("  - 3 gap clusters should have mean score < 0.55:")
    print("    \u2022 Financial Reporting    (no corpus coverage)")
    print("    \u2022 HR and Employee Policies (no corpus coverage)")
    print("    \u2022 Legal and Compliance   (no corpus coverage)")
    print()


if __name__ == "__main__":
    main()
