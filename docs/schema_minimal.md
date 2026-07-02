# Minimal Schema

This document describes the minimal records a ResearchKB Agent Memory system should expose. The exact database implementation can differ, but agents need a stable conceptual schema.

## Design Rules

- Every answerable claim should be traceable to evidence.
- Store raw source text separately from extracted claims.
- Distinguish paper evidence, LLM extraction, human notes, experiment logs, and failure cases.
- Missing evidence should be reported, not hidden.
- Private file paths should remain local and should not be committed to this repository.

## Tables

### `papers`

Bibliographic metadata.

| Field | Type | Description |
| --- | --- | --- |
| `paper_id` | string | Stable internal ID |
| `title` | string | Paper title |
| `authors` | string or JSON | Author list |
| `year` | integer | Publication year |
| `venue` | string | Venue or source |
| `doi` | string | Optional DOI |
| `arxiv_id` | string | Optional arXiv ID |
| `url` | string | Public source URL when available |
| `tags` | JSON | Topic tags |
| `created_at` | datetime | Ingestion time |

### `chunks`

Searchable source text from papers, notes, or documents.

| Field | Type | Description |
| --- | --- | --- |
| `chunk_id` | string | Stable chunk ID |
| `paper_id` | string | Optional linked paper |
| `source_type` | enum | `paper_text`, `abstract`, `appendix`, `table`, `human_note`, `web_page` |
| `section` | string | Section name when known |
| `locator` | string | Page, section, paragraph, or line locator |
| `text` | text | Source text |
| `embedding_ref` | string | Optional vector index reference |
| `created_at` | datetime | Ingestion time |

### `claims`

Structured statements extracted from sources.

| Field | Type | Description |
| --- | --- | --- |
| `claim_id` | string | Stable claim ID |
| `claim_type` | enum | `method`, `experiment`, `limitation`, `failure`, `safety`, `future_work`, `result` |
| `statement` | text | Concise claim |
| `paper_id` | string | Optional linked paper |
| `chunk_id` | string | Optional linked chunk |
| `confidence` | float | Extraction confidence from 0 to 1 |
| `created_by` | enum | `human`, `llm`, `script` |
| `created_at` | datetime | Creation time |

### `evidence_links`

Evidence provenance. This is the anti-hallucination layer.

| Field | Type | Description |
| --- | --- | --- |
| `evidence_id` | string | Stable evidence ID |
| `source_type` | enum | `paper`, `chunk`, `claim`, `run`, `problem_case`, `human_note`, `code_state` |
| `source_id` | string | ID of the source record |
| `paper_id` | string | Optional paper ID |
| `chunk_id` | string | Optional chunk ID |
| `run_id` | string | Optional experiment run ID |
| `problem_id` | string | Optional problem case ID |
| `locator` | string | Page, section, log line, file-relative locator, or table row |
| `quote_or_snippet` | text | Short supporting snippet |
| `confidence` | float | Confidence from 0 to 1 |
| `created_at` | datetime | Creation time |

### `experiment_runs`

Experiment records and outcomes.

| Field | Type | Description |
| --- | --- | --- |
| `run_id` | string | Stable run ID |
| `project` | string | Project name |
| `experiment` | string | Experiment name |
| `status` | enum | `running`, `completed_positive`, `completed_negative`, `failed` |
| `dataset` | string | Dataset or benchmark |
| `model` | string | Model or system under test |
| `seed` | integer, string, or null | Optional seed |
| `config_ref` | string or null | Relative config path, content hash, or git ref; never a machine-local absolute path |
| `metrics_json` | JSON | Parsed metrics |
| `artifacts_json` | JSON | Output artifacts |
| `failure_type` | string | Optional failure label |
| `decision` | enum | `continue`, `stop`, `redesign`, `rerun`, `unknown` |
| `next_action` | text | Proposed next step |
| `created_at` | datetime | Run time or ingestion time |

### `problem_cases`

Reusable failure memory.

| Field | Type | Description |
| --- | --- | --- |
| `problem_id` | string | Stable problem ID |
| `symptom` | text | User-visible failure symptom |
| `context` | text or JSON | Model, dataset, config, environment summary |
| `suspected_causes` | text or JSON | Candidate causes |
| `tried_fixes` | text or JSON | Fixes attempted |
| `final_solution` | text | Confirmed solution, if known |
| `linked_runs` | JSON | Related run IDs |
| `linked_papers` | JSON | Related paper IDs |
| `confidence` | float | Confidence from 0 to 1 |
| `created_at` | datetime | Creation time |

### `research_projects`

Project-level memory for the current research direction.

| Field | Type | Description |
| --- | --- | --- |
| `project_id` | string | Stable project ID |
| `name` | string | Human-readable project name |
| `goal` | text | Current project goal |
| `active_hypothesis` | text | Current working hypothesis |
| `constraints_json` | JSON | Privacy, compute, deadline, or scope constraints |
| `status` | enum | `active`, `paused`, `completed`, `archived` |
| `tags_json` | JSON | Topic tags |
| `created_at` | datetime | Creation time |
| `updated_at` | datetime | Last update time |

### `decision_logs`

Decisions made during the project, including why alternatives were rejected.

| Field | Type | Description |
| --- | --- | --- |
| `decision_id` | string | Stable decision ID |
| `project_id` | string | Linked project ID |
| `decision` | text | Decision summary |
| `rationale` | text | Why the decision was made |
| `evidence_ids_json` | JSON | Supporting source IDs |
| `rejected_options_json` | JSON | Alternatives considered and rejected |
| `next_action` | text | Concrete follow-up |
| `created_at` | datetime | Decision time |
| `created_by` | string | `human`, `agent`, `script`, or local convention |

### `open_questions`

Unresolved questions that should shape future experiments or reading.

| Field | Type | Description |
| --- | --- | --- |
| `question_id` | string | Stable question ID |
| `project_id` | string | Linked project ID |
| `question` | text | The unresolved question |
| `priority` | enum | `low`, `medium`, `high`, `critical` |
| `status` | enum | `open`, `answered`, `dropped` |
| `evidence_ids_json` | JSON | Related source IDs |
| `next_action` | text | Concrete follow-up |
| `created_at` | datetime | Creation time |

### `rejected_ideas`

Ideas that should not be retried blindly.

| Field | Type | Description |
| --- | --- | --- |
| `idea_id` | string | Stable idea ID |
| `project_id` | string | Linked project ID |
| `idea` | text | Rejected idea |
| `reason` | text | Why it was rejected |
| `evidence_ids_json` | JSON | Supporting source IDs |
| `reusable_parts_json` | JSON | Parts that may still be useful |
| `created_at` | datetime | Rejection time |

### `agent_decisions`

Optional record of agent recommendations and outcomes.

| Field | Type | Description |
| --- | --- | --- |
| `decision_id` | string | Stable decision ID |
| `request_type` | enum | `troubleshoot`, `next_experiment`, `novelty_check`, `literature_search`, `result_interpretation` |
| `question` | text | User request |
| `answer_summary` | text | Short answer |
| `evidence_ids` | JSON | Evidence used |
| `recommendation` | text | Recommended action |
| `missing_context` | JSON | Missing evidence or inputs |
| `outcome` | string | Optional later outcome |
| `created_at` | datetime | Decision time |

## Required Evidence Fields For Agent Output

When an agent uses ResearchKB, each cited evidence item should include:

```json
{
  "source_type": "run",
  "source_id": "run_smoke_001",
  "locator": "metrics.json:accuracy",
  "snippet": "\"accuracy\": 0.842",
  "confidence": 0.95
}
```

The exact storage format can vary, but these fields should be recoverable.
