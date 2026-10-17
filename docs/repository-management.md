# Repository management

`main` is the canonical integration branch. Substantive changes use reviewed branches and coherent commits. The repository ruleset should require the validation workflow, prohibit force pushes to protected release history, and reserve release tags for validated manifests.

Core semantics, schemas, governance, persistence, and release gates receive stronger review than documentation-only changes. Pull requests identify change classification, compatibility impact, evidence, migrations, and any approval boundary.

Do not destroy unknown work, rewrite history, bypass required checks, weaken controls to make CI green, or close migrations without evidence.

