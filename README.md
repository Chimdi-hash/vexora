# Vexora

**Vexora is a reusable GenLayer Intelligent Contract for consensus-backed policy compatibility and bilateral ratification between independent autonomous systems.**

It is intentionally **contract-only**. There is no frontend, no hosted backend, no mock application, and no off-chain database. The Intelligent Contract is the source of truth.

## Why Vexora exists

Two autonomous agents, APIs, DAOs, or services can each have valid policies and still be unsafe to connect.

A buyer agent might require:

- price <= 50 USD
- no customer PII disclosure
- full refund if execution never begins

A seller agent might require:

- price between 40 and 45 USD
- no PII required
- delivery within 600 seconds

Those policies are jointly satisfiable.

A different seller might require:

- price >= 60 USD
- customer email required before execution

Those policies are not.

A single agent should not get to interpret both sides. Vexora lets GenLayer validators independently judge the semantic satisfiability of the overlapping hard constraints, stores the immutable compatibility receipt, and then requires both actual policy owners to ratify before the vexora becomes active.

## The key design rule: no invented compromise

Vexora does **not** ask an LLM to write a new agreement.

The model may only classify a topic shared by both policies as:

- `COMPATIBLE`
- `CONFLICT`
- `AMBIGUOUS`

The original policy clauses remain the authoritative terms.

If one policy says `price <= 50` and another says `price >= 60`, the model cannot invent `55`.

If one side prohibits PII and the other side requires email, the model cannot invent hashing, tokenization, consent, or an exception.

If a safe conclusion cannot be reached, the correct result is `AMBIGUOUS`.

That bounded decision surface is the central safety property of the primitive.

## Architecture

Vexora has four layers.

### 1. Immutable policy versions

Each owner publishes a policy containing up to 12 hard constraints.

```json
[
  {
    "topic": "price.usd",
    "statement": "Total price must not exceed 50 USD."
  },
  {
    "topic": "data.pii",
    "statement": "Customer personally identifiable information must never be disclosed."
  }
]
```

Topics are deterministic machine keys. Statements are the semantic content.

Publishing a new version never mutates an old one. Every version receives a canonical Keccak definition hash.

### 2. Reusable compatibility assessments

Assessments pin two exact immutable policy versions.

The pair is canonicalized so:

```text
A:v1 + B:v3
```

and:

```text
B:v3 + A:v1
```

share one assessment cache entry.

For topics that appear in only one policy, Vexora deterministically records a unilateral hard constraint. Absence of a topic means "no additional restriction from this policy"; it is not treated as an implied permission.

The leader proposes one bounded relation per bilateral group, dependency, or declared same-policy consistency unit. The validator independently derives the same relation from the same immutable source; it does not merely check JSON shape. Unilateral groups are classified deterministically from source cardinality and never by an LLM.

The assessment becomes:

```text
COMPATIBLE
INCOMPATIBLE
AMBIGUOUS
```

An immutable assessment can be reused by many downstream consumers or multiple vexora proposals.

### 3. Bilateral ratification

Only a `COMPATIBLE` assessment can become a vexora proposal.

The proposer automatically ratifies their own proposal. The other policy owner must independently ratify it.

No LLM can activate a vexora.

```text
compatible assessment
        |
        v
PROPOSED --party A ratifies--> still PROPOSED
        |
        +--party B ratifies--> ACTIVE
```

Either party can reject before activation.

### 4. Supersession

A new vexora may reference an existing active vexora as its parent.

The old vexora remains active while the successor is merely proposed.

Only when both parties ratify the successor does deterministic contract logic move:

```text
old: ACTIVE -> SUPERSEDED
new: PROPOSED -> ACTIVE
```

This prevents one party from silently replacing shared terms.

## Why consensus is necessary

The hard part is not parsing JSON. It is the semantic question:

> Is there at least one behavior that satisfies both natural-language hard constraints?

Examples:

```text
A: "price must not exceed 50 USD"
B: "price must be between 40 and 45 USD"
=> COMPATIBLE
```

```text
A: "customer PII must never be disclosed"
B: "customer email is required before execution"
=> CONFLICT
```

```text
A: "delivery must be reasonably fast"
B: "delivery should be prompt in normal conditions"
=> AMBIGUOUS
```

This is exactly the kind of nondeterministic semantic task GenLayer is designed to execute under validator consensus.

Vexora uses a custom `gl.vm.run_nondet_unsafe` leader/validator pattern. Validators do not check that the leader returned valid JSON. They independently re-run the semantic classification from the same immutable source clauses and must agree on the exact bounded topic relation.

All storage writes happen only after consensus returns.

## Consensus pipeline

```text
immutable policy A:vN
immutable policy B:vM
          |
          v
immutable versioned domain vocabulary
          |
          +---- canonical semantic-group alignment
          |
          +---- declared dependency and self-consistency units
          |
          +---- topic in both
                    |
                    v
             leader LLM judgment
                    |
                    v
       COMPATIBLE / CONFLICT / AMBIGUOUS
                    |
                    v
       source-grounded validator checks
                    |
          agree ----+---- disagree
            |               |
            v               v
      consensus result   no settlement
            |
            v
 deterministic aggregate assessment
```

Only relation codes are consensus-critical. Free-form model reasoning is deliberately not stored.

## State model

### Policy

```text
owner
name
domain_id + domain_version + domain_definition_hash
active_version
status
created_at
```

### PolicyVersion

```text
policy_id
version
definition_hash
created_at
constraints[]
```

### CompatibilityAssessment

```text
policy_a_id + version
policy_b_id + version
policy_a_hash
policy_b_hash
pair_hash
status
global_relation
results[]
created_at
resolved_at
```

### VexoraRecord

```text
assessment_id
party_a
party_b
agreement_hash
status
ratified_a
ratified_b
proposed_at
activated_at
expires_at
parent_vexora_id
```

## Statuses

### Assessment

| Code | Meaning |
|---|---|
| `PENDING` | not yet semantically resolved |
| `COMPATIBLE` | all hard constraints are jointly satisfiable or unilateral |
| `INCOMPATIBLE` | at least one overlapping topic is a conflict |
| `AMBIGUOUS` | no conflict was established, but at least one topic cannot be safely resolved |

### Vexora

| Code | Meaning |
|---|---|
| `PROPOSED` | awaiting the second party |
| `ACTIVE` | both owners ratified |
| `REJECTED` | a party rejected before activation |
| `EXPIRED` | explicit expiry passed and state was refreshed |
| `SUPERSEDED` | both parties activated a successor vexora |

## Reusable interface

Other Intelligent Contracts can consume Vexora through `IVexora`.

The most important view is:

```python
is_vexora_active(vexora_id, expected_agreement_hash)
```

A downstream contract should pin the expected agreement hash rather than trusting a bare vexora ID.

That prevents a caller from substituting an unrelated vexora record.

The full terms can be inspected with:

```python
get_vexora_terms(vexora_id)
```

Those terms are always the original source clauses from the pinned policy versions. There is no generated agreement prose.

## Example consumer pattern

See [`examples/consumer.py`](examples/consumer.py).

A marketplace, agent router, procurement contract, data exchange, or tool delegation system can require an active Vexora before accepting a cross-system action.

Vexora itself does not move funds.

## Public write methods

```text
create_domain(name, definition_json)
publish_domain_version(domain_id, definition_json)
create_policy(name, domain_id, domain_version, constraints_json)
publish_version(policy_id, constraints_json)
pause_policy(policy_id, paused)

open_assessment(policy_a_id, policy_a_version, policy_b_id, policy_b_version)
resolve_assessment(assessment_id)

propose_vexora(assessment_id, expires_at, parent_vexora_id)
ratify_vexora(vexora_id)
reject_vexora(vexora_id)
refresh_expiry(vexora_id)
```

## Public views

```text
get_policy
get_domain
get_domain_version
get_policy_version
get_assessment
get_cached_assessment
get_vexora
get_vexora_terms
is_vexora_active
status_dictionary
```

## Security properties

Vexora is designed around explicit invariants.

1. **No generated compromise.** Consensus classifies; it never writes replacement terms.
2. **Immutable source pinning.** Assessments reference exact version hashes.
3. **Independent validators.** Validators rerun the semantic decision.
4. **Bounded outputs.** Only finite relation codes affect state.
5. **Prompt-injection containment.** Policy statements are explicitly treated as untrusted data.
6. **Exact topic alignment.** The model cannot invent or reorder topics.
7. **Independent ownership.** A single address cannot create both sides of a bilateral assessment.
8. **Owner-only publication.** Only the policy owner can publish revisions or pause a policy.
9. **Bilateral activation.** Consensus cannot activate an agreement; both owners must ratify.
10. **Safe supersession.** A successor does not disable its parent until both parties ratify.
11. **Order-independent cache.** Reversing policy order cannot create a second semantic truth for the same immutable pair.
12. **No value movement.** Vexora is a trust primitive, not an escrow.

More detail is in [`docs/SECURITY.md`](docs/SECURITY.md) and [`docs/CONSENSUS.md`](docs/CONSENSUS.md).

## Tests

The direct-mode suite covers lifecycle, access control, semantic consensus, and adversarial behavior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt
pytest tests/direct/ -v
```

Important adversarial tests include:

- validator independently disagrees with a compatible leader result
- malformed model result
- model topic reordering/invention
- prompt-injection text inside a policy statement
- non-party assessment creation
- same-owner bilateral manufacturing
- paused policy gating
- unauthorized ratification/rejection
- successor cannot supersede parent before the second ratification
- exact immutable source clauses are preserved in vexora terms

## Preflight

The repository includes a deterministic source preflight that does not need GenLayer Studio:

```bash
python scripts/preflight.py
```

Optional full linter:

```bash
pip install -r requirements.txt
genvm-lint check contracts/vexora.py
```

## Deployment

Vexora has no constructor arguments.

Deploy Vexora to StudioNet using the provided deployment script. After deployment, update `docs/DEPLOYMENT.md` with your fresh transaction receipts.