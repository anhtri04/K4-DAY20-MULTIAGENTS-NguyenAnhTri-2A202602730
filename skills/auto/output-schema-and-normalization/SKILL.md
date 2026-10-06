---
name: output-schema-and-normalization
description: Use when producing structured output such as JSON, CSV, or logs that must follow explicit naming, sorting, or schema conventions.
---
- Read the output contract for every field: case, separators, canonical values, units, timestamp format, and null handling.
- Normalize identifiers exactly as specified, including case conversion, separator replacement, and whitespace trimming.
- Apply the specified sort order completely; when multiple keys are required, sort by them in the stated order.
- Include every required top-level metadata, version, or generator field, even if it seems redundant.
- Validate the final artifact against the spec: parse it, check keys, types, allowed values, sort order, and row counts.
- Do not rely on input order or default library sorting; make the required order explicit in code.
- If the spec provides an example, match its structure and normalization exactly.
- Re-open the final file after writing and inspect the metadata block, first record, and last record.
- Keep temporary generation scripts out of the final deliverable workspace unless the task requires them.