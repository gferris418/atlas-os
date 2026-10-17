# Migration controls

Each migration is a structured control validated by `schemas/migration.schema.json`. A `CLOSED` control requires a closure timestamp and evidence. Release-blocking controls listed in `atlas-os.yaml` must resolve to these files and remain open until their acceptance criteria are independently demonstrated.
