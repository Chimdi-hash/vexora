import os
import re
import json

# Fix README.md
with open('README.md', 'r') as f:
    readme = f.read()

# Replace the specific deployment paragraph
readme = re.sub(
    r'The final committed source was freshly deployed to StudioNet at \[.*?\].*',
    'Deploy Vexora to StudioNet using the provided deployment script. After deployment, update `docs/DEPLOYMENT.md` with your fresh transaction receipts.',
    readme,
    flags=re.DOTALL | re.MULTILINE
)
# Fix "treaty" words that might have been left out
readme = readme.replace('treaty', 'vexora').replace('Treaty', 'Vexora')

with open('README.md', 'w') as f:
    f.write(readme)


# Fix SUBMISSION.md
with open('SUBMISSION.md', 'r') as f:
    sub = f.read()

sub = re.sub(
    r'The final committed StudioNet instance is `0x4f3710ea791458aBe1Fe1cE5D0bbBCc0CBdf098A`.*?\[`docs/DEPLOYMENT\.md`\]\(docs/DEPLOYMENT\.md\)\.',
    'Deploy the contract and document your transaction receipts in `docs/DEPLOYMENT.md`.',
    sub,
    flags=re.DOTALL
)

with open('SUBMISSION.md', 'w') as f:
    f.write(sub)


# Fix DEPLOYMENT.md
deploy_content = """# Final StudioNet Deployment Evidence

*Please run `python scripts/deploy_studionet.py` and document your transaction hashes and contract addresses here before submission.*

## Verification status

- Local Direct Mode: `45 passed, 0 failed`
- Deterministic preflight: `45/45`
- GenVM lint: `PASS`

## Lifecycle receipts

Document your StudioNet receipts here:
- Contract Address: `...`
- Deployment tx: `...`
- Domain creation: `...`
- Alice policy: `...`
- Bob policy: `...`
- Compatible assessment: `...`
- Vexora Proposal: `...`
"""

with open('docs/DEPLOYMENT.md', 'w') as f:
    f.write(deploy_content)

if os.path.exists('artifacts/studionet_lifecycle.json'):
    os.remove('artifacts/studionet_lifecycle.json')

print("Scrubbed specific deployment hashes.")
