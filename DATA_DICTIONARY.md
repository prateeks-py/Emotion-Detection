# Data dictionary

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique row identifier. |
| `text` | string | Expression text; synthetic in the starter dataset. |
| `language` | string | Language code or language label (`en`, `hi`, `hinglish`, `es`, `fr`, `ar`). |
| `primary_emotion` | string | Primary emotion target. |
| `secondary_emotions` | JSON array string | Other relevant emotions. |
| `emotion_intensity_1_5` | integer | Weak synthetic intensity estimate, 1–5; not a calibrated score. |
| `expression_type` | string | General expression or safety-related expression. |
| `language_style` | string | Approximate register/style label. |
| `profanity_present` | boolean/0-1 | Whether an explicit profanity marker was detected by the template generator. |
| `sarcasm` | string | `unknown` unless manually annotated. |
| `negation_present` | boolean/0-1 | Heuristic marker; not a full syntactic analysis. |
| `sensitive_category` | string | `none`, `profanity`, `emotional_distress`, `abuse_or_threat`, `self_harm_signal`, `sexual_boundary`, `discrimination_or_hate`. These are weak synthetic tags, not clinical or legal judgments. |
| `context_required` | boolean/0-1 | Indicates that contextual review is recommended. |
| `source_type` | string | `synthetic`, `public_dataset`, or `human_annotated`. |
| `source_name` | string | Template name or exact public dataset identifier. |
| `source_license` | string | Provenance/license note; verify before redistribution. |
| `annotation_status` | string | Describes how labels were assigned. |
| `split` | string | `train`, `validation`, or `test`. |

## Recommended emotion taxonomy
Core emotions: `anger`, `sadness`, `joy`, `love`, `fear`, `surprise`, `disgust`, `shame`, `neutral`.
Sensitive and contextual labels are independent: profanity, emotional distress, abuse/threat, self-harm signal, sexual boundary, discrimination/hate.
A phrase may have multiple emotions. Do not infer an actual mental state or diagnosis from text alone.
