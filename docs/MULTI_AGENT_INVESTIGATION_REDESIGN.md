# Enterprise Multi-Agent Investigation Redesign

## 1. Review of the Current Architecture

The existing implementation already contains the right building blocks for a fraud investigation workflow:

- A feature-engineering and scoring pipeline that produces a fraud probability.
- Specialist agents for provider, claim, and beneficiary analysis.
- A coordinator that aggregates outputs into a report.

In the current codebase, the investigation layer is centered around:

- ProviderAnalysisAgent
- ClaimAnalysisAgent
- BeneficiaryAnalysisAgent
- InvestigationCoordinatorAgent

The current behavior is mostly statistical and score-driven:

- Each agent evaluates a set of metrics against reference distributions.
- Evidence is a list of metric-level outlier records.
- The coordinator averages specialist scores and merges evidence.

This is useful for prototyping, but it is not yet an investigation engine. It behaves more like a rules-based anomaly scorer than a fraud investigation team.

---

## 2. Weaknesses in the Current Design

### 2.1 The agents are not semantically aware

They currently produce outputs such as:

- metric/value/zscore evidence
- risk score
- simple outlier flags

These are operationally useful, but they do not express a professional investigation finding such as:

- “Provider reimbursement is materially above comparable cardiology providers.”
- “Billing aligns with a pattern consistent with upcoding.”
- “Patient concentration suggests possible identity misuse or referral abuse.”

### 2.2 The agents act independently

The current design does not have an explicit collaboration protocol. One agent does not automatically trigger a second specialist investigation based on a high-confidence finding.

### 2.3 Evidence fusion is too shallow

The coordinator currently computes a simple average of agent risk scores. This suppresses strong corroboration and cannot capture contradiction or business impact.

### 2.4 Hypothesis generation is missing

The system does not explicitly map evidence to fraud hypotheses such as:

- upcoding
- phantom billing
- duplicate billing
- unbundling
- excessive services
- identity misuse
- referral abuse

### 2.5 Temporal and cohort context are underrepresented

The current design compares providers mostly against a broad population and does not yet model:

- trend changes over time
- sudden reimbursement spikes
- seasonality
- peer-group suitability

### 2.6 The architecture is not extensible enough

Adding a new domain agent requires touching the coordinator and the task wiring. The design should be open for future agents such as:

- Policy Agent
- Network Analysis Agent
- Temporal Agent
- Financial Agent

---

## 3. Proposed Enterprise Architecture

The redesign should move from a scoring pipeline to a structured investigation platform.

### 3.1 Design philosophy

The investigation layer should behave like an insurance fraud investigation team:

- collect evidence
- reason about hypotheses
- cross-check findings across domains
- prioritize cases
- recommend investigative actions

This can be implemented with a layered architecture:

1. Evidence Layer
   - raw provider, claim, beneficiary, and temporal features
   - cohort baseline data
   - historical claim history

2. Analysis Layer
   - specialist agents that produce structured findings
   - each agent works on a domain-specific hypothesis set

3. Collaboration Layer
   - triggers and follow-up checks across agents
   - evidence propagation between domains

4. Fusion Layer
   - weighted evidence aggregation
   - contradiction handling
   - hypothesis scoring

5. Investigation Layer
   - case prioritization
   - next-actions recommendation
   - structured report generation

### 3.2 Core runtime objects

The system should operate around a shared investigation context rather than around raw JSON blobs.

- InvestigationContext
  - provider identifier
  - claim history
  - beneficiary history
  - prior findings
  - cohort metadata
  - temporal context
  - ML risk signal

- Finding
  - semantic statement of the issue
  - severity
  - confidence
  - evidence quality
  - business impact
  - fraud hypothesis
  - supporting metrics
  - triggered checks
  - recommended investigation

- InvestigationCase
  - all findings for a provider or claim cluster
  - priority score
  - active hypotheses
  - recommended next actions

---

## 4. Agent Responsibilities

### 4.1 Provider Agent

Responsibilities:

- detect unusual reimbursement intensity
- identify abnormal utilization patterns versus peer cohorts
- evaluate specialty-specific outliers
- flag concentration of high-cost services

Typical findings:

- “Provider reimbursement is significantly above comparable cardiology providers.”
- “Billing volume increased sharply relative to the prior quarter.”

Example triggers:

- if reimbursement is high, trigger Claim Agent for procedure-code review
- if patient concentration is unusual, trigger Beneficiary Agent

### 4.2 Claim Agent

Responsibilities:

- detect duplicate billing
- detect suspicious CPT or procedure distributions
- infer unbundling behavior
- evaluate claim velocity and temporal spikes

Typical findings:

- “Claims show a concentration of high-reimbursement procedure codes.”
- “Multiple claims share the same beneficiary and service dates.”

Example triggers:

- if duplicate billing is found, trigger Temporal Agent and Provider Agent
- if unusual code mix is found, trigger Financial Agent

### 4.3 Beneficiary Agent

Responsibilities:

- identify beneficiary concentration around a provider
- detect shared diagnosis patterns
- identify suspicious patient overlap or dependency
- assess identity misuse and referral abuse possibilities

Typical findings:

- “A small set of beneficiaries account for an unusually large share of the provider’s claims.”
- “Beneficiary overlap pattern is inconsistent with expected treatment patterns.”

Example triggers:

- if concentration is high, trigger Provider Agent for provider concentration review
- if overlap is extreme, trigger Network Analysis Agent

### 4.4 Temporal Agent

Responsibilities:

- analyze month-over-month reimbursement trends
- detect spike behavior and sudden acceleration
- compare seasonal cycles to historical norms

Typical findings:

- “Claims volume surged by 43% month over month.”
- “Reimbursement spiked sharply after a change in coding practice.”

### 4.5 Financial Agent

Responsibilities:

- evaluate claim amounts, reimbursement ratios, and loss patterns
- identify financially disproportionate behavior
- correlate high reimbursement with suspicious claim mixes

### 4.6 Policy Agent

Responsibilities:

- assess whether observed patterns violate benefit or policy rules
- identify unsupported billing behavior
- examine coverage mismatch and plan-specific anomalies

### 4.7 Network Analysis Agent

Responsibilities:

- analyze provider-beneficiary-provider relationships
- identify collusive or referral-based patterns
- detect unusual connectedness and clustering

---

## 5. Collaboration Workflow

The investigation system should not be a set of isolated agents. It should support a collaboration protocol.

### 5.1 Collaboration model

Each agent should emit findings that can trigger follow-up investigations.

A practical protocol is:

- TriggerEvent
  - source_agent
  - hypothesis
  - evidence_strength
  - entity_scope
  - recommended_next_agents

- InvestigationTask
  - target agent
  - context object
  - reason for escalation
  - required evidence

### 5.2 Example collaboration rules

1. Provider Agent detects high reimbursement
   - triggers Claim Agent to inspect CPT distribution, duplicate billing, and claim volume patterns

2. Beneficiary Agent detects high concentration
   - triggers Provider Agent to inspect provider concentration and beneficiary overlap

3. Claim Agent detects duplicate claim behavior
   - triggers Temporal Agent to assess whether the duplicate pattern is recent and accelerating

4. Temporal Agent detects sudden spike
   - triggers Financial Agent to assess reimbursement impact and cost exposure

5. Network Analysis Agent detects suspicious referral clustering
   - triggers Policy Agent to assess whether policy rules or authorization patterns were bypassed

### 5.3 Collaboration design principle

Agents should communicate through structured events, not through free-form text. This keeps the system deterministic, testable, and production-safe.

---

## 6. Coordinator Workflow

The coordinator should evolve into an Investigation Coordinator rather than a simple merger of risk scores.

### 6.1 The coordinator should perform five core functions

1. Correlate findings across agents
   - identify which findings support the same hypothesis
   - identify cross-agent corroboration

2. Detect contradictions
   - a provider looks anomalous but beneficiary evidence is weak
   - a high-risk claim pattern may appear inconsistent with provider-level evidence

3. Strengthen evidence
   - if multiple independent agents support the same hypothesis, increase confidence

4. Prioritize cases
   - rank the investigation case by urgency, financial exposure, and evidence strength

5. Recommend next actions
   - target audit, record request, beneficiary interview, payment hold, or case escalation

### 6.2 Decision workflow

The coordinator should follow this sequence:

1. Receive all specialist findings and the ML probability score.
2. Normalize findings into a common schema.
3. Group findings by fraud hypothesis.
4. Score each hypothesis using weighted evidence.
5. Resolve contradictions and assign confidence.
6. Determine case priority.
7. Generate a structured summary and recommended next steps.

### 6.3 Example decision logic

- If two or more independent agents support an upcoding hypothesis and evidence quality is high, escalate to a high-priority investigation.
- If evidence is weak or contradictory, downgrade the case to monitoring rather than immediate action.
- If the case involves high financial impact, increase urgency even if confidence is moderate.

---

## 7. Evidence Weighting Strategy

The current average-of-scores approach should be replaced with weighted evidence fusion.

### 7.1 Per-finding scoring

Each finding should carry the following attributes:

- confidence $c_i \in [0,1]$
- severity $s_i \in [0,1]$
- evidence quality $q_i \in [0,1]$
- business impact $b_i \in [0,1]$
- source independence $u_i \in [0,1]$

A basic evidence strength is:

$$
E_i = c_i \cdot s_i \cdot q_i \cdot b_i \cdot u_i
$$

### 7.2 Hypothesis support

For a hypothesis $h$:

$$
Support(h) = \frac{\sum_{i \in h} w_i \cdot E_i}{\sum_{i \in h} w_i}
$$

where $w_i$ is a domain-specific weight for the evidence source.

### 7.3 Contradiction penalty

If a hypothesis has strong negative evidence, the score should be reduced:

$$
FinalScore(h) = Support(h) - \lambda \cdot Contradiction(h)
$$

where $\lambda$ is a penalty coefficient.

### 7.4 Final case confidence

The coordinator can combine the ML model score with the fused hypothesis evidence:

$$
CaseConfidence = \alpha \cdot P_{ml} + \beta \cdot Support(h^*) - \gamma \cdot Contradiction(h^*)
$$

where:

- $P_{ml}$ is the model fraud probability
- $h^*$ is the strongest supported hypothesis
- $\alpha$, $\beta$, and $\gamma$ are calibrated weights

This yields a more business-aligned confidence than a simple average of agent scores.

---

## 8. Fraud Pattern Detection Mapping

The system should explicitly map evidence into fraud hypotheses.

### 8.1 Upcoding

Signals:

- high average reimbursement versus peer cohort
- high concentration of high-reimbursement procedure codes
- high ratio of expensive diagnosis-procedure combinations

Evidence pattern:

- provider reimbursement is high
- claim mix is skewed toward expensive codes
- distribution differs materially from specialty peers

### 8.2 Phantom Billing

Signals:

- claims that appear unrelated to legitimate service patterns
- unusual provider-beneficiary patterns
- no corresponding utilization history
- strong irregularity in temporal cadence

### 8.3 Duplicate Billing

Signals:

- repeated claim dates or service dates
- identical beneficiary and reimbursement amounts
- same provider and same procedure billed repeatedly

### 8.4 Unbundling

Signals:

- many lower-cost line items instead of one higher-value bundled code
- procedure-code distribution concentrated in component services

### 8.5 Excessive Services

Signals:

- claim volume above cohort peers
- claim velocity above expected level
- repeated treatment episodes for the same beneficiary

### 8.6 Identity Misuse

Signals:

- unusual beneficiary concentration
- high provider dependency by a small beneficiary set
- suspicious patient overlap patterns

### 8.7 Referral Abuse

Signals:

- abnormal network relationships between providers and beneficiaries
- concentrated referral patterns
- suspicious clustering between providers and a few beneficiaries

---

## 9. Temporal Analysis

The system should include temporal features rather than relying only on static snapshot statistics.

### 9.1 Features to compute

- month-over-month reimbursement change
- month-over-month claim volume change
- rolling 3-month and 6-month averages
- claim velocity
- reimbursement spike ratio
- seasonality index
- trend slope over time
- change-point indicators
- day-of-week or month-of-year concentration

### 9.2 Example temporal evidence

- “Reimbursement rose 42% month over month versus a 6% expected historical trend.”
- “Claims accelerated sharply in the last 30 days.”
- “The provider’s pattern diverged from seasonal norms for the specialty.”

These should be used as additional evidence in the claim and provider agents.

---

## 10. Cohort-Aware Analysis

The system should compare providers against the right peers rather than the entire population.

### 10.1 Cohort dimensions

Peer groups should be constructed using:

- specialty
- region
- hospital type
- practice setting
- patient demographics
- case mix
- age band
- chronic disease burden

### 10.2 Cohort construction strategy

A robust approach is to build a cohort engine that:

1. identifies candidate peers using categorical and continuous similarity
2. computes a weighted similarity score
3. uses the most similar peers as the comparison baseline
4. adjusts for case mix and patient complexity

This makes findings more credible and less prone to false positives.

### 10.3 Example

A cardiology provider in a metropolitan hospital should not be compared to a rural primary-care provider without accounting for specialty and patient mix.

---

## 11. Proposed Investigation Object Schema

The output should be a structured investigation object rather than a flat risk score.

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Finding:
    finding_id: str
    agent_name: str
    title: str
    severity: str  # low, medium, high, critical
    confidence: float
    evidence_quality: float
    business_impact: float
    fraud_hypothesis: str
    evidence: List[dict]
    supporting_metrics: List[dict]
    triggered_checks: List[str]
    recommended_investigation: str
    reasoning: str

@dataclass
class InvestigationCase:
    provider_id: str
    ml_probability: float
    findings: List[Finding] = field(default_factory=list)
    overall_confidence: float = 0.0
    priority: str = "low"
    recommended_next_actions: List[str] = field(default_factory=list)
    summary: str = ""
```

### 11.1 Required semantics

Each finding should answer the following questions:

- What is the issue?
- Why is it suspicious?
- How strong is the evidence?
- What hypothesis does it support?
- What should be investigated next?

---

## 12. Suggested Class Hierarchy

A production design should use interfaces and abstract classes.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class InvestigationContext:
    provider_id: str
    provider_row: dict
    cohort_context: dict
    temporal_context: dict
    ml_probability: float

class InvestigationAgent(ABC):
    @abstractmethod
    def analyze(self, context: InvestigationContext) -> List[dict]:
        raise NotImplementedError

class CollaborationAwareAgent(InvestigationAgent):
    @abstractmethod
    def trigger_follow_up(self, finding: dict) -> List[dict]:
        raise NotImplementedError

class ProviderInvestigationAgent(CollaborationAwareAgent):
    pass

class ClaimInvestigationAgent(CollaborationAwareAgent):
    pass

class BeneficiaryInvestigationAgent(CollaborationAwareAgent):
    pass

class InvestigationCoordinator(ABC):
    @abstractmethod
    def coordinate(self, context: InvestigationContext, findings: List[dict]) -> dict:
        raise NotImplementedError
```

### 12.1 Design benefits

- explicit contracts between components
- easier testing
- easier extension with new agents
- reduced coupling between specialist logic and coordinator logic

---

## 13. Suggested Folder Structure

```text
agents/
  investigation/
    __init__.py
    base.py
    protocols.py
    findings.py
    context.py
    agents/
      provider_agent.py
      claim_agent.py
      beneficiary_agent.py
      temporal_agent.py
      financial_agent.py
      policy_agent.py
      network_agent.py

services/
  investigation/
    coordinator.py
    evidence_fusion.py
    collaboration_bus.py
    case_manager.py

schemas/
  investigation_schema.py

config/
  investigation_config.yaml
  investigation_config.py

tests/
  test_investigation_fusion.py
  test_collaboration_workflow.py
```

---

## 14. Dependency Injection and Configuration Management

To keep the system maintainable:

- inject the data source, feature builder, and coordinator into the agents
- define configuration through a central config object
- support environment-driven settings for thresholds, weights, and cohort heuristics

Example:

```python
from dataclasses import dataclass

@dataclass
class InvestigationConfig:
    high_severity_threshold: float = 0.8
    evidence_weight: float = 0.35
    contradiction_penalty: float = 0.2
    cohort_similarity_threshold: float = 0.7
```

This makes the system testable and easier to tune in production.

---

## 15. Migration Strategy from the Current Code

### Phase 1 — Preserve compatibility

- keep the existing agents and service entry points
- add a new structured finding layer alongside current outputs
- keep the old risk score fields temporarily for backward compatibility

### Phase 2 — Introduce the new schema

- replace raw metric evidence with semantic findings
- add a shared InvestigationContext object
- introduce a coordinator that uses hypothesis-based fusion

### Phase 3 — Add collaboration triggers

- implement a lightweight event bus or queue between agents
- allow one agent’s finding to trigger follow-up checks in another agent

### Phase 4 — Move to production-grade orchestration

- add persistence for investigation cases
- add audit trails and explainability for each decision step
- integrate with human investigator workflows and case management systems

---

## 16. Recommended Implementation Direction

The most important architectural shift is this:

- stop treating agents as simple statistical calculators
- treat them as domain-specialist investigators that produce structured findings
- make the coordinator a decision engine that correlates findings, scores hypotheses, and recommends actions

That shift is what converts the current prototype into a production-oriented investigation platform.
