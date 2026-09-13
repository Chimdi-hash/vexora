# Example only: how another Intelligent Contract can gate an action on Vexora.
# This file is documentation and is not a second deployable contract.


def consumer_pattern(vexora_contract, vexora_id, expected_agreement_hash):
    """Pseudocode integration pattern for a downstream Intelligent Contract."""
    if not vexora_contract.is_vexora_active(vexora_id, expected_agreement_hash):
        raise Exception("required bilateral vexora is not active")

    terms = vexora_contract.get_vexora_terms(vexora_id)

    # The consumer decides what to do next. Vexora deliberately stops at
    # semantic compatibility plus bilateral consent.
    return terms
