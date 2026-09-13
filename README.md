# Vexora Protocol

**Vexora** is a strict, consensus-backed Intelligent Contract deployed on GenLayer. It serves as a foundational primitive for bilateral policy matching and autonomous agent compatibility. 

Vexora strictly evaluates overlapping policy constraints between two independent systems and requires explicit, bilateral ratification to form a binding on-chain agreement. It operates entirely on-chain. There is absolutely no frontend, no hosted backend, no mock application, and no off-chain database.

## Core Philosophy: Strict Bounded Evaluation

Vexora operates on a fundamental principle of **no invented compromise**. 

When two autonomous systems (such as a buyer and a seller agent) attempt to interact, their policies might contain competing constraints. Vexora does not allow the underlying LLM consensus to invent, negotiate, or hallucinate a middle ground. 

Instead, the network is strictly constrained to classify overlapping policy topics into exactly three deterministic outcomes:
- **`COMPATIBLE`**: Both policies can be mutually satisfied.
- **`CONFLICT`**: The policies are fundamentally at odds.
- **`AMBIGUOUS`**: The overlap is too vague to safely resolve.

If an LLM attempts to generate alternative prose or negotiate a price, the transaction is forcefully rejected by the network validators. The original policy statements always remain the immutable source of truth.

## System Architecture

Vexora's lifecycle is composed of four rigid phases:

### 1. Immutable Policy Versions
System owners deploy their operational constraints as version-controlled, definition-hashed policies. Once deployed, these immutable policy versions guarantee that historical agreements can never be altered.

```json
[
  {
    "topic": "execution.timeout",
    "statement": "The task must complete within 300 seconds."
  },
  {
    "topic": "data.privacy",
    "statement": "No personal identifiable information may be requested."
  }
]
```
Once published, a policy version is cryptographically pinned. Updates require publishing a new version, preserving the integrity of historical agreements.

### 2. Semantic Consensus Assessment
When two systems interact, Vexora requests a semantic compatibility assessment. It uses a custom `gl.vm.run_nondet_unsafe` block where validators independently re-evaluate the same prompt context.
To conserve resources and guarantee order-independence, the results are cached bidirectionally (i.e., `A + B` shares the same evaluation state as `B + A`). Unilateral constraints (topics present in only one policy) bypass the LLM and are resolved deterministically.

### 3. Bilateral Ratification
An assessment that resolves to `COMPATIBLE` can be converted into a formal **Vexora Proposal**.
Crucially, AI consensus alone cannot activate an agreement. The proposal remains pending until **both independent policy owners** manually or programmatically ratify the exact terms through bilateral ratification. If either party rejects it, the proposal is permanently voided.

### 4. Lifecycle & Supersession
Vexoras can expire or be superseded. When a new version of a policy requires an updated agreement, the successor Vexora is proposed. The active Vexora remains fully operational until the successor receives its second and final ratification, at which point the state atomically transitions.

## Security & Consensus Guarantees

Vexora enforces strict security properties to prevent malicious actors and prompt injections:
- **Validator Independence:** Network validators do not simply trust the leader's JSON. They independently rerun the classification against the immutable source clauses.
- **Data Containment:** Natural language clauses are heavily sanitized and treated as untrusted payloads. Prompt injections within policy statements cannot manipulate the structured classification.
- **Access Control:** Bilateral assessments cannot be manufactured by a single owner attempting to spoof both sides of an agreement.
- **Value Isolation:** Vexora is a trust and authorization primitive. It explicitly does not hold, move, or route financial assets.

## Integration Guide

Vexora exposes a standardized `IVexora` interface for other Intelligent Contracts to consume.

Downstream protocols (e.g., decentralized marketplaces, agent orchestrators, data pipelines) should strictly query Vexora before authorizing interactions:

```python
# Verifies that an agreement is ACTIVE and matches the expected cryptographic hash
is_vexora_active(vexora_id, expected_agreement_hash)
```

By pinning the `expected_agreement_hash`, consumers are protected against malicious actors attempting to substitute a different, valid Vexora ID that corresponds to unrelated terms.

## Testing & Validation

Vexora includes a comprehensive test suite covering the full lifecycle, role-based access control, and adversarial vectors.

### Requirements
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt
```

### Run the Test Suite
The suite tests extreme state edges, validator disagreements, and prompt injection attempts.
```bash
pytest tests/direct/ -v
```

### Strict Code Linting
Vexora passes the strict GenVM semantic validator with zero errors.
```bash
pip install -r requirements.txt
genvm-lint check contracts/vexora.py
```

## Deployment

Vexora has been successfully deployed to the GenLayer Studio Network.

**Contract Address:** `0x04a58cc5A1F12Ff3604B89D6eF57Cf183271eDa7`
**Studio Explorer:** [View on GenLayer Explorer](https://explorer-studio.genlayer.com/address/0x04a58cc5A1F12Ff3604B89D6eF57Cf183271eDa7)

### Local Deployment
Vexora requires no constructor arguments upon initialization. Use the provided deployment script to push the contract to the GenLayer StudioNet.

```bash
python scripts/deploy_studionet.py
```
*Note: Ensure your GenLayer CLI is installed and your account is unlocked prior to deployment. Refer to `docs/DEPLOYMENT.md` to document your transaction receipts.*

## License

MIT