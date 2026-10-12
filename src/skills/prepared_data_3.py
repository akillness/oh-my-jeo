"""Static prepared guidance records for partition three of the audited catalog."""

PREPARED_MEMBERS = ({'canonical_id': 'adversarial-consensus',
  'family_id': 'adversarial-decision',
  'description': '[omh] Technical proposal facing adversarial scrutiny: independent perspectives attack a proposal, '
                 'then distill into a bundle a separate planner consumes. Use when the user says: '
                 'adversarial-consensus, adversarial planning, adversarial plan review, red team this plan, red-team '
                 'this plan, red team the proposal, multi-perspective review, multiple perspectives.',
  'triggers': ['adversarial-consensus',
               'adversarial planning',
               'adversarial plan review',
               'red team this plan',
               'red-team this plan',
               'red team the proposal',
               'multi-perspective review',
               'multiple perspectives'],
  'category': 'planning',
  'phase': 'adversarial-consensus',
  'role': 'planner',
  'source_folder': 'omh-adversarial-consensus',
  'source_path': 'skills/omh-adversarial-consensus/SKILL.md',
  'source_sha256': 'c531e927bf354b3c1f16dacd4124879162a592b2b4827c27fbc3fb3b2884fb8c',
  'required_inputs': ['the proposal, plan draft, or direction under review',
                      'the decision the review must inform',
                      'known constraints and non-negotiables',
                      'the perspective roster and why each angle is distinct'],
  'expected_outputs': ['per-perspective independent findings',
                       'cross-attack objections attributed to their author',
                       'defend, refine, or concede verdict per objection',
                       'distilled bundle in the fixed buckets Hard Constraints, Decisions, Risks, Open Questions',
                       'mandatory planner handoff naming the follow-on planning workflow'],
  'artifact_expectations': ['record the distilled bundle with `omh hermes plan --record`, which writes '
                            '`<repo>/.omh/plans/<slug>.md` inside a repository and the user-scope OMH store outside '
                            'one, so the planner pass consumes a file rather than scrollback'],
  'acceptance_criteria': ['The roster is named with 3-5 distinct angles, and no two seats argue the same one.',
                          'Round-one findings were produced blind, and any perspective that could not be kept blind is '
                          'named as a broken-independence caveat instead of being presented as independent.',
                          "Every cross-attack objection targets another perspective's finding, and no perspective "
                          'defended itself in that round.',
                          'Every objection carries exactly one verdict — defended, refined, or conceded — and conceded '
                          'findings are struck, not softened.',
                          'The bundle contains only Hard Constraints, Decisions, Risks, Open Questions, every line '
                          'traces to a surviving finding, and nothing new was added at distillation.',
                          'The closing message states that the bundle is input, names the follow-on planning workflow, '
                          'and claims no plan, acceptance, implementation, or verification evidence.'],
  'handoff_policy': 'Keep every round in Hermes as prepared prompt contracts. The distilled bundle is planning input: '
                    'hand it to `ralplan` or `plan` for the plan itself, and prepare a selected executor/runtime '
                    'handoff only after that separate planning pass produces an accepted plan.',
  'catalog_rules': ['Source routing exclusion: The user wants the plan itself, with options, acceptance criteria, and '
                    'verification commands; use `ralplan`, which this workflow feeds.',
                    'Source routing exclusion: The request is still too ambiguous to state the proposal being '
                    'attacked; use `deep-interview` first.',
                    'Source routing exclusion: The user wants completed code reviewed for defects rather than a '
                    'proposal attacked before it is built; use `code-review`.',
                    'Source routing exclusion: The user wants hostile runtime scenarios against a built change; use '
                    '`ultraqa`.',
                    'Source routing exclusion: One perspective would do: a small local change with no contested '
                    'decision does not earn three rounds.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'ralplan as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ralplan'],
  'references': [{'relative_path': 'omh-adversarial-consensus/references/consensus-protocol.md',
                  'content': '# Adversarial Consensus Protocol\n'
                             '\n'
                             'Load this reference when running the rounds. The always-loaded skill body states the '
                             'rules; this is the per-round procedure, the wording that keeps a perspective '
                             'independent, and the failure modes that make a run look adversarial while producing '
                             'agreement.\n'
                             '\n'
                             'Everything here is a prepared prompt contract. OMH runs no perspective and observes no '
                             'round. A stated round transition is a declaration, not evidence that the round '
                             'happened.\n'
                             '\n'
                             '## 1. The Roster\n'
                             '\n'
                             'Seat 3-5 perspectives. The suggested roster is `skeptic`, `validator`, `researcher`, '
                             '`architect`, `creative`, and each seat is defined by the angle it attacks from, not by a '
                             'job title:\n'
                             '\n'
                             '| Seat | Attacks from |\n'
                             '| --- | --- |\n'
                             '| `skeptic` | The claim that is being assumed rather than shown. Asks what breaks if the '
                             'load-bearing assumption is false. |\n'
                             '| `validator` | Verifiability. Asks how anyone would know this worked, and what the '
                             'failing case looks like. |\n'
                             '| `researcher` | Prior art and current behavior. Asks what the sources, upstream docs, '
                             'or the existing code already say. |\n'
                             '| `architect` | Structure and blast radius. Asks what else this couples to and what it '
                             'makes impossible later. |\n'
                             '| `creative` | The unexamined framing. Asks what a different shape of the solution would '
                             'cost, including doing nothing. |\n'
                             '\n'
                             'Substitute a domain seat (security, cost, operations, accessibility) when the problem '
                             'needs one. Two seats arguing the same angle is a duplicate, not a perspective: the '
                             "roster's value is coverage, and a duplicated angle buys none while making the run look "
                             'broader than it is.\n'
                             '\n'
                             '## 2. The Rounds, In Order\n'
                             '\n'
                             '1. independent findings\n'
                             '2. cross-attack\n'
                             '3. defend, refine, or concede\n'
                             '\n'
                             "The order is the contract. Independence exists only before any seat has read another's "
                             'findings, and an attack round placed after a defense round is agreement with extra '
                             'steps.\n'
                             '\n'
                             '### Round 1 - independent findings\n'
                             '\n'
                             "Each perspective produces its findings without seeing any other perspective's output. "
                             'Prompt each seat separately with the same problem statement, and give each one the same '
                             'context: the proposal, the decision it must inform, and the known constraints. Nothing '
                             'else.\n'
                             '\n'
                             'Every finding names its evidence or labels itself an assumption. "This will not scale" '
                             'is not a finding; "this holds every session in one process, and the deploy target runs '
                             'four replicas behind a round-robin balancer" is.\n'
                             '\n'
                             'Record all findings before opening round two. If the host cannot keep a seat blind -- '
                             'one context window, one transcript, one agent playing every part in sequence -- say so '
                             "and mark the round's independence as caveated. A caveated round is still useful. A run "
                             'that silently claims independence it did not have is not.\n'
                             '\n'
                             '### Round 2 - cross-attack\n'
                             '\n'
                             "Every perspective attacks other perspectives' findings, and never defends or restates "
                             'its own. Self-defense in this round is the single most common way the exercise '
                             'collapses: the moment a seat is allowed to answer its critics, the round turns into a '
                             'debate the loudest seat wins, and the objections stop being independent.\n'
                             '\n'
                             'Each attack names the finding it targets and the specific reason it fails: unsupported '
                             'evidence, a case it does not cover, a cost it does not price, or a conflict with another '
                             'finding. A perspective with no objection to any other seat says so explicitly. An empty '
                             'attack round is a roster defect -- state which angle is missing and fix the roster -- '
                             'not consensus.\n'
                             '\n'
                             '### Round 3 - defend, refine, or concede\n'
                             '\n'
                             'Now, and only now, each perspective answers the objections against it. Exactly one '
                             'verdict per objection:\n'
                             '\n'
                             '- **Defend** - the objection is answered with evidence the original finding already had '
                             'or can now cite.\n'
                             '- **Refine** - the objection lands partially; the finding is narrowed to what survives.\n'
                             '- **Concede** - the objection lands; the finding is struck from the record.\n'
                             '\n'
                             'A conceded finding is struck, not softened into a hedge. "Possibly a concern" is how a '
                             'conceded finding survives to become a Hard Constraint it never earned.\n'
                             '\n'
                             '## 3. Distillation - The Lead Subtracts Only\n'
                             '\n'
                             'The lead distills. Nothing new enters at distillation: every line in the bundle traces '
                             'back to a finding that survived round three, and it goes into exactly one of these '
                             'buckets:\n'
                             '\n'
                             '- **Hard Constraints**\n'
                             '- **Decisions**\n'
                             '- **Risks**\n'
                             '- **Open Questions**\n'
                             '\n'
                             '- **Hard Constraints** are the non-negotiables the plan must satisfy. A constraint here '
                             'is one no surviving objection disputes.\n'
                             '- **Decisions** are what the rounds actually settled, each with the reason it settled '
                             'that way.\n'
                             '- **Risks** are surviving objections that were refined rather than conceded: real, '
                             'priced, and not blocking.\n'
                             '- **Open Questions** are the disputes the rounds could not settle and the evidence that '
                             'would settle them.\n'
                             '\n'
                             'The bucket set is closed. If distillation seems to need a fifth bucket, the extra '
                             'content is a plan trying to escape -- move it into the handoff, not into a new bucket. '
                             'An unsupported objection is an **Open Questions** entry, never a **Hard Constraints** '
                             'one.\n'
                             '\n'
                             '## 4. The Mandatory Handoff\n'
                             '\n'
                             'The run ends with the bundle handed to a separate planning pass, and it ends there.\n'
                             '\n'
                             'State plainly that the bundle (**Hard Constraints**, **Decisions**, **Risks**, **Open '
                             'Questions**) is INPUT to planning, name the follow-on workflow -- `ralplan` when the '
                             'plan itself needs review gates, `plan` when the shape is already agreed -- and stop.\n'
                             '\n'
                             '**The anti-pattern:** treating the bundle as the plan. The four buckets read like a '
                             "plan's front matter, which is exactly why the substitution is tempting and exactly why "
                             'it is wrong. The bundle contains no sequence, no owner, no acceptance criteria, and no '
                             "verification commands, because producing those is the planner's job and this workflow "
                             'deliberately never did it. Emitting steps here skips the reviewed-plan gate and ships a '
                             'task list that nobody planned.\n'
                             '\n'
                             '## 5. Failure Modes\n'
                             '\n'
                             '| Looks like | Actually is | Fix |\n'
                             '| --- | --- | --- |\n'
                             '| Every seat agrees in round one | The seats were not independent, or the roster '
                             'duplicates an angle | Re-run the seats separately; replace a duplicate seat |\n'
                             '| Round two is polite | Self-defense leaked into the attack round | Restate the round '
                             'rule and re-run round two |\n'
                             '| Buckets full of "consider", "possibly", "may want to" | Conceded findings were '
                             'softened instead of struck | Strike them; a hedge is not a constraint |\n'
                             '| The bundle has steps and an order | The distillation became a plan | Move it to the '
                             'planner handoff |\n'
                             '| One long transcript, all seats | Independence was structural, not real | Keep it, and '
                             'mark the caveat rather than claiming independence |\n'
                             '\n'
                             '## 6. Attribution\n'
                             '\n'
                             'The round structure, the no-self-defense rule, and the distill-only discipline are '
                             'adapted from published multi-agent planning practice; no upstream text is reproduced. '
                             'The bucket set, the closed-set rule, and the `prepared_not_observed` claim boundary are '
                             "OMH's own contract vocabulary.\n",
                  'source_path': 'skills/omh-adversarial-consensus/references/consensus-protocol.md',
                  'source_sha256': 'e2337062d98214abc440d3909d7c076db284c817dc45c9b67a292003a6b51a89'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member adversarial-consensus is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep every round '
                       'in Hermes as prepared prompt contracts. The distilled bundle is planning input: hand it to '
                       '`ralplan` or `plan` for the plan itself, and prepare a selected executor/runtime handoff only '
                       'after that separate planning pass produces an accepted plan. No executor/provider/runtime '
                       'execution, observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'agent-instructions',
  'family_id': 'instruction-maintenance',
  'description': '[omh] Agent instruction file for a repo -- AGENTS.md, CLAUDE.md, a Cursor rule: write or update what '
                 'an agent cannot derive from the code, inside a marked region, with every command verified or marked '
                 'unverified and no counts that drift. Use when the user says: agent-instructions, agents.md, '
                 'claude.md, gemini.md, copilot-instructions.md, .cursorrules, cursor rules, cursor rule.',
  'triggers': ['agent-instructions',
               'agents.md',
               'claude.md',
               'gemini.md',
               'copilot-instructions.md',
               '.cursorrules',
               'cursor rules',
               'cursor rule'],
  'category': 'planning',
  'phase': 'agent-instructions',
  'role': 'planner',
  'source_folder': 'omh-agent-instructions',
  'source_path': 'skills/omh-agent-instructions/SKILL.md',
  'source_sha256': 'acdb8eb6a411cc1e4b0345151fda6d70f443fb0ccf170d037c18b960aeb91fe9',
  'required_inputs': ['which instruction files exist, where they sit, and which agents read them',
                      'the build, test, lint, and regenerate commands the repository uses',
                      'which files are generated, from what source, and which gate checks them',
                      'the pitfalls that have cost time, each with what it cost',
                      'observed output for every command written into the file'],
  'expected_outputs': ['instruction_file_inventory/v1',
                       'command_verification_record/v1',
                       'instruction_region_update/v1',
                       'drift_refusal_note/v1 when a requested line would record a count or a line number'],
  'artifact_expectations': ['instruction_file_inventory/v1 lists every instruction file, its path, the agents that '
                            'read it, and which one is closest to each directory, since the closest file wins',
                            'command_verification_record/v1 marks every command verified, with the observed exit '
                            'status and when, or unverified, and nothing is written as verified without an observed '
                            'run',
                            'instruction_region_update/v1 replaces only the text between `<!-- '
                            'omh:agent-instructions:begin -->` and `<!-- omh:agent-instructions:end -->`, and inserts '
                            'the markers once when absent, so every hand-written section outside them is left '
                            'byte-for-byte',
                            'drift_refusal_note/v1 names each requested count, line number, or other value the code '
                            'already states, and writes the command or the file that derives it instead'],
  'acceptance_criteria': ['Every instruction file and its reader are listed.',
                          'Every command is marked verified with an observed run, or unverified.',
                          'Only the marked region changed, and hand-written text is byte-for-byte.',
                          'No count, line number, or value the code already states was written.',
                          'Every generated file names its source, its regenerate command, and its gate.'],
  'handoff_policy': 'Keep the section plan, the command verification record, and the region update in Hermes. Every '
                    "command's outcome is recorded only from executor, operator, or wrapper observed output; the file "
                    'is written by the executor, and only inside its marked region.',
  'catalog_rules': ['Source first step: List every instruction file and which agent reads it before proposing a '
                    'section.',
                    'Source first step: Run or ask for the observed run of each command before marking it verified.',
                    'Source routing exclusion: The ask is distilling repeated lessons into reviewed rule candidates; '
                    'use `rules-distill`.',
                    'Source routing exclusion: The ask is a reading path through the codebase for a new engineer; use '
                    '`codebase-onboarding`.',
                    'Source routing exclusion: The ask is project terminology alignment -- reviewing the terms this '
                    'project uses and correcting inconsistent vocabulary; use `context`.',
                    'Source routing exclusion: The ask is user-facing product documentation; use `product-docs`.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'plan, code-review as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['plan', 'code-review'],
  'references': [{'relative_path': 'omh-agent-instructions/references/instruction-file-method.md',
                  'content': '# Instruction File Method\n'
                             '\n'
                             'Load this while writing or updating an agent instruction file. OMH prepares the text; '
                             'the executor runs the commands and writes the file, and only inside the marked region.\n'
                             '\n'
                             '## 1. Which file, where\n'
                             '\n'
                             '| File | Read by | Note |\n'
                             '| --- | --- | --- |\n'
                             '| `AGENTS.md` | Codex, and most agents that follow the open format | nested files apply '
                             'to their directory; the closest file wins |\n'
                             '| `CLAUDE.md` | Claude Code | may point at `AGENTS.md` instead of repeating it |\n'
                             '| `GEMINI.md` | Gemini CLI | |\n'
                             '| `.cursor/rules/*.mdc`, `.cursorrules` | Cursor | rules carry their own globs |\n'
                             '| `.github/copilot-instructions.md` | GitHub Copilot | |\n'
                             '\n'
                             'When several exist, keep one source and point the others at it, so two files cannot '
                             'disagree.\n'
                             '\n'
                             '## 2. The marked region\n'
                             '\n'
                             '```text\n'
                             '<!-- omh:agent-instructions:begin -->\n'
                             '... prepared content ...\n'
                             '<!-- omh:agent-instructions:end -->\n'
                             '```\n'
                             '\n'
                             '- Replace only the text between the markers. Everything before and after is hand-written '
                             'and stays byte-for-byte.\n'
                             '- When the markers are absent, insert them once, around the new section, and change '
                             'nothing else.\n'
                             '- Never nest a second pair, and never move hand-written text into the region.\n'
                             '\n'
                             '## 3. Sections, in order\n'
                             '\n'
                             '1. **Build and test**: the exact commands, each marked `verified (exit 0, <date>)` or '
                             '`unverified`, with the environment they need (`PYTHONPATH`, a service, a toolchain '
                             'version file).\n'
                             '2. **Generated files**: for each one, its source, the command that regenerates it, and '
                             'the gate that checks it. Say "never hand-edit" once, here.\n'
                             '3. **Gates**: which checks are byte-exact, and which fail on a count the author must '
                             're-derive.\n'
                             '4. **Pitfalls**: each entry names the symptom, the cause, and what it cost, so a reader '
                             'can tell a scar from a preference.\n'
                             '5. **Conventions** the code cannot show: branch names, commit trailers, the language of '
                             'the text.\n'
                             '\n'
                             '## 4. What never goes in\n'
                             '\n'
                             '| Tempting line | Why it drifts | Write instead |\n'
                             '| --- | --- | --- |\n'
                             '| "the suite has 4,100 tests" | the next merge changes it | the command that runs the '
                             'suite |\n'
                             '| "the router is at line 212 of `chat.py`" | any edit above it moves it | the symbol '
                             'name |\n'
                             '| "we have 134 skills" | the catalog grows | the command or file that counts them |\n'
                             '| a restatement of what a function does | the code already says it, and the two diverge '
                             '| nothing |\n'
                             '| a secret, a token, or a private hostname | the file is read by every agent and often '
                             'published | the name of the variable that holds it |\n'
                             '\n'
                             'The injected copy of an instruction file is a snapshot of the session start. A long '
                             'session re-reads the file from the default branch before relying on it.\n',
                  'source_path': 'skills/omh-agent-instructions/references/instruction-file-method.md',
                  'source_sha256': 'cc8f82b67198fa905f1336ea0fb8b50a2451b290ca4678efc41cc2c195828446'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member agent-instructions is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep the section '
                       "plan, the command verification record, and the region update in Hermes. Every command's "
                       'outcome is recorded only from executor, operator, or wrapper observed output; the file is '
                       'written by the executor, and only inside its marked region. No executor/provider/runtime '
                       'execution, observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'connector-operator',
  'family_id': 'primitive-operators',
  'description': '[omh] Email, Slack, or Jira action to perform: external app actions - email, Slack, Discord, Notion, '
                 'Linear, Jira, CRM, and similar providers, scoped with auth, payload, confirmation, and '
                 'result-evidence gates. Use when the user says: connector-operator, connector operator, external app '
                 'action, external connector action, saas action, api action, send email, email customer.',
  'triggers': ['connector-operator',
               'connector operator',
               'external app action',
               'external connector action',
               'saas action',
               'api action',
               'send email',
               'email customer'],
  'category': 'connector',
  'phase': 'connector-task',
  'role': 'guide',
  'source_folder': 'omh-apps',
  'source_path': 'skills/omh-apps/SKILL.md',
  'source_sha256': 'fd17d1e8702a7630cd3e2b4e121b4de4911a5dd16ae0f1254cb83c1332bbcd26',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['connector_task_card/v1',
                       'connector_scope/v1',
                       'connector_auth_boundary/v1',
                       'connector_confirmation_gate/v1 when mutating or sending',
                       'connector_result_manifest/v1 when observed',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['connector_task_card/v1 metadata-only wrapper card when prepared',
                            'connector_scope/v1 with provider, target object, allowed action, payload summary, and '
                            'stop condition',
                            'connector_auth_boundary/v1 separating missing connector, missing credentials, '
                            'user-supplied authority, and credential-use prohibition',
                            'connector_confirmation_gate/v1 for sending, ticket mutation, external write, webhook '
                            'delivery, CRM/database update, or irreversible provider action',
                            'connector_result_manifest/v1 only when provider response, message id, ticket id, API '
                            'transcript, or delivery receipt is observed'],
  'acceptance_criteria': ['Provider, target object, allowed action, payload summary, authority, confirmation policy, '
                          'and stop condition are explicit.',
                          'Credentials, missing connector setup, external writes, sends, ticket mutations, calendar '
                          'invites, CRM updates, and webhook delivery are gated or marked missing.',
                          'Message ids, ticket ids, provider responses, delivery receipts, and API effects are '
                          'reported only from observed connector evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'toolbelt-readiness, deliverable-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness', 'deliverable-package'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member connector-operator is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as '
                       'Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                       'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                       'recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'browser-operator',
  'family_id': 'primitive-operators',
  'description': '[omh] Browser login, click, or form task: policy overlay for browser tasks - add auth, confirmation, '
                 'and observed-trace gates after preferring the native browser for ordinary URL, click, login, and '
                 'form actions. Use when the user says: browser-operator, browser operator, browser task, browser '
                 'operation, browser automation, browser session, webpage operation, web page operation.',
  'triggers': ['browser-operator',
               'browser operator',
               'browser task',
               'browser operation',
               'browser automation',
               'browser session',
               'webpage operation',
               'web page operation'],
  'category': 'browser',
  'phase': 'browser-task',
  'role': 'guide',
  'source_folder': 'omh-browser',
  'source_path': 'skills/omh-browser/SKILL.md',
  'source_sha256': '8529cab9578cb9309b6a3d2146ac727ff42bcf8039ddd400a1896e7d6f31d8e2',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['browser_task_card/v1',
                       'browser_interaction_scope/v1',
                       'browser_auth_boundary/v1',
                       'browser_observation_manifest/v1 when observed',
                       'browser_confirmation_gate/v1 when destructive',
                       'browser_adapter_capabilities/v1 when acquired',
                       'browser_session_lease/v1 when acquired',
                       'browser_page_state/v1 when observed',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['browser_task_card/v1 metadata only',
                            'browser_interaction_scope/v1: URL, allowed/prohibited actions, stop condition',
                            'browser_auth_boundary/v1: supplied/missing/prohibited credentials',
                            'browser_observation_manifest/v1: observed screenshots/DOM notes/console/network/click '
                            'traces only',
                            'Leases: docs/BROWSER-ADAPTER.md; owner/adapter/version/task scope, cached capabilities, '
                            'digest-only state, exact revision handles.',
                            'browser_skill_promotion/v1: `omh web-qa promotion diff`, `approve` its exact digest, then '
                            '`promote` one receipt; SKILL.md alone commits visibility'],
  'acceptance_criteria': ['Specify URL, allowed/prohibited actions, auth boundary, stop condition.',
                          'Gate credentials/login/payment/purchase/destruction/scraping/export; observed traces only.',
                          'Host request admission (not enablement/adapter presence) gates '
                          'schemas/context/callbacks/writes. Refuse foreign/stale/expired/released/ambiguous targets; '
                          'no index fallback.',
                          'omh_browser blocks native browser_*; inert by default. Opted-in effects need exact '
                          'approval: docs/BROWSER-EFFECTS.md.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'toolbelt-readiness, deliverable-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness', 'deliverable-package'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member browser-operator is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as '
                       'Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                       'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                       'recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'codebase-onboarding',
  'family_id': 'code-intelligence',
  'description': '[omh] Unfamiliar repository needing a guided tour: create a repo map, reading path, glossary, risk '
                 'map, and first-task runway for unfamiliar codebases. Use when the user says: codebase-onboarding, '
                 'codebase onboarding, repo onboarding, repository onboarding, codebase tour, code tour, new repo '
                 'orientation, understand this repo.',
  'triggers': ['codebase-onboarding',
               'codebase onboarding',
               'repo onboarding',
               'repository onboarding',
               'codebase tour',
               'code tour',
               'new repo orientation',
               'understand this repo'],
  'category': 'planning',
  'phase': 'codebase-onboarding',
  'role': 'planner',
  'source_folder': 'omh-codebase-onboarding',
  'source_path': 'skills/omh-codebase-onboarding/SKILL.md',
  'source_sha256': 'c604623f641ae38026951712bbe2e6ed62ba26fc5413ed066dfeb66c181598e3',
  'required_inputs': ['repo root or supplied source context',
                      'target audience: operator, new contributor, maintainer, or executor',
                      'desired depth: quick map, architecture tour, first issue, or handoff pack',
                      'known constraints such as no network, no secrets, or read-only mode'],
  'expected_outputs': ['codebase_onboarding_plan/v1',
                       'repo_map/v1',
                       'reading_path/v1',
                       'domain_glossary/v1',
                       'risk_and_unknowns_map/v1',
                       'first_task_runway/v1',
                       'not-evidence boundary'],
  'artifact_expectations': ['repo_map/v1 with observed directories, entrypoints, generated surfaces, tests, docs, '
                            'scripts, and runtime artifacts',
                            'reading_path/v1 ordered from product direction to architecture, core modules, tests, and '
                            'operational docs',
                            'domain_glossary/v1 with repo-specific terms, owners, artifacts, and evidence references',
                            'first_task_runway/v1 with low-risk starter tasks, verification commands, and handoff '
                            'readiness'],
  'acceptance_criteria': ['The plan names goals, non-goals, assumptions, acceptance criteria, and verification shape.',
                          'Draft recommendations, accepted decisions, and executor handoffs are separate states.',
                          'Rejected options or unresolved tradeoffs are recorded before handoff.'],
  'handoff_policy': 'Keep codebase orientation in Hermes as prepared local context. File reads, generated maps, and '
                    'first-task recommendations need observed repo evidence; code edits and executor handoffs happen '
                    'only after onboarding identifies a concrete task.',
  'catalog_rules': ['Source routing exclusion: The user already named a concrete implementation task and acceptance '
                    'criteria; use `ultrawork` or `idea-to-deploy`.',
                    'Source routing exclusion: The user needs a whole-workspace capability inventory; use '
                    '`workspace-audit`.',
                    'Source routing exclusion: The user wants a code diff review; use `code-review`.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'plan as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['plan'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member codebase-onboarding is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep codebase '
                       'orientation in Hermes as prepared local context. File reads, generated maps, and first-task '
                       'recommendations need observed repo evidence; code edits and executor handoffs happen only '
                       'after onboarding identifies a concrete task. No executor/provider/runtime execution, observed '
                       'result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'codebase-uml',
  'family_id': 'code-intelligence',
  'description': '[omh] Architecture picture of a codebase: turn a repository into one readable, interface-level '
                 'PlantUML architecture picture - packages or modules, the public symbols other units actually import, '
                 'bounded import edges - and get it rendered to a single PNG a chat surface can show. Use when the '
                 'user says: codebase-uml, codebase uml, uml, plantuml, uml diagram, class diagram, package diagram, '
                 'module diagram.',
  'triggers': ['codebase-uml',
               'codebase uml',
               'uml',
               'plantuml',
               'uml diagram',
               'class diagram',
               'package diagram',
               'module diagram'],
  'category': 'planning',
  'phase': 'codebase-uml',
  'role': 'planner',
  'source_folder': 'omh-codebase-uml',
  'source_path': 'skills/omh-codebase-uml/SKILL.md',
  'source_sha256': '2342c510401082490fb87dca8c046d63d8b19c8ae2dcbef0c04314d8df544487',
  'required_inputs': ['repo root or current workspace',
                      'view: whole repo at package level, one area by `--focus <path>`, or module level for a '
                      'subsystem',
                      'delivery target (chat attachment, PR, doc) which fixes the format: PNG for chat, SVG only when '
                      'asked',
                      "renderer readiness from the command's render plan (`plantuml` on PATH, or `PLANTUML_JAR` plus "
                      '`java`)'],
  'expected_outputs': ['codebase_uml/v1 model (units, interfaces, edges, omissions) via `omh codegraph uml --json`',
                       'PlantUML source written by `omh codegraph uml --output <file>.puml`',
                       'uml_render_plan/v1 naming the exact render command or the blocker',
                       'one rendered PNG (or SVG on request) attached to the reply, with the omissions legend visible',
                       'not-evidence boundary'],
  'artifact_expectations': ['codebase_uml/v1 with `view` (level, depth, focus, caps), `nodes` carrying fan-in-ranked '
                            'public interfaces, weighted `edges`, `layout` hardening, and `omissions` counts',
                            'uml_render_plan/v1 with `status`, `renderer`, `layout_engine`, `command`, `blockers`, and '
                            '`notes`',
                            'the rendered image path only after the render command is observed to exit 0 and the file '
                            'exists'],
  'acceptance_criteria': ['The view (package, focus, or module) matches the question asked, and only one view was '
                          'rendered unless more were requested.',
                          'The render command and its observed result are recorded before the image is claimed.',
                          "The legend's omissions were read back to the user in the reply.",
                          'Follow-up exploration used narrower generated views, not recollection of the first '
                          'picture.'],
  'handoff_policy': 'Keep diagram scoping, the `omh codegraph uml` source generation, and the render command in '
                    "Hermes; the render runs through Hermes' own terminal tool and the image is attached by the chat "
                    'surface. A generated `.puml` is prepared context; the picture exists only when the render '
                    "command's exit status and output file are observed, and neither is architecture proof, review, "
                    'CI, or merge evidence.',
  'catalog_rules': ['Source routing exclusion: The user wants the local code index refreshed or a task-scoped handoff '
                    'pack, not a picture; use `codegraph-refresh`.',
                    'Source routing exclusion: The user wants a narrative first-read tour, reading path, or glossary; '
                    'use `codebase-onboarding`.',
                    'Source routing exclusion: The user wants a summary card, thumbnail, or explainer image of a PR, '
                    'meeting, or release rather than a structural diagram; use `img-summary`.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'plan as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['plan'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member codebase-uml is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep diagram '
                       'scoping, the `omh codegraph uml` source generation, and the render command in Hermes; the '
                       "render runs through Hermes' own terminal tool and the image is attached by the chat surface. A "
                       "generated `.puml` is prepared context; the picture exists only when the render command's exit "
                       'status and output file are observed, and neither is architecture proof, review, CI, or merge '
                       'evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'content-operator',
  'family_id': 'primitive-operators',
  'description': '[omh] Product or company copy to publish or rewrite: scope publish-ready writing, rewriting, '
                 'summarization, translation, release-note, newsletter, customer-copy, social-copy, README-copy, and '
                 'email-draft work with audience, tone, style, source, review, and hallucination gates. Use when the '
                 'user says: content-operator, content operator, content workflow, writing workflow, publish-ready '
                 'writing, publish ready writing, release notes, release note draft.',
  'triggers': ['content-operator',
               'content operator',
               'content workflow',
               'writing workflow',
               'publish-ready writing',
               'publish ready writing',
               'release notes',
               'release note draft'],
  'category': 'content',
  'phase': 'content-task',
  'role': 'guide',
  'source_folder': 'omh-content-operator',
  'source_path': 'skills/omh-content-operator/SKILL.md',
  'source_sha256': 'cb842f86a965133d2c74bc2a22e04e39fbab684d3301e6acff56a31e9acb3853',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['content_task_card/v1',
                       'source_scope/v1',
                       'audience_tone_style/v1',
                       'content_review_gate/v1',
                       'content_output_manifest/v1 when observed',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['content_task_card/v1 metadata-only wrapper card when prepared',
                            'source_scope/v1 with supplied sources, missing sources, fact-risk, citation need, and '
                            'no-invention rule',
                            'audience_tone_style/v1 with audience, channel, language, tone, style guide, length, '
                            'format, and accessibility constraints',
                            'content_review_gate/v1 separating draft, reviewer approval, legal/compliance needs, '
                            'publish/send/file-export authority, and stop condition',
                            'content_output_manifest/v1 only when produced draft, revision diff, approval, export, '
                            'publish, or delivery evidence is observed'],
  'acceptance_criteria': ['Audience, channel, language, tone, style guide, length, source scope, fact-risk, review '
                          'owner, and stop condition are explicit.',
                          'Missing facts, source gaps, claims needing citations, legal/compliance needs, approval, '
                          'publish/send authority, and file-export needs are gated or marked missing.',
                          'Published, sent, exported, approved, and fact-verified claims are reported only from '
                          'observed evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'toolbelt-readiness, deliverable-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness', 'deliverable-package'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member content-operator is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as '
                       'Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                       'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                       'recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'data-analysis',
  'family_id': 'data-analysis',
  'description': '[omh] Dataset or table to analyze: scope supplied data with provenance, causal-claim, and '
                 'hallucination guards. Use when the user says: data-analysis, data analysis, dataset analysis, csv '
                 'analysis, json analysis, log analysis, table analysis, analyze csv.',
  'triggers': ['data-analysis',
               'data analysis',
               'dataset analysis',
               'csv analysis',
               'json analysis',
               'log analysis',
               'table analysis',
               'analyze csv'],
  'category': 'analysis',
  'phase': 'data-task',
  'role': 'guide',
  'source_folder': 'omh-data-analysis',
  'source_path': 'skills/omh-data-analysis/SKILL.md',
  'source_sha256': '571206ff152f35aeea7f4d962f35b9e9b8f6f6283dfa8d6b7c8c42e26fc579ec',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['data_analysis_task_card/v1',
                       'dataset_scope/v1',
                       'analysis_method_plan/v1',
                       'operations_data_harness/v1',
                       'product_evidence_loop/v1',
                       'analysis_result_summary/v1 when observed',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['data_analysis_task_card/v1 metadata-only wrapper card when prepared',
                            'dataset_scope/v1 with source, row/record scope, columns or schema, filters, and stop '
                            'condition',
                            'analysis_method_plan/v1 naming summary, anomaly, trend, segment, schema, or log-pattern '
                            'methods',
                            'operations_data_harness/v1 for relationship and causal boundaries',
                            'product_evidence_loop/v1 for prepared opaque data reference metadata',
                            'analysis_result_summary/v1 only from observed data, calculations, query output, or '
                            'supplied evidence'],
  'acceptance_criteria': ['Dataset or corpus source, record scope, schema or extraction method, join assumptions, '
                          'analysis question, method, and stop condition are explicit.',
                          'Numeric claims, anomalies, trends, segments, and log patterns are reported only from '
                          'observed data or supplied evidence.',
                          'Causal claims require observed identification evidence.',
                          'Source acquisition, file conversion, report generation, and code fixes are routed to the '
                          'narrower workflow when stronger.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'report-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['report-package'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member data-analysis is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as '
                       'Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                       'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                       'recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'workspace-file-operator',
  'family_id': 'primitive-operators',
  'description': '[omh] Folder cleanup, renames, or deletions: policy overlay for local file tasks - add path scoping '
                 'and destructive-action gates after preferring native file tools for ordinary list, search, organize, '
                 'copy, move, and rename actions. Use when the user says: workspace-file-operator, workspace file '
                 'operator, file operator, file operation, file operations, filesystem task, filesystem operation, '
                 'file system task.',
  'triggers': ['workspace-file-operator',
               'workspace file operator',
               'file operator',
               'file operation',
               'file operations',
               'filesystem task',
               'filesystem operation',
               'file system task'],
  'category': 'filesystem',
  'phase': 'file-task',
  'role': 'guide',
  'source_folder': 'omh-files',
  'source_path': 'skills/omh-files/SKILL.md',
  'source_sha256': 'b0051a22d4b8ec86afc5594642c747fe099c316c702745e414ec75dac8d5c3a8',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['workspace_file_task_card/v1',
                       'file_operation_scope/v1',
                       'file_observation_manifest/v1 when observed',
                       'file_confirmation_gate/v1 when destructive',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['workspace_file_task_card/v1 metadata-only wrapper card when prepared',
                            'file_operation_scope/v1 with path root, allowed operations, excluded paths, and stop '
                            'condition',
                            'file_observation_manifest/v1 only when directory listings, file stats, hashes, diffs, or '
                            'operation output are observed',
                            'session_file_activity/v1 (`omh quality-evidence file-activity --hermes-session <id> '
                            "--json`) cited in that manifest for which workspace files a Hermes session's read_file, "
                            'write_file, and patch calls named and the outcome Hermes recorded; never as file-content, '
                            'hash, diff, test, review, CI, or merge evidence',
                            'file_confirmation_gate/v1 for delete, overwrite, move, rename, chmod, archive mutation, '
                            'or irreversible cleanup'],
  'acceptance_criteria': ['The path root, allowed file operations, excluded paths, destructive-operation policy, and '
                          'stop condition are explicit.',
                          'Delete, overwrite, move, rename, permission change, archive mutation, upload, and download '
                          'are gated or marked missing.',
                          'Directory listings, file contents, hashes, diffs, and operation results are reported only '
                          'from observed file evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'toolbelt-readiness, deliverable-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness', 'deliverable-package'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member workspace-file-operator is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as '
                       'Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                       'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                       'recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'finance-analysis',
  'family_id': 'finance',
  'description': '[omh] Company budget overrun, cash risk, or close issue: turn finance and accounting inputs into a '
                 'decision-ready variance, cash, and close-risk brief. Use when the user says: finance analysis, '
                 'budget variance, budget vs actual, month-end close, 재무 분석, 예산 대비 실적, 월마감.',
  'triggers': ['finance-analysis',
               'finance analysis',
               'budget variance',
               'budget vs actual',
               'month-end close',
               '재무 분석',
               '예산 대비 실적',
               '월마감'],
  'category': 'operations',
  'phase': 'finance-analysis',
  'role': 'operator',
  'source_folder': 'omh-finance-analysis',
  'source_path': 'skills/omh-finance-analysis/SKILL.md',
  'source_sha256': 'a0263ea7e99e71e903e4c7997497854d02cadad3060f826bed1e4eb95cba89d9',
  'required_inputs': ['period', 'supplied finance source', 'decision question', 'calculation assumptions'],
  'expected_outputs': ['finance_scope_source_record/v1',
                       'finance_reconciliation_analysis_schedule/v1',
                       'finance_risk_register/v1',
                       'finance_decision_brief/v1'],
  'artifact_expectations': ['prepared finance analysis brief when a wrapper captures it'],
  'acceptance_criteria': ['Confirm the workflow target, evidence boundary, and stop condition are named.',
                          'Report which outputs are prepared, observed, blocked, or missing.',
                          'Name the smallest next verification or handoff instead of claiming completion from '
                          'narration.'],
  'handoff_policy': 'Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work '
                    'routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, '
                    'filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a '
                    'connector, file, coding, or human-review handoff only when the user explicitly accepts that next '
                    'step; report it only from observed evidence. Calculations are only as authoritative as supplied '
                    'or observed sources and methods; no ERP, bank, ledger, tax, payment, or filing action is implied.',
  'catalog_rules': ['Source routing exclusion: The request is for a current quote, exchange rate, crypto price, or '
                    'other live market lookup; use `live-info-operator`.',
                    'Source routing exclusion: The user wants generic exploration of a supplied CSV or table without '
                    'accounting periods, controls, or finance decision framing; use `data-analysis`.',
                    'Source routing exclusion: The user asks to post journal entries, reconcile accounts, approve '
                    'payments, submit tax filings, or configure an accounting system; use `connector-operator` for an '
                    'explicit observed action path.',
                    'Source routing exclusion: The user wants pipeline coverage, deal health, or a seller forecast '
                    'scenario rather than authoritative revenue or close reporting; use `sales-pipeline-review`.',
                    'Source routing exclusion: The user needs an enterprise or product direction decision after '
                    'analysis; route that decision to `strategy-brief`.',
                    'Source routing exclusion: The ask is testing whether an internal control operated -- a SOX or '
                    "ICFR sample, re-performance, or a deficiency's severity; use `internal-audit`.",
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'ops-review, report-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ops-review', 'report-package'],
  'references': [{'relative_path': 'omh-finance-analysis/references/procedure.md',
                  'content': '# finance-analysis Specialist Procedure\n'
                             '\n'
                             'Expert clarification questions:\n'
                             '- `period`\n'
                             '  - English: What period, cutoff, reporting entity/perimeter, currency/units, accounting '
                             'basis, comparator version, and close status apply?\n'
                             '  - Korean: 어떤 기간, 마감 기준일, 보고 법인과 범위, 통화와 단위, 회계 기준, 비교 버전, 마감 상태를 적용해야 하나요?\n'
                             '- `supplied finance source`\n'
                             '  - English: Which actual and comparator sources, provenance, versions, completeness '
                             'checks, account mappings, and tie-out status are supplied?\n'
                             '  - Korean: 어떤 실적 및 비교 자료와 출처, 버전, 완전성 점검, 계정 매핑, 대사 상태가 제공되었나요?\n'
                             '- `decision question`\n'
                             '  - English: Which decision, owner, threshold or materiality boundary, and deadline '
                             'should the analysis support?\n'
                             '  - Korean: 이 분석이 지원할 의사결정, 책임자, 임계값 또는 중요성 기준, 기한은 무엇인가요?\n'
                             '- `calculation assumptions`\n'
                             '  - English: Which formulas, approved policy sources, materiality, FX or allocation '
                             'treatments, and challenged assumptions apply?\n'
                             '  - Korean: 어떤 공식, 승인된 정책 근거, 중요성, 환율 또는 배부 처리, 검토할 가정을 적용해야 하나요?\n'
                             '\n'
                             '## Procedure\n'
                             '\n'
                             'Declared checks:\n'
                             '- `finance_scope_comparability_check`\n'
                             '  - Required result fields: `entity_perimeter`, `period_cutoff`, `currency_units`, '
                             '`accounting_basis`, `comparator_version`, `close_status`, `source_provenance`\n'
                             '  - Criterion: PASS only when scope and comparator attributes are supplied and '
                             'comparable; otherwise HOLD with each missing or conflicting attribute.\n'
                             '- `finance_source_reconciliation_check`\n'
                             '  - Required result fields: `totals_status`, `account_mapping_status`, '
                             '`basis_units_status`, `cutoff_status`, `duplicate_missing_status`, `tie_out_status`, '
                             '`unreconciled_gaps`\n'
                             '  - Criterion: Record totals, mappings, basis and units, cutoff, duplicate or missing '
                             'records, and tie-out evidence; never label an untied extract reconciled.\n'
                             '- `finance_policy_assumption_check`\n'
                             '  - Required result fields: `formula_provenance`, `policy_provenance`, '
                             '`materiality_status`, `fx_allocation_treatment`, `assumption_approval_status`\n'
                             '  - Criterion: Use supplied formulas, policy, thresholds, FX, and allocations; mark '
                             'every unsupplied choice an unapproved assumption and infer no accounting policy or '
                             'assurance.\n'
                             '- `finance_conditional_interpretation_check`\n'
                             '  - Required result fields: `analysis_applicability`, `revenue_bridge_status`, '
                             '`receivables_dso_status`, `working_capital_status`, `unavailable_evidence`\n'
                             '  - Criterion: Run only relevant supported analyses; distinguish bookings, billings, '
                             'recognized and deferred revenue and cutoff, or calculate DSO, aging, AR, AP, inventory '
                             'and working-capital movement only from stated comparable formulas and balances.\n'
                             '- `finance_validation_escalation_check`\n'
                             '  - Required result fields: `recalculation_status`, `reconciliation_status`, '
                             '`source_conflicts`, `control_exceptions`, `high_impact_assumptions`, `disposition`, '
                             '`escalation_owner`\n'
                             '  - Criterion: HOLD authoritative conclusions and escalate unresolved policy, cutoff, '
                             'source conflict, control exception, failed recalculation, or high-impact assumption to a '
                             'qualified finance or accounting owner.\n'
                             '\n'
                             '### `finance_scope_sources` (analysis)\n'
                             '\n'
                             'Capture the reporting and comparator perimeter, units, basis, versions, close state, '
                             'provenance, and explicit evidence gaps before interpreting amounts.\n'
                             '\n'
                             '- Input refs: `period`, `supplied finance source`\n'
                             '- Output refs: `finance_scope_source_record/v1`\n'
                             '- Check IDs: `finance_scope_comparability_check`\n'
                             '\n'
                             '### `finance_reconcile_sources` (validation)\n'
                             '\n'
                             'Tie totals and account mappings, normalize only approved basis and units, test cutoff '
                             'and duplicate or missing records, and preserve unreconciled gaps.\n'
                             '\n'
                             '- Input refs: `period`, `supplied finance source`\n'
                             '- Output refs: `finance_reconciliation_analysis_schedule/v1`\n'
                             '- Check IDs: `finance_source_reconciliation_check`\n'
                             '\n'
                             '### `finance_analyze_variances` (analysis)\n'
                             '\n'
                             'Recalculate comparable variances with supplied formulas and thresholds, separating '
                             'facts, approved policy, proposed assumptions, and material decision effects.\n'
                             '\n'
                             '- Input refs: `supplied finance source`, `calculation assumptions`, `decision question`\n'
                             '- Output refs: `finance_reconciliation_analysis_schedule/v1`\n'
                             '- Check IDs: `finance_policy_assumption_check`\n'
                             '\n'
                             '### `finance_interpret_conditionally` (analysis)\n'
                             '\n'
                             'Apply revenue, receivables, liquidity, or working-capital interpretation only when '
                             'relevant evidence exists, and mark unavailable analyses rather than forcing them.\n'
                             '\n'
                             '- Input refs: `supplied finance source`, `calculation assumptions`, `decision question`\n'
                             '- Output refs: `finance_risk_register/v1`\n'
                             '- Check IDs: `finance_conditional_interpretation_check`\n'
                             '\n'
                             '### `finance_validate_brief` (validation)\n'
                             '\n'
                             'Report recalculation and reconciliation status, evidence-linked risks, assumptions, '
                             'decision options and owners, and a PASS or HOLD disposition with mandatory escalation '
                             'gaps.\n'
                             '\n'
                             '- Input refs: `period`, `supplied finance source`, `decision question`, `calculation '
                             'assumptions`\n'
                             '- Output refs: `finance_decision_brief/v1`\n'
                             '- Check IDs: `finance_scope_comparability_check`, `finance_source_reconciliation_check`, '
                             '`finance_policy_assumption_check`, `finance_conditional_interpretation_check`, '
                             '`finance_validation_escalation_check`\n',
                  'source_path': 'skills/omh-finance-analysis/references/procedure.md',
                  'source_sha256': '0fd8b3ad528d10aebd971c26375de9775e95429d3dbdc3a6f2ee5cc063a9c79c'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member finance-analysis is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep domain '
                       'framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in '
                       'Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, '
                       'send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, '
                       'file, coding, or human-review handoff only when the user explicitly accepts that next step; '
                       'report it only from observed evidence. Calculations are only as authoritative as supplied or '
                       'observed sources and methods; no ERP, bank, ledger, tax, payment, or filing action is implied. '
                       'No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence '
                       'is implied.'},
 {'canonical_id': 'instinct-ledger',
  'family_id': 'atomic-instincts',
  'description': '[omh] Recurring lessons worth promoting: turn repeated project or cross-project lessons into atomic, '
                 'confidence-scored instinct candidates with scoped promotion and export boundaries. Use when the user '
                 'says: instinct-ledger, instinct ledger, project instincts, project-scoped instincts, project scoped '
                 'instincts, global instincts, instinct review, instinct candidate.',
  'triggers': ['instinct-ledger',
               'instinct ledger',
               'project instincts',
               'project-scoped instincts',
               'project scoped instincts',
               'global instincts',
               'instinct review',
               'instinct candidate'],
  'category': 'optimization',
  'phase': 'instinct-ledger',
  'role': 'tracker',
  'source_folder': 'omh-instinct-ledger',
  'source_path': 'skills/omh-instinct-ledger/SKILL.md',
  'source_sha256': 'dfa7798ccd95bd2a92ffc5c0a0451f90675af65411cc1f8e74472ac1805b1a4b',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['instinct_ledger_plan/v1',
                       'instinct_candidate/v1',
                       'project_instinct_scope_map/v1',
                       'instinct_promotion_review/v1',
                       'instinct_export_review/v1 when requested'],
  'artifact_expectations': ['instinct_candidate/v1 with trigger, action, confidence, domain, scope, source evidence, '
                            'non-goals, and review state',
                            'project_instinct_scope_map/v1 separating project, global, imported, and '
                            'promotion-candidate instincts',
                            'instinct_promotion_review/v1 with repeated evidence, confidence threshold, conflicts, and '
                            'approval state',
                            'instinct_export_review/v1 with redaction, destination, import/export trust gaps, and '
                            'raw-observation exclusion when requested'],
  'acceptance_criteria': ['Each instinct is atomic: one trigger, one action, one scope, confidence, evidence refs, and '
                          'review state.',
                          'Project-specific conventions, global practices, project/global promotion candidates, '
                          'imports, and exports are separated.',
                          'No hooks, memory writes, skill edits, global promotion, import/export, or behavior-change '
                          'claims are made without observed approval and implementation evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'workflow-learning as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['workflow-learning'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member instinct-ledger is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as '
                       'Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                       'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                       'recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'legal-compliance-review',
  'family_id': 'legal',
  'description': '[omh] Business contract, NDA, or policy with legal risk: surface contract and compliance risks, '
                 'questions, and escalation points before a legal decision or action. Use when the user says: contract '
                 'review, contract liability clause, regulatory analysis, compliance review, contract redline, redline '
                 'the contract, negotiation preparation, negotiation strategy.',
  'triggers': ['legal-compliance-review',
               'contract review',
               'contract liability clause',
               'regulatory analysis',
               'compliance review',
               'contract redline',
               'redline the contract',
               'negotiation preparation',
               'negotiation strategy'],
  'category': 'review',
  'phase': 'legal-compliance-review',
  'role': 'reviewer',
  'source_folder': 'omh-legal-compliance-review',
  'source_path': 'skills/omh-legal-compliance-review/SKILL.md',
  'source_sha256': 'e2c82551a10012f0a0c753b5d474ce8be8a2dc410cc490a3ad259f3193701d22',
  'required_inputs': ['jurisdiction', 'document or process version', 'supplied authority', 'review objective'],
  'expected_outputs': ['legal_scope_authority_record/v1',
                       'legal_issue_traceability_matrix/v1',
                       'legal_risk_counsel_hold_register/v1',
                       'legal_negotiation_preparation/v1 when the objective is a redline rather than an assessment',
                       'legal_review_disposition/v1'],
  'artifact_expectations': ['prepared legal and compliance issue matrix when a wrapper captures it',
                            'legal_negotiation_preparation/v1 with one row per contested clause: the playbook position '
                            'it came from, the proposed language, the fallback, and the walk-away, plus the concession '
                            'order across rows'],
  'acceptance_criteria': ['Findings or no-issue results are grounded in concrete file, artifact, command, or source '
                          'evidence.',
                          'Open questions, residual risk, and missing verification are named.',
                          'Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement '
                          'them.'],
  'handoff_policy': 'Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work '
                    'routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, '
                    'filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a '
                    'connector, file, coding, or human-review handoff only when the user explicitly accepts that next '
                    'step; report it only from observed evidence. The result is a prepared review and escalation aid, '
                    'not legal advice, counsel sign-off, compliance certification, contract execution, filing, or '
                    'regulator communication.',
  'catalog_rules': ['Source routing exclusion: The user needs a final jurisdiction-specific legal opinion, legal '
                    'representation, or authoritative filing decision; prepare the issue and counsel brief instead.',
                    'Source routing exclusion: The review is about code, secrets, permissions, prompt injection, '
                    'dependencies, or unsafe tool behavior; use `security-safety-review`.',
                    'Source routing exclusion: The request is a plain-language rewrite without a legal-risk review '
                    'objective; use `content-operator`.',
                    'Source routing exclusion: The user asks to sign, accept, submit, file, publish, or change a '
                    'policy or contract in an external system; use `connector-operator` only after explicit authority.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'code-review as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['code-review'],
  'references': [{'relative_path': 'omh-legal-compliance-review/references/negotiation-preparation.md',
                  'content': '# Negotiation Preparation\n'
                             '\n'
                             'This is the output mode where the objective is a redline rather than an\n'
                             'assessment: proposed language, fallbacks, and a concession order, prepared for\n'
                             'the person who will negotiate.\n'
                             '\n'
                             'The boundary from the rest of this workflow carries through unchanged. This is\n'
                             'preparation material, never legal advice. A proposed clause says "here is\n'
                             'language that matches the playbook position, and here is what it gives up"; it\n'
                             'never says whether to accept a term, whether a clause is enforceable, or what\n'
                             'the law requires. The authority-citation and counsel-hold rules apply to every\n'
                             'row.\n'
                             '\n'
                             '## Requires a playbook\n'
                             '\n'
                             "Preparation is against the organization's OWN positions. Without a playbook -\n"
                             'standard terms, approved deviations, and what needs escalation - a proposal is\n'
                             'an invented position, and inventing a position is the failure this whole\n'
                             'workflow exists to prevent. If none is supplied, ask for it, or say that rows\n'
                             "are being prepared against the counterparty's draft alone and carry no approved\n"
                             'position behind them.\n'
                             '\n'
                             '## The row\n'
                             '\n'
                             'One row per contested clause:\n'
                             '\n'
                             '| Field | Content |\n'
                             '| --- | --- |\n'
                             "| `clause` | the counterparty's language, by its own reference |\n"
                             '| `playbook_position` | the standard position, cited to the playbook clause |\n'
                             '| `gap` | what the draft does that the position does not allow |\n'
                             '| `proposed` | the replacement language |\n'
                             '| `fallback` | the next acceptable position if the proposal is refused |\n'
                             '| `walk_away` | the point past which escalation is required, and to whom |\n'
                             '| `counsel_hold` | open or closed, from the hold register |\n'
                             '\n'
                             '`fallback` and `walk_away` are not optional. A redline with a proposal and\n'
                             'nothing behind it puts the negotiator in front of a counterparty with one\n'
                             'position and no room, and the first refusal becomes an escalation that could\n'
                             'have been planned.\n'
                             '\n'
                             '**An open counsel hold blocks the row.** A clause with an unresolved\n'
                             'enforceability, privilege, uncapped-liability, or regulatory-deadline trigger\n'
                             'gets a counsel question, not a proposal. Proposing language over an open hold is\n'
                             'how preparation turns into advice.\n'
                             '\n'
                             '## Concession order across rows\n'
                             '\n'
                             'Rank the rows by what the organization actually loses, not by how contested\n'
                             'they are. Then state which are linked - a concession on liability that assumes a\n'
                             'cap elsewhere is one position, and trading it away separately loses both halves.\n'
                             'Record what each concession buys: an ordering with no exchange is a list of\n'
                             'things to give away.\n'
                             '\n'
                             'Three rows that usually rank higher than they read: an indemnity whose cap is\n'
                             'set elsewhere in the document, a termination-for-convenience clause with an\n'
                             'asymmetric notice period, and an audit right with no scope or frequency limit.\n'
                             '\n'
                             '## What the negotiator gets\n'
                             '\n'
                             'The rows, the concession order with its linkages, the counsel questions that\n'
                             'are still open, and an explicit statement of what was not reviewed - clauses\n'
                             'outside the supplied instruments, exhibits that were not provided, and any\n'
                             'version uncertainty. A preparation pack that does not say what it did not see\n'
                             'reads as complete.\n'
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'Prepared negotiation material is not legal advice, counsel sign-off, an\n'
                             'accepted position, an executed amendment, or a communication to the\n'
                             'counterparty. Every authority-dependent statement in a row traces to supplied\n'
                             'authority with an exact locator and status, exactly as in the issue matrix, and\n'
                             'an unresolved hold blocks a final determination here as it does everywhere else\n'
                             'in this workflow.\n',
                  'source_path': 'skills/omh-legal-compliance-review/references/negotiation-preparation.md',
                  'source_sha256': 'a0952b301dc12976606e979590da1f01c9b71d4cd5892f6b2f453536b2e4b4c1'},
                 {'relative_path': 'omh-legal-compliance-review/references/procedure.md',
                  'content': '# legal-compliance-review Specialist Procedure\n'
                             '\n'
                             'Expert clarification questions:\n'
                             '- `jurisdiction`\n'
                             '  - English: Which parties, actor or data roles, operative facts, governing law and '
                             'forum, and separately applicable regulatory jurisdictions are supplied?\n'
                             '  - Korean: 어떤 당사자, 행위자 또는 데이터 역할, 주요 사실, 준거법과 관할, 별도 적용 규제 관할권이 제공되었나요?\n'
                             '- `document or process version`\n'
                             '  - English: Which instrument type, complete document set and precedence, version, '
                             'execution/effective date, amendments, and as-of date are in scope?\n'
                             '  - Korean: 어떤 문서 유형, 전체 문서 세트와 우선순위, 버전, 체결일과 효력일, 개정본, 기준일이 범위에 포함되나요?\n'
                             '- `supplied authority`\n'
                             '  - English: Which supplied authority identifiers, issuers, versions, effective status, '
                             'exact pinpoints, hierarchy, and verification state may be used?\n'
                             '  - Korean: 사용 가능한 제공 근거의 식별자, 발행기관, 버전, 효력 상태, 정확한 인용 위치, 위계, 검증 상태는 무엇인가요?\n'
                             '- `review objective`\n'
                             '  - English: Which decision, risk tolerance, approval owner, deadline, and mandatory '
                             'counsel questions should the review support?\n'
                             '  - Korean: 이 검토가 지원할 의사결정, 위험 허용 범위, 승인 책임자, 기한, 필수 법률 자문 질문은 무엇인가요?\n'
                             '\n'
                             '## Procedure\n'
                             '\n'
                             'Declared checks:\n'
                             '- `legal_scope_facts_instruments_check`\n'
                             '  - Required result fields: `actors_roles`, `operative_facts`, `instrument_set`, '
                             '`order_of_precedence`, `governing_law_forum`, `regulatory_jurisdictions`, '
                             '`execution_effective_as_of_dates`, `assumptions_blockers`\n'
                             '  - Criterion: Require material facts and roles, complete instruments and precedence, '
                             'distinct contractual and regulatory jurisdictions, and temporal scope; never infer '
                             'missing values.\n'
                             '- `legal_authority_citation_check`\n'
                             '  - Required result fields: `source_type`, `source_identifier`, `source_version`, '
                             '`effective_status`, `pinpoint`, `operative_text_summary`, `verification_status`\n'
                             '  - Criterion: Each authority-dependent proposition must trace to supplied or observed '
                             'authority and an exact locator and status; user summaries and inferences stay '
                             'unverified.\n'
                             '- `legal_issue_matrix_check`\n'
                             '  - Required result fields: `applicability_facts`, `obligation_position`, '
                             '`definitions_dependencies`, `exceptions_carveouts_conflicts`, `evidence_status`, '
                             '`risk_uncertainty`, `action_owner`, `recommended_disposition`, `counsel_question`, '
                             '`issue_family_applicability`\n'
                             '  - Criterion: Map facts to operative text, dependencies, exceptions and conflicts; when '
                             'triggered cover warranty, disclaimer, indemnity and liability interactions or privacy '
                             'roles, basis, transfers, security, breach, retention, rights and DPIA, marking other '
                             'families not applicable.\n'
                             '- `legal_counsel_hold_check`\n'
                             '  - Required result fields: `trigger_ids`, `impact`, `likelihood_applicability`, '
                             '`urgency`, `evidence_confidence`, `reversibility`, `hold_status`, `counsel_owner`\n'
                             '  - Criterion: Mandatory HOLD triggers include uncertain or conflicting authority, '
                             'missing jurisdiction or dates, enforceability or privilege, material or uncapped '
                             'liability or indemnity, regulatory deadlines, and sensitive, high-risk or cross-border '
                             'privacy or DPIA uncertainty.\n'
                             '- `legal_negotiation_preparation_check`\n'
                             '  - Required result fields: `playbook_position`, `gap`, `proposed_language`, '
                             '`fallback_position`, `walk_away_trigger`, `concession_order`, `counsel_hold_state`\n'
                             '  - Criterion: Every proposed clause traces to a cited playbook position and carries its '
                             'fallback and walk-away; a row whose position cannot be cited becomes a counsel question, '
                             'an open hold blocks its row, and the concession order states which rows are linked.\n'
                             '- `legal_final_determination_guard`\n'
                             '  - Required result fields: `invented_authority_status`, `stale_authority_status`, '
                             '`unresolved_triggers`, `disposition`\n'
                             '  - Criterion: Fail closed on absent, fabricated, stale, superseded or unverified '
                             'authority; invent no citation, holding, requirement or compliance conclusion and issue '
                             'no final determination while a hold remains open.\n'
                             '\n'
                             '### `legal_scope_facts_instruments` (analysis)\n'
                             '\n'
                             'Record actors, roles, facts, instrument set and precedence, governing law, forum, '
                             'regulatory reach, dates, objective, and every missing assumption or blocker.\n'
                             '\n'
                             '- Input refs: `jurisdiction`, `document or process version`, `review objective`\n'
                             '- Output refs: `legal_scope_authority_record/v1`\n'
                             '- Check IDs: `legal_scope_facts_instruments_check`\n'
                             '\n'
                             '### `legal_trace_authority` (validation)\n'
                             '\n'
                             'Create a citation ledger using only supplied or observed sources, exact pinpoints and '
                             'effective status; route absent authority to research or counsel instead of filling it '
                             'in.\n'
                             '\n'
                             '- Input refs: `supplied authority`, `document or process version`\n'
                             '- Output refs: `legal_scope_authority_record/v1`\n'
                             '- Check IDs: `legal_authority_citation_check`, `legal_final_determination_guard`\n'
                             '\n'
                             '### `legal_map_issues_exceptions` (analysis)\n'
                             '\n'
                             'Build clause and obligation rows with facts-to-rule traceability, definitions, '
                             'dependencies, exceptions, conflicts, evidence state, uncertainty, disposition and '
                             'counsel questions, adding only triggered issue families.\n'
                             '\n'
                             '- Input refs: `jurisdiction`, `document or process version`, `supplied authority`, '
                             '`review objective`\n'
                             '- Output refs: `legal_issue_traceability_matrix/v1`\n'
                             '- Check IDs: `legal_issue_matrix_check`\n'
                             '\n'
                             '### `legal_apply_counsel_holds` (production)\n'
                             '\n'
                             'Rank impact, applicability, urgency, confidence and reversibility, then impose mandatory '
                             'counsel holds and owners for every triggered high-risk or authority-sensitive issue.\n'
                             '\n'
                             '- Input refs: `jurisdiction`, `supplied authority`, `review objective`\n'
                             '- Output refs: `legal_risk_counsel_hold_register/v1`\n'
                             '- Check IDs: `legal_counsel_hold_check`\n'
                             '\n'
                             '### `legal_prepare_negotiation_positions` (production)\n'
                             '\n'
                             'When the objective is a redline, build one row per contested clause -- playbook '
                             'position, gap, proposed language, fallback, walk-away, counsel-hold state -- then rank '
                             'the concession order by what is lost and name the linked rows; prepare nothing for a '
                             'clause whose hold is open.\n'
                             '\n'
                             '- Input refs: `document or process version`, `supplied authority`, `review objective`\n'
                             '- Output refs: `legal_negotiation_preparation/v1 when the objective is a redline rather '
                             'than an assessment`\n'
                             '- Check IDs: `legal_negotiation_preparation_check`, `legal_counsel_hold_check`\n'
                             '\n'
                             '### `legal_validate_disposition` (validation)\n'
                             '\n'
                             'Return PASS, REVISE, or HOLD with exact open triggers and counsel route; prohibit final '
                             'legal or compliance determinations until all mandatory holds are resolved by qualified '
                             'counsel.\n'
                             '\n'
                             '- Input refs: `jurisdiction`, `document or process version`, `supplied authority`, '
                             '`review objective`\n'
                             '- Output refs: `legal_review_disposition/v1`\n'
                             '- Check IDs: `legal_scope_facts_instruments_check`, `legal_authority_citation_check`, '
                             '`legal_issue_matrix_check`, `legal_counsel_hold_check`, '
                             '`legal_final_determination_guard`\n',
                  'source_path': 'skills/omh-legal-compliance-review/references/procedure.md',
                  'source_sha256': '670f501f3136c0f5456b82149ca24153f1b38d5151f539a9b1ab0df30e2f0b58'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member legal-compliance-review is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep domain '
                       'framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in '
                       'Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, '
                       'send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, '
                       'file, coding, or human-review handoff only when the user explicitly accepts that next step; '
                       'report it only from observed evidence. The result is a prepared review and escalation aid, not '
                       'legal advice, counsel sign-off, compliance certification, contract execution, filing, or '
                       'regulator communication. No executor/provider/runtime execution, observed result, review, CI, '
                       'deploy, or merge evidence is implied.'},
 {'canonical_id': 'live-info-operator',
  'family_id': 'primitive-operators',
  'description': '[omh] Live rate, score, or local time a work task needs: policy overlay for live lookups - add '
                 'provider, freshness, units, and source-quality gates after preferring native live-data tools for '
                 'ordinary weather, finance, sports, maps, and time-zone requests. Use when the user says: '
                 'live-info-operator, live info operator, live information, real time information, real-time '
                 'information, weather today, current weather, weather forecast.',
  'triggers': ['live-info-operator',
               'live info operator',
               'live information',
               'real time information',
               'real-time information',
               'weather today',
               'current weather',
               'weather forecast'],
  'category': 'live-info',
  'phase': 'live-info-task',
  'role': 'guide',
  'source_folder': 'omh-live-info',
  'source_path': 'skills/omh-live-info/SKILL.md',
  'source_sha256': '31df680b2f1c9ab7d3ce011a8bdb14129c6658ab81a1059b2eeaedf7cc6bf55d',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['live_info_task_card/v1',
                       'live_info_scope/v1',
                       'freshness_boundary/v1',
                       'live_info_result_manifest/v1 when observed',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['live_info_task_card/v1 metadata-only wrapper card when prepared',
                            'live_info_scope/v1 with domain, location or symbol, time window, provider preference, '
                            'units, and stop condition',
                            'freshness_boundary/v1 separating requested recency, provider timestamp, source quality, '
                            'and stale-result handling',
                            'live_info_result_manifest/v1 only when provider response, timestamp, quote/source id, or '
                            'rendered result is observed'],
  'acceptance_criteria': ['Domain, location or symbol, time window, provider preference, freshness, units, and stop '
                          'condition are explicit.',
                          'Provider setup, API access, source quality, stale data, and missing location/symbol '
                          'decisions are gated or marked missing.',
                          'Weather, price, score, exchange-rate, time-zone, map, place, and traffic facts are reported '
                          'only from observed provider evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'toolbelt-readiness, deliverable-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness', 'deliverable-package'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member live-info-operator is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as '
                       'Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                       'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                       'recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'localization-review',
  'family_id': 'localization',
  'description': '[omh] Translated product or content release: make a product or content release locale-ready with '
                 'terminology, cultural-fit, and quality-review guidance. Use when the user says: localization review, '
                 'translation QA, locale glossary, 현지화 검토, 번역 QA, 용어집.',
  'triggers': ['localization-review',
               'localization review',
               'translation QA',
               'locale glossary',
               '현지화 검토',
               '번역 QA',
               '용어집'],
  'category': 'review',
  'phase': 'localization-review',
  'role': 'reviewer',
  'source_folder': 'omh-localization-review',
  'source_path': 'skills/omh-localization-review/SKILL.md',
  'source_sha256': '16a8c9bf1b5716695c37dc66effffd0fddaee853e1296e44badcb0dcdb4f8bdf',
  'required_inputs': ['locale', 'audience', 'source version', 'product or content context'],
  'expected_outputs': ['locale/audience/context and source-version brief',
                       'approved-term glossary and transcreation/localization choices',
                       'string/content issue matrix with context, severity, and review owner',
                       'locale QA acceptance criteria and handoff/observed-evidence gaps'],
  'artifact_expectations': ['prepared localization review when a wrapper captures it'],
  'acceptance_criteria': ['Findings or no-issue results are grounded in concrete file, artifact, command, or source '
                          'evidence.',
                          'Open questions, residual risk, and missing verification are named.',
                          'Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement '
                          'them.'],
  'handoff_policy': 'Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work '
                    'routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, '
                    'filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a '
                    'connector, file, coding, or human-review handoff only when the user explicitly accepts that next '
                    'step; report it only from observed evidence. Hermes may draft and review language guidance; it '
                    'does not alter locale files, upload strings, publish translations, validate a rendered build, or '
                    'claim market approval.',
  'catalog_rules': ['Source routing exclusion: The request is a short sentence or word translation or rewrite with no '
                    'product or locale QA context; answer directly or use `content-operator`.',
                    'Source routing exclusion: The user needs fresh rendered UI evidence, clipping checks, or a visual '
                    'PASS/REVISE/BLOCK verdict; use `visual-qa`.',
                    'Source routing exclusion: The user asks to edit locale files, push a '
                    'translation-management-system job, publish strings, or configure localization settings; use '
                    '`workspace-file-operator` or `connector-operator` with explicit target and authority.',
                    'Source routing exclusion: The request asks for a regulatory or contractual conclusion about '
                    'translated legal text; use `legal-compliance-review`.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'materials-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['materials-package'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member localization-review is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep domain '
                       'framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in '
                       'Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, '
                       'send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, '
                       'file, coding, or human-review handoff only when the user explicitly accepts that next step; '
                       'report it only from observed evidence. Hermes may draft and review language guidance; it does '
                       'not alter locale files, upload strings, publish translations, validate a rendered build, or '
                       'claim market approval. No executor/provider/runtime execution, observed result, review, CI, '
                       'deploy, or merge evidence is implied.'},
 {'canonical_id': 'media-input-operator',
  'family_id': 'primitive-operators',
  'description': '[omh] Audio, video, or screenshot to process: user-sent media - audio, video, YouTube links, '
                 'screenshots, receipts, OCR, meeting recordings, transcripts, timestamps, and clip summaries, gated '
                 'for source, permission, and hallucination risk. Use when the user says: media-input-operator, media '
                 'input operator, media input, audio transcription, audio transcript, transcribe audio, transcribe '
                 'this audio, meeting recording.',
  'triggers': ['media-input-operator',
               'media input operator',
               'media input',
               'audio transcription',
               'audio transcript',
               'transcribe audio',
               'transcribe this audio',
               'meeting recording'],
  'category': 'media',
  'phase': 'media-input-task',
  'role': 'guide',
  'source_folder': 'omh-media-input',
  'source_path': 'skills/omh-media-input/SKILL.md',
  'source_sha256': '7bb72c89c13ce8e064bfcd326e075664851456a5dfa7225559a64912e5ea18c9',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['media_input_task_card/v1',
                       'media_source_scope/v1',
                       'transcript_boundary/v1',
                       'media_summary_plan/v1',
                       'media_result_manifest/v1 when observed',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['media_input_task_card/v1 metadata-only wrapper card when prepared',
                            'media_source_scope/v1 with media type, source location, permission boundary, requested '
                            'time range, and stop condition',
                            'transcript_boundary/v1 separating supplied transcript, missing transcript, ASR/extraction '
                            'requirement, language, speaker labels, and confidence gaps',
                            'media_summary_plan/v1 naming action-item, timestamped, clip, chapter, quote, or '
                            'evidence-linked summary method',
                            'media_result_manifest/v1 only when supplied transcript, media file metadata, provider '
                            'response, or observed transcript output exists'],
  'acceptance_criteria': ['Media type, source location, permission boundary, transcript availability, language, '
                          'requested output, timestamp requirement, and stop condition are explicit.',
                          'Downloads, uploads, ASR, transcript extraction, speaker labels, copyrighted media access, '
                          'and provider setup are gated or marked missing.',
                          'Transcript text, OCR output, screenshot text, receipt fields, timestamps, quotes, action '
                          'items, and media-summary claims are reported only from observed media or supplied '
                          'transcript/extraction evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'toolbelt-readiness, deliverable-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness', 'deliverable-package'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member media-input-operator is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as '
                       'Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                       'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                       'recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'model-finetuning',
  'family_id': 'model-finetuning',
  'description': '[omh] Fine-tuning a model on your own data -- SFT, DPO, RLVR or a LoRA adapter: decide first whether '
                 'prompting or retrieval already closes the gap, choose the method from the data you have, and promote '
                 'a checkpoint only when it beats the untuned baseline on a held-out eval. Use when the user says: '
                 'model-finetuning, model finetuning, model fine-tuning, fine-tune a model, fine-tune the model, fine '
                 'tune a model, fine tune the model, fine-tune.',
  'triggers': ['model-finetuning',
               'model finetuning',
               'model fine-tuning',
               'fine-tune a model',
               'fine-tune the model',
               'fine tune a model',
               'fine tune the model',
               'fine-tune'],
  'category': 'planning',
  'phase': 'model-finetuning',
  'role': 'planner',
  'source_folder': 'omh-model-finetuning',
  'source_path': 'skills/omh-model-finetuning/SKILL.md',
  'source_sha256': '3a888f3b0c821a4b2c9844ceab6ec259e16b50f1a096e49a3d6d8522c38610e8',
  'required_inputs': ['the task the model fails at, and the held-out examples that show the failure',
                      'what prompting, few-shot examples, or retrieval were already tried, and what they scored',
                      'the data available: demonstrations, ranked or paired preferences, or answers a program can '
                      'check',
                      'the base model, its license, and the compute or provider the operator will train on',
                      'observed eval scores for the untuned baseline and every candidate checkpoint'],
  'expected_outputs': ['finetune_decision/v1',
                       'training_method_choice/v1',
                       'training_data_plan/v1',
                       'baseline_comparison/v1',
                       'checkpoint_promotion_gate/v1'],
  'artifact_expectations': ['finetune_decision/v1 names the measured gap on the held-out eval and what prompting, '
                            'few-shot, and retrieval scored against it, and returns `do_not_finetune` when one of them '
                            'closes the gap -- a complete outcome, reached before any training step',
                            'training_method_choice/v1 picks SFT, DPO, or RLVR from the shape of the data -- '
                            'demonstrations, preference pairs, or a verifiable reward -- and full weights or an '
                            'adapter, and names the failure mode of the method chosen',
                            'training_data_plan/v1 names each source and its license, the dedupe and filtering, and a '
                            'held-out split drawn before training and checked for overlap with the training set',
                            'baseline_comparison/v1 runs the same held-out eval on the untuned baseline and each '
                            'candidate, per metric, plus a regression check on general capability the task does not '
                            'cover',
                            'checkpoint_promotion_gate/v1 promotes a checkpoint only when it beats the untuned '
                            'baseline by a stated margin with no regression past a stated tolerance, and otherwise '
                            'keeps the baseline serving'],
  'acceptance_criteria': ['The fine-tune decision is stated, and `do_not_finetune` was considered first.',
                          "The method is chosen from the data's shape and its failure mode is named.",
                          'The held-out split was drawn before training and checked for overlap.',
                          'Promotion cites the same eval observed on the untuned baseline and the candidate.',
                          'OMH ran nothing, and every score cites observed output or is marked unverified.'],
  'handoff_policy': 'Keep the fine-tune decision, the method choice, the data plan, the baseline comparison, and the '
                    'promotion gate in Hermes. Losses, eval scores, and comparisons are recorded only from executor, '
                    'operator, or wrapper observed output; OMH never launches a training run, calls a model, or runs '
                    'an eval.',
  'catalog_rules': ['Source first step: Ask what the untuned model and the best prompt score on the held-out examples '
                    'before discussing any method.',
                    'Source first step: Ask what shape the data has -- demonstrations, preference pairs, or answers a '
                    'program can check.',
                    "Source routing exclusion: The ask is onboarding a new model generation into OMH's routing, "
                    'calibration, or pricing; use `model-optimization`.',
                    'Source routing exclusion: The ask is serving an existing model behind an endpoint or benchmarking '
                    'that endpoint; use `inference-serving`.',
                    'Source routing exclusion: The ask is building an application on top of a hosted model -- RAG, '
                    'structured output, prompt versions; use `llm-app-dev`.',
                    'Source routing exclusion: The ask is learning from an OMH run, a missed route, or a skill '
                    'improvement candidate; use `workflow-learning`.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'plan, best-practice-research as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['plan', 'best-practice-research'],
  'references': [{'relative_path': 'omh-model-finetuning/references/finetuning-method.md',
                  'content': '# Fine-Tuning Method\n'
                             '\n'
                             'Load this while planning a fine-tune. OMH prepares; the operator trains, evaluates and '
                             'serves, and each step is `prepared` until its output is observed.\n'
                             '\n'
                             '## 1. Decide whether to fine-tune at all\n'
                             '\n'
                             'Climb the ladder in order and stop at the first rung that closes the measured gap on the '
                             'held-out eval:\n'
                             '\n'
                             '| Rung | Try | Stop here when |\n'
                             '| --- | --- | --- |\n'
                             '| 1 | a clearer instruction and an output schema | the failure was an unstated '
                             'requirement |\n'
                             '| 2 | few-shot examples in the prompt | the failure was format or style the examples '
                             'show |\n'
                             '| 3 | retrieval over the source documents | the failure was missing or stale knowledge '
                             '|\n'
                             '| 4 | a larger or newer base model | the failure was reasoning the current model lacks '
                             '|\n'
                             '| 5 | fine-tuning | none of the above closed the gap, and the task is stable enough to '
                             'be worth a trained artifact |\n'
                             '\n'
                             'Rungs 1 to 4 return `do_not_finetune` with the score that closed the gap. Knowledge that '
                             'changes weekly belongs in retrieval, not in weights.\n'
                             '\n'
                             '## 2. Choose the method from the data\n'
                             '\n'
                             '| Method | The data you have | Use when | Failure mode to watch |\n'
                             '| --- | --- | --- | --- |\n'
                             '| SFT | demonstrations: an input and the output you want | the target behavior can be '
                             "written down | copies the demonstrations' errors and narrows general ability |\n"
                             '| DPO | preference pairs: a chosen and a rejected output for the same input | good and '
                             'bad are easier to rank than to write | drifts from the reference model when pairs are '
                             'noisy or one-sided |\n'
                             '| RLVR | inputs whose answers a program can check: tests, exact answers, a validator | '
                             'correctness is verifiable and demonstrations are scarce | reward hacking: passes the '
                             'checker without solving the task |\n'
                             '\n'
                             'SFT first and DPO after is the common order when both kinds of data exist. A LoRA or '
                             'other adapter trains a small set of extra weights: cheaper, swappable, and easy to roll '
                             'back; train full weights only when an adapter measured short of the gap.\n'
                             '\n'
                             '## 3. Training data checklist\n'
                             '\n'
                             '1. Every source has a license or consent that permits training on it.\n'
                             '2. Deduplicate, and drop examples that contradict each other.\n'
                             '3. Draw the held-out split before training, from the same distribution as real traffic.\n'
                             '4. Check that no held-out example, or a near duplicate of one, is in the training set.\n'
                             '5. Record the counts per source and per split.\n'
                             '\n'
                             '## 4. Compare and promote\n'
                             '\n'
                             '1. Run the same held-out eval, same prompt and same decoding settings, on the untuned '
                             'baseline and on every candidate checkpoint.\n'
                             '2. Add a regression set for general capability the task does not cover.\n'
                             '3. Promote only when the candidate beats the baseline by the stated margin on the task '
                             'metric and regresses no more than the stated tolerance elsewhere.\n'
                             '4. Keep the baseline serving, and keep it as the rollback, until the promoted '
                             "checkpoint's live metrics are observed.\n",
                  'source_path': 'skills/omh-model-finetuning/references/finetuning-method.md',
                  'source_sha256': '10a677fdc07303b3b2b3b0d7759f9b5956e9f00fac94ccad0bac9bdef3d8d797'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member model-finetuning is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep the fine-tune '
                       'decision, the method choice, the data plan, the baseline comparison, and the promotion gate in '
                       'Hermes. Losses, eval scores, and comparisons are recorded only from executor, operator, or '
                       'wrapper observed output; OMH never launches a training run, calls a model, or runs an eval. No '
                       'executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is '
                       'implied.'},
 {'canonical_id': 'production-audit',
  'family_id': 'production-readiness',
  'description': '[omh] Imminent production launch or release: evaluate release, deploy, security, observability, '
                 'rollback, docs, and support readiness without claiming production access. Use when the user says: '
                 'production-audit, production audit, production readiness, prod audit, prod readiness, ready for '
                 'production, ready to ship, ship readiness.',
  'triggers': ['production-audit',
               'production audit',
               'production readiness',
               'prod audit',
               'prod readiness',
               'ready for production',
               'ready to ship',
               'ship readiness'],
  'category': 'review',
  'phase': 'production-readiness',
  'role': 'reviewer',
  'source_folder': 'omh-production-audit',
  'source_path': 'skills/omh-production-audit/SKILL.md',
  'source_sha256': 'be28c1c10dd2a8fdca2e0782fdfbdec209f64375fa589f93d4308ab295964e6f',
  'required_inputs': ['product, service, release, or artifact scope',
                      'target environment and release channel',
                      'known test, CI, deploy, observability, security, and support evidence',
                      'rollback owner and acceptable risk threshold'],
  'expected_outputs': ['production_audit_plan/v1',
                       'readiness_matrix/v1',
                       'release_gate_verdict/v1',
                       'rollback_and_monitoring_plan/v1',
                       'risk_register/v1',
                       'not-evidence boundary'],
  'artifact_expectations': ['readiness_matrix/v1 covering build, tests, CI, security/privacy, performance, '
                            'observability, rollback, docs/support, and release communication',
                            'release_gate_verdict/v1 with GO, HOLD, or BLOCK plus missing evidence',
                            'rollback_and_monitoring_plan/v1 with health signals, owner, threshold, and recovery path',
                            'Artifact contracts:',
                            'This label denotes the machine-enforcement level, not a skill quality score and not an '
                            'observed evidence state.',
                            'contract_id: `readiness_matrix/v1`; enforcement_level: `executable_validated`; '
                            'consumer_id: `parse_readiness_matrix`'],
  'acceptance_criteria': ['Findings or no-issue results are grounded in concrete file, artifact, command, or source '
                          'evidence.',
                          'Open questions, residual risk, and missing verification are named.',
                          'Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement '
                          'them.'],
  'handoff_policy': 'Keep readiness synthesis in Hermes. Code fixes, deploys, infrastructure changes, security scans, '
                    'and platform actions require selected executor/runtime or operator evidence.',
  'catalog_rules': ['Source routing exclusion: The user wants to implement a feature or fix; prepare a coding handoff '
                    'first.',
                    'Source routing exclusion: The user wants incident/SLO analysis after production behavior; use '
                    '`reliability-review`.',
                    'Source routing exclusion: The user wants a narrow code diff review; use `code-review`.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'deploy-and-monitor, ops-review as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['deploy-and-monitor', 'ops-review'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member production-audit is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep readiness '
                       'synthesis in Hermes. Code fixes, deploys, infrastructure changes, security scans, and platform '
                       'actions require selected executor/runtime or operator evidence. No executor/provider/runtime '
                       'execution, observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'release-cut',
  'family_id': 'version-release',
  'description': '[omh] Shipping a versioned release -- tag it, stage it behind a canary, or roll back the last '
                 'deploy: decide what goes in, the version, the rollout stages, and a rollback with its trigger and '
                 'exact command before it is needed. Use when the user says: release-cut, release cut, cut a release, '
                 'cut the release, cut a new release, tag a release, tag the release, release candidate.',
  'triggers': ['release-cut',
               'release cut',
               'cut a release',
               'cut the release',
               'cut a new release',
               'tag a release',
               'tag the release',
               'release candidate'],
  'category': 'planning',
  'phase': 'release-cut',
  'role': 'planner',
  'source_folder': 'omh-release-cut',
  'source_path': 'skills/omh-release-cut/SKILL.md',
  'source_sha256': 'eae75507d98e6f4dfdbcfce89d05a674e64b31112dd3178ead2bc1c33a8146a6',
  'required_inputs': ['the changes since the last release, and the current version and versioning scheme',
                      'how a release is cut here: the workflow or command, the approval gates, and every version '
                      'surface it bumps',
                      'the deploy target, the traffic split available, and the health signals with their normal range',
                      'the rollback mechanism: redeploy of the previous artifact, a flag, or a revert, and who may run '
                      'it',
                      'observed evidence for any published, promoted, or rolled-back claim'],
  'expected_outputs': ['release_scope/v1',
                       'release_plan/v1',
                       'rollout_stages/v1 when the release is staged',
                       'rollback_trigger/v1',
                       'release_readiness_verdict/v1'],
  'artifact_expectations': ['release_scope/v1 lists what goes in and what is held back, and derives the version from '
                            'the change classes: a breaking change, a feature, or a fix',
                            'release_plan/v1 orders the cut: freeze the release branch, bump every version surface, '
                            'tag, run the release workflow, pass its approval gate, publish, and curate the notes',
                            'rollout_stages/v1 gives each stage its traffic share, its bake time, and the promotion '
                            'criterion read from a named health signal',
                            'rollback_trigger/v1 names the signal and threshold that trigger the rollback, the exact '
                            'command that performs it, and who runs it',
                            'release_readiness_verdict/v1 reads ready only when a named rollback trigger and its exact '
                            'command are stated; otherwise it names what is missing'],
  'acceptance_criteria': ['The contents, the held items, and the version are stated.',
                          'Every rollout stage has a traffic share, a bake time, and a promotion criterion.',
                          'The rollback trigger names a signal, a threshold, and the exact command.',
                          'The readiness verdict is ready only when the trigger and the command are named.',
                          'Nothing was tagged, published, deployed, or rolled back by OMH.'],
  'handoff_policy': 'Keep the release contents, the version decision, the rollout stages, the rollback trigger and '
                    'command, and the readiness verdict in Hermes. Tags, workflow runs, approvals, published '
                    'artifacts, canary metrics, and every rollback are recorded only from executor, operator, CI, or '
                    'wrapper observed output; OMH prepares and never publishes, tags, or deploys.',
  'catalog_rules': ['Source first step: State what goes in, what is held back, and the version before proposing the '
                    'cut.',
                    'Source first step: Name the rollback trigger and its exact command before the first stage ships.',
                    'Source routing exclusion: The rollout is already running and the ask is watching its health '
                    'signals and post-deploy status; use `deploy-and-monitor`.',
                    'Source routing exclusion: Production is down or degraded and the work is commanding the incident; '
                    'use `live-incident-response`.',
                    'Source routing exclusion: The ask is a readiness audit across observability, security, and '
                    'operations before launch; use `production-audit`.',
                    'Source routing exclusion: The ask is drafting the commit message or the pull request description '
                    'for a change; use `commit-pr-authoring`.',
                    'Source routing exclusion: The app ships through the App Store or Google Play -- signing, a '
                    'TestFlight or Play testing-track beta, a phased release, a store hotfix; use `mobile-release`.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'deploy-and-monitor as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['deploy-and-monitor'],
  'references': [{'relative_path': 'omh-release-cut/references/release-and-rollback-method.md',
                  'content': '# Release And Rollback Method\n'
                             '\n'
                             'Load this while deciding a release or a rollback. OMH prepares; the host, CI, or an '
                             'operator tags, publishes, deploys, and rolls back, and each step is `prepared` until its '
                             'output is observed.\n'
                             '\n'
                             '## 1. Scope and version\n'
                             '\n'
                             '- List the changes since the last tag and sort them into breaking changes, features, and '
                             'fixes.\n'
                             '- Semantic versioning: any breaking change is a major, otherwise any feature is a minor, '
                             'otherwise a patch. A pre-1.0 project states its own rule.\n'
                             '- Hold back what is not ready behind a flag or out of the branch, and say which.\n'
                             '\n'
                             '## 2. The cut sequence\n'
                             '\n'
                             '| Order | Step | Failure it prevents |\n'
                             '| --- | --- | --- |\n'
                             '| 1 | Land the prep change: changelog entry, and any version surface that gained a check '
                             '| a bump that leaves a surface behind and turns the release branch red |\n'
                             '| 2 | Freeze the release branch: nothing merges until the tag is pushed | a merge in the '
                             'window breaks the atomic push of the bump commit and the tag |\n'
                             '| 3 | Run the cut (a release workflow or command) that bumps every version surface, runs '
                             'the suite on the bumped tree, and pushes the bump commit and the tag atomically | a tag '
                             'that points at a tree nobody tested |\n'
                             '| 4 | Pass the approval gate (a protected environment or a manual approval) | an '
                             'unreviewed publish |\n'
                             '| 5 | Publish, then check each channel moved: package registry, container registry, '
                             'installers, site | a release visible on one channel and missing on another |\n'
                             '| 6 | Curate the notes on top of the generated change list | a list of titles nobody can '
                             'act on |\n'
                             '\n'
                             "Wait for the release branch's own CI on its last merge before starting the cut. After "
                             'the cut, compare every version surface against the tag.\n'
                             '\n'
                             '## 3. Rollout stages\n'
                             '\n'
                             '| Stage | Traffic | Bake time | Promote when |\n'
                             '| --- | --- | --- | --- |\n'
                             '| Canary | 1-5% or one instance | long enough to cover one traffic peak | error rate, '
                             'latency, and saturation stay inside the stated range against the baseline |\n'
                             '| Partial | 25-50% | one more peak | the same signals hold with more load |\n'
                             '| Full | 100% | until the rollback window closes | the previous artifact may be retired '
                             '|\n'
                             '\n'
                             'Promotion reads a named signal against a threshold. A clock alone is not a promotion '
                             'criterion.\n'
                             '\n'
                             '## 4. Rollback trigger and command\n'
                             '\n'
                             'A rollback trigger is a signal, a threshold, and a window: "5xx rate above 1% for 5 '
                             'minutes against the canary cohort". The command is the literal line that performs it, '
                             'and it names who may run it.\n'
                             '\n'
                             '| Mechanism | Command shape | Cannot undo |\n'
                             '| --- | --- | --- |\n'
                             '| Redeploy the previous artifact | `kubectl rollout undo deployment/<name>`, or redeploy '
                             'the previous image tag | data the new version already wrote |\n'
                             '| Traffic shift | set the canary weight to 0 | nothing, while the old version still runs '
                             '|\n'
                             '| Feature flag | turn the flag off | side effects already emitted |\n'
                             '| Revert and re-release | revert the merge, then cut a patch | a published package: yank '
                             'or deprecate it, never delete and reuse the version |\n'
                             '\n'
                             'A rollback that crosses a schema migration needs the migration to be backward compatible '
                             '(expand before contract), or the rollback is a restore, and the plan says which.\n',
                  'source_path': 'skills/omh-release-cut/references/release-and-rollback-method.md',
                  'source_sha256': 'e97a49d65d6b943fa5bbacc4f8083fcd94e52d864cea97301c9b945180e57cc9'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member release-cut is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep the release '
                       'contents, the version decision, the rollout stages, the rollback trigger and command, and the '
                       'readiness verdict in Hermes. Tags, workflow runs, approvals, published artifacts, canary '
                       'metrics, and every rollback are recorded only from executor, operator, CI, or wrapper observed '
                       'output; OMH prepares and never publishes, tags, or deploys. No executor/provider/runtime '
                       'execution, observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'rust',
  'family_id': 'rust',
  'description': '[omh] Rust ownership, lifetime, or unsafe trouble: prepare Rust changes with ownership, error, and '
                 'API discipline, and escalate any unsafe, FFI, or lock-free change to the UB checklist. Use when the '
                 'user says: rust, rust code, rust skill, rustlang, borrow checker, lifetime error, ownership error, '
                 'trait bound.',
  'triggers': ['rust',
               'rust code',
               'rust skill',
               'rustlang',
               'borrow checker',
               'lifetime error',
               'ownership error',
               'trait bound'],
  'category': 'planning',
  'phase': 'rust-development',
  'role': 'planner',
  'source_folder': 'omh-rust',
  'source_path': 'skills/omh-rust/SKILL.md',
  'source_sha256': '8810fd2a8d52e2d4bf36b86c1921b84722fa3f01e6875562987679dcab7e86c2',
  'required_inputs': ['the crate, module, or function being changed',
                      'whether the change touches `unsafe`, raw pointers, FFI, `MaybeUninit`, or a lock-free primitive',
                      "the crate's edition, MSRV, and async runtime when relevant",
                      'existing error type and public API stability constraints',
                      'the gate commands the repository already runs',
                      'observed compiler, clippy, test, and Miri/sanitizer evidence for completion claims'],
  'expected_outputs': ['rust_change_contract/v1',
                       'ownership_shape/v1',
                       'error_and_api_contract/v1',
                       'rust_gate_list/v1',
                       'ub_escalation_verdict/v1',
                       'ub_discipline_checklist/v1 when the escalation triggers',
                       'observed_rust_gate_evidence/v1 when observed'],
  'artifact_expectations': ['rust_change_contract/v1 names the crate, the change, and the escalation verdict on its '
                            'first line',
                            'ownership_shape/v1 states who owns each value, which borrows cross a function or await '
                            'boundary, and where a clone is deliberate rather than a borrow-checker surrender',
                            'error_and_api_contract/v1 names the error type, its conversion boundary, and every '
                            '`unwrap`, `expect`, or `panic!` that survives with its justification',
                            'rust_gate_list/v1 lists the exact commands the executor must run and pass',
                            'ub_escalation_verdict/v1 is `escalated` or `not_escalated` with the trigger that decided '
                            'it',
                            'ub_discipline_checklist/v1 adds the Miri, sanitizer, and loom-style concurrency '
                            'requirements when escalated',
                            'compiler, clippy, test, Miri, sanitizer, and loom results only when observed'],
  'acceptance_criteria': ['The escalation verdict is stated with the trigger that decided it.',
                          'The ownership shape names owners, borrows across boundaries, and every deliberate clone.',
                          'The error type, its conversion boundary, and every surviving `unwrap`/`expect`/`panic!` are '
                          'named.',
                          'The gate list names the exact commands the executor must run and pass.',
                          'An escalated change carries the Miri, sanitizer, and concurrency-testing requirements as '
                          'blocking items.',
                          'Compiler, clippy, test, Miri, sanitizer, and loom results stay observed-only.'],
  'handoff_policy': 'Keep the ownership shape, error-type choice, API surface, gate list, and the UB escalation '
                    'verdict in Hermes. Record compilation, clippy output, test results, Miri runs, sanitizer runs, '
                    'and loom runs only from executor or wrapper observed evidence.',
  'catalog_rules': ['Source routing exclusion: The request is a server, API, or schema design that happens to mention '
                    'a Rust stack; use `backend` for the contract and name Rust as the stack.',
                    'Source routing exclusion: The request is debugging a stripped or source-less native binary; use '
                    '`native-debugging`.',
                    'Source routing exclusion: The request is a general code review of finished Rust; use '
                    '`code-review`.',
                    'Source routing exclusion: The request is a Rust vocabulary or concept question with no change to '
                    'prepare; answer it directly.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'plan, code-review as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['plan', 'code-review'],
  'references': [{'relative_path': 'omh-rust/references/rust-discipline.md',
                  'content': '# Rust Change Discipline\n'
                             '\n'
                             'Load this when preparing a Rust change. The escalation check in '
                             '`references/ub-escalation.md` runs first and is not optional; this reference covers the '
                             'ordinary-Rust half of the contract.\n'
                             '\n'
                             'OMH runs no toolchain. Every command below is one the executor runs and reports.\n'
                             '\n'
                             '## 1. Ownership shape\n'
                             '\n'
                             'The borrow checker is not an obstacle to route around; it is the design surfacing early. '
                             'Before code, name:\n'
                             '\n'
                             '- **Who owns each value**, and for how long.\n'
                             '- **Which borrows cross a boundary** -- a function return, a struct field, an `await` '
                             'point, a thread spawn. Borrows that cross an `await` are the usual reason a future is '
                             'not `Send`.\n'
                             '- **Every deliberate clone**, with the reason. A clone is a legitimate decision when the '
                             'alternative is a lifetime that infects a public API; it is a surrender when it exists '
                             'because an error message would not go away.\n'
                             '- **Every interior-mutability wrapper.** `Rc<RefCell<_>>` and `Arc<Mutex<_>>` move a '
                             'compile-time check to runtime. That trade is sometimes right and is always a decision to '
                             'write down, because the failure mode changes from a build error to a panic or a '
                             'deadlock.\n'
                             '\n'
                             'Escalation ladder when the checker refuses: restructure ownership, then narrow the '
                             "borrow's scope, then split the type, then clone deliberately, then interior mutability. "
                             '`unsafe` is not on this ladder -- reaching for it moves the change into the UB '
                             'escalation.\n'
                             '\n'
                             '## 2. Errors and the API surface\n'
                             '\n'
                             '- Name the error type and where conversion happens. Library crates define their own '
                             'error enum; binaries may collapse to a single boxed error at the top. Mixing the two '
                             'conventions inside one crate is the thing to avoid.\n'
                             '- Every surviving `unwrap`, `expect`, or `panic!` is listed with its justification. "The '
                             'invariant is guaranteed by the constructor" is a justification. Silence is not.\n'
                             "- Panicking in a library is an API decision. Say whether the function's contract allows "
                             'it.\n'
                             '- Make illegal states unrepresentable where the type system can: newtypes for distinct '
                             'semantic primitives, enums over stringly-typed states, exhaustive `match` so a new '
                             'variant is a build error rather than a silent fallthrough.\n'
                             '- Public API changes name their semver impact before the change, not at release.\n'
                             '\n'
                             '## 3. Async and concurrency\n'
                             '\n'
                             '- Say which runtime, and whether the change adds a blocking call inside an async '
                             'context. Blocking inside an async task starves the executor and is invisible until '
                             'load.\n'
                             '- Any shared mutable state names its synchronization primitive and its lock order. Two '
                             'locks with no stated order is a deadlock waiting for scheduling.\n'
                             '- Cancellation is part of the contract: state what happens when a future is dropped '
                             'mid-operation.\n'
                             '- A hand-written lock-free structure is not ordinary Rust. It escalates.\n'
                             '\n'
                             '## 4. The gate list\n'
                             '\n'
                             'Name the exact commands, in this order, and treat each as its own observed state:\n'
                             '\n'
                             '| Gate | What it proves | What it does not prove |\n'
                             '| --- | --- | --- |\n'
                             '| `cargo fmt --check` | formatting | nothing about behavior |\n'
                             "| `cargo clippy -- -D warnings` | lint cleanliness at the crate's configured level | "
                             'nothing about runtime behavior |\n'
                             '| `cargo test` | the tests that exist pass | nothing about paths without tests |\n'
                             '| `cargo test --release` | behavior under optimization | debug-only assertions no longer '
                             'run |\n'
                             '| `cargo doc` | doc links resolve, doc tests compile | nothing about API quality |\n'
                             '\n'
                             "Add the repository's own gates rather than assuming this list is complete. When the "
                             'change is escalated, the Miri and sanitizer gates from `references/ub-escalation.md` are '
                             'appended and are blocking.\n'
                             '\n'
                             '## 5. Failure modes\n'
                             '\n'
                             '| Symptom | What actually went wrong | Correction |\n'
                             '| --- | --- | --- |\n'
                             '| Clones added until it compiled | Ownership was never designed | Name the owner, then '
                             're-derive the borrows |\n'
                             '| `Rc<RefCell<_>>` everywhere | A compile-time problem was moved to runtime | State the '
                             'decision, or restructure |\n'
                             '| `unwrap` in a library path | A contract was assumed rather than encoded | Encode it in '
                             'the type or return the error |\n'
                             '| "It compiles" reported as done | Compilation is one gate of five | Report each gate '
                             'separately |\n'
                             '| `unsafe` used to end a borrow argument | The change silently became a UB-risk change | '
                             'Escalate; the compiler stopped checking |\n'
                             '\n'
                             '## Attribution\n'
                             '\n'
                             'Concept lineage only. The idea of a mandatory per-language reference gate that\n'
                             'escalates on `unsafe`/FFI contact, and of a hypothesis-first native debugging\n'
                             'loop, is adapted from the `programming` and `debugging` skills of the\n'
                             "`omo-ai` plugin; the DAP-over-printf preference is adapted from `can1357/oh-my-pi`'s\n"
                             'first-class debug adapter tooling. No upstream text is reproduced -- the\n'
                             'wording, the artifact vocabulary, and the `prepared_not_observed` claim\n'
                             "boundary are OMH's own, and OMH keeps its no-execution boundary: every command\n"
                             'below is something the executor runs, never OMH.\n',
                  'source_path': 'skills/omh-rust/references/rust-discipline.md',
                  'source_sha256': '7d9b5005213715f4712dac2371fa63699b8ba963e843f360d75789d576c12844'},
                 {'relative_path': 'omh-rust/references/ub-escalation.md',
                  'content': '# Rust UB Escalation\n'
                             '\n'
                             'This is a routing rule, not a judgment call. Run the trigger check on every Rust change '
                             "before anything else, and state the verdict on the contract's first line.\n"
                             '\n'
                             'OMH runs neither Miri nor a sanitizer. Every command below is one the executor runs and '
                             'reports.\n'
                             '\n'
                             '## 1. The trigger check\n'
                             '\n'
                             'The change is **escalated** if it adds, moves, or modifies any of:\n'
                             '\n'
                             '- an `unsafe` block or an `unsafe fn`\n'
                             '- a raw pointer -- `*mut T`, `*const T` -- or any pointer arithmetic\n'
                             '- `MaybeUninit`, `mem::transmute`, `mem::zeroed`, `mem::uninitialized`, or '
                             '`ptr::read`/`ptr::write` family calls\n'
                             '- an FFI boundary: `extern "C"`, `#[no_mangle]`, a `-sys` crate binding, or a callback '
                             'handed to foreign code\n'
                             '- `unsafe impl Send` or `unsafe impl Sync`\n'
                             '- a hand-written lock-free primitive, or any direct use of `core::sync::atomic` ordering '
                             'weaker than `SeqCst`\n'
                             '- `Pin` projection written by hand rather than through a derive\n'
                             '- a `#[repr(...)]` change on a type that crosses an FFI or transmute boundary\n'
                             '\n'
                             'If the change cannot be inspected well enough to answer, the verdict is **escalated**. A '
                             'conservative verdict is correct and is labelled conservative; an unmeasured "not '
                             'escalated" is a false clean.\n'
                             '\n'
                             'Ordinary Rust that touches none of the above is **not escalated**, and '
                             '`references/rust-discipline.md` is the whole bar.\n'
                             '\n'
                             '## 2. What escalation adds\n'
                             '\n'
                             'An escalated change is not ready for handoff until all four are named as blocking '
                             'items:\n'
                             '\n'
                             '1. **The invariant.** Every `unsafe` block states, in a comment the change ships with, '
                             'what it asserts and why the assertion holds. An `unsafe` block with no stated invariant '
                             'is an unreviewable one -- the compiler stopped checking, so the comment is the only '
                             'remaining specification.\n'
                             '2. **Miri.** The affected tests run under Miri. Miri is the oracle for aliasing, '
                             'use-after-free, uninitialized reads, invalid values, misalignment, out-of-bounds access, '
                             'provenance, and double free.\n'
                             '3. **A sanitizer**, where Miri cannot reach -- anything crossing FFI or doing real I/O. '
                             'Address, leak, thread, and memory sanitizers each cover a different class; name which '
                             'one and why.\n'
                             '4. **Concurrency testing** for anything lock-free or atomic-ordering-sensitive: a '
                             'loom-style exhaustive interleaving check, not a stress loop. A stress test that passes '
                             'ten thousand times has sampled the interleaving space, not covered it.\n'
                             '\n'
                             '## 3. Categories and where each is caught\n'
                             '\n'
                             '| Category | Caught by |\n'
                             '| --- | --- |\n'
                             '| aliasing violation (stacked/tree borrows) | Miri |\n'
                             '| data race | Miri; thread sanitizer under FFI |\n'
                             '| use after free / dangling pointer | Miri; address sanitizer |\n'
                             '| uninitialized memory read | Miri; memory sanitizer |\n'
                             '| invalid value for its type | Miri |\n'
                             '| misaligned pointer access | Miri |\n'
                             '| out-of-bounds access | Miri; address sanitizer |\n'
                             '| provenance violation | Miri, strict-provenance mode |\n'
                             '| double free / invalid free | Miri; address sanitizer |\n'
                             '| incorrect `Send`/`Sync` | Miri, via the race it enables |\n'
                             '| `Pin` invariant violation | partially -- reasoning plus Miri |\n'
                             '| FFI boundary UB | sanitizers; Miri cannot cross the boundary |\n'
                             '| unwinding across `extern "C"` | reasoning plus a targeted panic test |\n'
                             '| unsafe-contract violation in a dependency | reasoning; read the safety comment the '
                             'callee documents |\n'
                             '\n'
                             'The last three rows are why escalation is not "run Miri and move on". Name which '
                             'category the change risks, then name the tool that actually reaches it.\n'
                             '\n'
                             '## 4. What each proves\n'
                             '\n'
                             '| Observation | Proves | Does not prove |\n'
                             '| --- | --- | --- |\n'
                             '| `cargo build` succeeds | the type checker accepted it | nothing about `unsafe` '
                             'invariants |\n'
                             '| `cargo test` passes | the tested paths ran without a detected fault | nothing about '
                             'untested `unsafe` paths |\n'
                             '| Miri passes on a test | that execution path has no Miri-detectable UB | nothing about '
                             'paths that test does not reach |\n'
                             '| A sanitizer passes | that run had no detected fault | nothing about a different '
                             'interleaving or input |\n'
                             '| A loom-style check passes | the modelled interleavings are sound | nothing about '
                             'interleavings outside the model |\n'
                             '\n'
                             'Coverage is the limit on all of them: Miri proves things about the code paths a test '
                             'executes. If the `unsafe` path is untested, escalation is not satisfied by a green Miri '
                             'run -- it is satisfied by a test that reaches the path, then Miri on that test.\n'
                             '\n'
                             '## 5. When the toolchain cannot run it\n'
                             '\n'
                             'If the executor cannot run Miri or the needed sanitizer, the change stays blocked. Name '
                             'the smallest substitute proof -- a narrower test that Miri can run, a safe wrapper that '
                             'shrinks the `unsafe` surface, or a review of the invariant comment by a second reader -- '
                             'and keep the verdict escalated. Downgrading the verdict because the tool is unavailable '
                             'is the failure this reference exists to prevent.\n'
                             '\n'
                             '## Attribution\n'
                             '\n'
                             'Concept lineage only. The idea of a mandatory per-language reference gate that\n'
                             'escalates on `unsafe`/FFI contact, and of a hypothesis-first native debugging\n'
                             'loop, is adapted from the `programming` and `debugging` skills of the\n'
                             "`omo-ai` plugin; the DAP-over-printf preference is adapted from `can1357/oh-my-pi`'s\n"
                             'first-class debug adapter tooling. No upstream text is reproduced -- the\n'
                             'wording, the artifact vocabulary, and the `prepared_not_observed` claim\n'
                             "boundary are OMH's own, and OMH keeps its no-execution boundary: every command\n"
                             'below is something the executor runs, never OMH.\n',
                  'source_path': 'skills/omh-rust/references/ub-escalation.md',
                  'source_sha256': 'b39328707a4c3e1cf1d152603f0840255d68db3cfda714d6c33d853ebb087768'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member rust is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep the ownership '
                       'shape, error-type choice, API surface, gate list, and the UB escalation verdict in Hermes. '
                       'Record compilation, clippy output, test results, Miri runs, sanitizer runs, and loom runs only '
                       'from executor or wrapper observed evidence. No executor/provider/runtime execution, observed '
                       'result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'support-operations',
  'family_id': 'support',
  'description': '[omh] Support ticket your team must answer or escalate: turn a support case into a clear customer '
                 'reply, severity path, and owned next step. Use when the user says: support escalation, customer '
                 'support reply, ticket triage, 고객 지원 에스컬레이션, 고객 답변 초안, 지원 티켓 분류.',
  'triggers': ['support-operations',
               'support escalation',
               'customer support reply',
               'ticket triage',
               '고객 지원 에스컬레이션',
               '고객 답변 초안',
               '지원 티켓 분류'],
  'category': 'triage',
  'phase': 'support-operations',
  'role': 'operator',
  'source_folder': 'omh-support-operations',
  'source_path': 'skills/omh-support-operations/SKILL.md',
  'source_sha256': '66d79e8a68058f862823032d8aa599c2bb12ebba15b1f88adeb5c81b8a3a8719',
  'required_inputs': ['support case', 'known facts', 'customer impact', 'available ownership or escalation path'],
  'expected_outputs': ['customer-safe reply draft with stated facts, unknowns, and tone',
                       'issue/severity/impact/escalation matrix',
                       'internal next-step and owner handoff brief',
                       'missing repro, account, entitlement, or approval evidence list'],
  'artifact_expectations': ['prepared support case brief when a wrapper captures it',
                            'Artifact contracts:',
                            'This label denotes the machine-enforcement level, not a skill quality score and not an '
                            'observed evidence state.',
                            'contract_id: `support-operations`; enforcement_level: `guidance_only`; consumer_id: '
                            '`none`'],
  'acceptance_criteria': ['The source boundary, signal clusters, severity, and follow-up lane are named.',
                          'Bug, feature, research, strategy, and coding handoff outcomes stay separate.',
                          'The next workflow is recommended before any implementation claim.'],
  'handoff_policy': 'Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work '
                    'routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, '
                    'filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a '
                    'connector, file, coding, or human-review handoff only when the user explicitly accepts that next '
                    'step; report it only from observed evidence. Reply text is a draft, escalation is a '
                    'recommendation, and no ticket state, message send, refund, account action, or customer outcome is '
                    'claimed.',
  'catalog_rules': ['Source routing exclusion: The request clusters a backlog of customer signals to find product '
                    'patterns or roadmap candidates; use `feedback-triage`.',
                    'Source routing exclusion: The user only needs a generic, non-support marketing or email rewrite '
                    'with no case, severity, or escalation context; use `content-operator`.',
                    'Source routing exclusion: The request asks to send a reply, change ticket priority or status, '
                    'issue a refund, modify an account, or update a helpdesk; use `connector-operator` with an '
                    'explicit target and observed result.',
                    'Source routing exclusion: The request is an incident that is still open, needing severity '
                    'declared, a commander assigned, and a running timeline rather than a support-case response; use '
                    '`live-incident-response`.',
                    "Source routing exclusion: The request is a closed incident's postmortem or reliability evidence "
                    'rather than a support-case response; use `reliability-review`.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'feedback-triage as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['feedback-triage'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member support-operations is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep domain '
                       'framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in '
                       'Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, '
                       'send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, '
                       'file, coding, or human-review handoff only when the user explicitly accepts that next step; '
                       'report it only from observed evidence. Reply text is a draft, escalation is a recommendation, '
                       'and no ticket state, message send, refund, account action, or customer outcome is claimed. No '
                       'executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is '
                       'implied.'},
 {'canonical_id': 'command-operator',
  'family_id': 'primitive-operators',
  'description': '[omh] Shell command or test-suite execution: policy overlay for terminal commands - add cwd, '
                 'environment, safety, and result-evidence gates after preferring native shell tools for ordinary CLI, '
                 'package-manager, and test runs. Use when the user says: command-operator, command operator, terminal '
                 'command, terminal task, shell command, shell task, cli command, command execution.',
  'triggers': ['command-operator',
               'command operator',
               'terminal command',
               'terminal task',
               'shell command',
               'shell task',
               'cli command',
               'command execution'],
  'category': 'command',
  'phase': 'command-task',
  'role': 'guide',
  'source_folder': 'omh-terminal',
  'source_path': 'skills/omh-terminal/SKILL.md',
  'source_sha256': '242f733a773d99f885623728fde1fca4594fe2d039fe4f070d18a0a6d10ff58c',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['command_task_card/v1',
                       'command_scope/v1',
                       'command_safety_gate/v1',
                       'command_result_manifest/v1 when observed',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['command_task_card/v1 metadata-only wrapper card when prepared',
                            'command_scope/v1 with command text, working directory, environment assumptions, timeout, '
                            'and stop condition',
                            'command_safety_gate/v1 separating read-only, write/mutation, network, credential, and '
                            'destructive-risk commands',
                            'command_result_manifest/v1 only when exit code, stdout/stderr, logs, or terminal '
                            'transcript are observed'],
  'acceptance_criteria': ['Command text, working directory, environment assumptions, timeout, safety level, and stop '
                          'condition are explicit.',
                          'Destructive, credential, network, filesystem mutation, install, deploy, and production '
                          'commands are gated or marked missing.',
                          'Exit codes, stdout/stderr, test results, package-manager effects, and filesystem mutations '
                          'are reported only from observed command evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'toolbelt-readiness, deliverable-package as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness', 'deliverable-package'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member command-operator is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as '
                       'Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                       'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                       'recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or '
                       'merge evidence is implied.'},
 {'canonical_id': 'context',
  'family_id': 'domain-context',
  'description': '[omh] Repository vocabulary unclear or inconsistent: project terminology alignment workflow: look '
                 'up, capture, correct, and align the words a repository uses before planning or handoff. Use when the '
                 'user says: ulw-context, project terminology alignment, review project terms, align project '
                 'terminology, terminology this project uses.',
  'triggers': ['context',
               'ulw-context',
               'project terminology alignment',
               'review project terms',
               'align project terminology',
               'terminology this project uses'],
  'category': 'clarification',
  'phase': 'terminology-alignment',
  'role': 'planner',
  'source_folder': 'ulw-context',
  'source_path': 'skills/ulw-context/SKILL.md',
  'source_sha256': '372aa8e9d50db2e0f7e60988e1b9ee0bfd13a0a4e64dbd24d8e0d40067b3d80b',
  'required_inputs': ['the terminology question or alignment goal',
                      'repository evidence and optional root PROJECT_TERMS.md source status',
                      'active reviewed project terminology profile when one exists',
                      'unresolved decisions and their dependency relationships when an interview is needed'],
  'expected_outputs': ['direct source-labeled terminology answer or proposed terminology alignment',
                       'dependency-ready frontier with concise recommendations when decisions remain',
                       'explicit pending-candidate staging choice when machine mappings should be reviewed',
                       'confirmed shared-understanding summary and separately prepared planning or coding-owner '
                       'handoff'],
  'artifact_expectations': ['optional human-reviewed PROJECT_TERMS.md patch proposal that OMH does not write '
                            'automatically',
                            'pending domain-intelligence candidates only after explicit staging confirmation',
                            'prepared `ulw-plan` or selected coding-owner handoff only after separate confirmation'],
  'acceptance_criteria': ['Source status and reviewed-profile status are named without treating either as model-use '
                          'evidence.',
                          'Safe lookups were answered directly and unresolved decisions were asked only when the user '
                          'confirmed interview entry.',
                          'Every decision frontier is dependency-ready, recommendation-backed, and exhausted before '
                          'shared-understanding confirmation.',
                          'Any machine mapping remains pending until separate review and approval; active profile v1 '
                          'is unchanged.',
                          'Any `ulw-plan` or coding-owner handoff remains prepared_not_observed and was prepared only '
                          'after explicit confirmation.'],
  'handoff_policy': 'Keep terminology lookup, source inspection, and decision-frontier facilitation in Hermes. Stage '
                    'project candidates only after explicit confirmation, activate them only through the existing '
                    'separate review lifecycle, and prepare `ulw-plan` or a selected executor-neutral coding handoff '
                    'only after the user confirms shared understanding and the next path.',
  'catalog_rules': ['Source routing exclusion: A safe one-term definition or source lookup can be answered directly; '
                    'use the read-only lookup mode and do not enter the full context interview.',
                    'Source routing exclusion: The request is broad ambiguity with no project-language conflict; use '
                    '`deep-interview`.',
                    'Source routing exclusion: The unresolved decision is empirical and a cheap isolated experiment '
                    'can answer it; use `decision-prototype` and keep the frontier for the rest.',
                    'Source routing exclusion: The terminology is already agreed and the request is to produce an '
                    'implementation plan; use `ralplan`.',
                    'Source routing exclusion: The user wants to capture or curate general retained memory rather than '
                    'repository terminology; use `memory-new` or `memory-sync`.',
                    'Source routing exclusion: The user asks for workflow discovery, help, status, file lookup, direct '
                    'answer, or dispatch; preserve `oh-my-hermes` and ordinary protected-route behavior.',
                    'Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'deep-interview as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['deep-interview'],
  'references': [{'relative_path': 'ulw-context/references/decision-frontier.md',
                  'content': '# Dependency-Ready Decision Frontier\n'
                             '\n'
                             'Load this reference only when terminology correction exposes unresolved product or '
                             'workflow decisions. A safe lookup does not enter this interview.\n'
                             '\n'
                             '## Entry\n'
                             '\n'
                             'Ask for explicit confirmation before starting. First inspect repository and source '
                             'evidence for facts Hermes can discover. The user owns product decisions; do not ask them '
                             'to retrieve facts available locally.\n'
                             '\n'
                             '## Dependency Model\n'
                             '\n'
                             'Represent each unresolved decision with its prerequisites and dependents. Assign '
                             'append-only `D1`, `D2`, ... identifiers and never renumber or reuse them. A decision is '
                             '`open`, `resolved`, `deferred`, `blocked`; reachability is separate from state.\n'
                             '\n'
                             'In each round, present the whole dependency-ready frontier: every reachable open '
                             'decision whose prerequisites are resolved. One emitted batch consumes one round '
                             'regardless of item count. Do not ask a dependent question in the same round as its '
                             'prerequisite.\n'
                             '\n'
                             'Open each batch with `Frontier round {n}/6 · Resolved {r} · Deferred {d} · Blocked {b} · '
                             'Open {o}`. Find the latest header in the thread before incrementing it. Repository '
                             'research, entry consent, the pre-Round-4 consent check, summary confirmation, and '
                             'next-path consent consume no rounds.\n'
                             '\n'
                             'For each frontier item:\n'
                             '\n'
                             '1. state the decision and why it changes shared understanding;\n'
                             '2. summarize observed evidence and unknowns;\n'
                             '3. give one concise recommendation with the main tradeoff;\n'
                             "4. ask for the user's decision, correction, or skip.\n"
                             '\n'
                             'Apply unambiguous answers only to the identifiers they address. Omitted decisions remain '
                             'open. A recommendation becomes selected terminology only when the user explicitly '
                             'accepts it. Apply addressed answers before evaluating a global stop request; newly '
                             'unlocked dependents wait for the next round.\n'
                             '\n'
                             'Record agreed canonical identity and short definition separately from design rationale. '
                             'Keep rare, hard-to-reverse tradeoffs as decision notes rather than glossary entries.\n'
                             '\n'
                             '## Stop and Transition\n'
                             '\n'
                             'After each answer, stop on the first matching condition:\n'
                             '\n'
                             '1. every reachable decision is resolved, explicitly deferred, or blocked by named '
                             'missing evidence;\n'
                             '2. the user asks to stop questioning or proceed;\n'
                             '3. the answer to Round 6 was recorded.\n'
                             '\n'
                             'On user stop or budget exhaustion, keep unaddressed decisions open and show '
                             'recommendations only as proposed assumptions. Never emit Round 7. Read back resolved, '
                             'deferred, blocked, and open decisions separately and ask the user to confirm that '
                             'summary. Confirmation closes the interview; it does not approve implementation.\n'
                             '\n'
                             'If no valid round header or decision identity survives context compaction, do not '
                             'restart or emit another decision round. Summarize only recoverable decisions and close '
                             'unresolved items with a named `compaction_state_unavailable` blocker.\n'
                             '\n'
                             'After confirmation, offer either `ulw-plan` for a reviewed implementation plan or a '
                             'selected executor-neutral coding-owner handoff when work is already plan-ready. Ask for '
                             'a separate go-ahead before preparing either. A prepared handoff is not dispatch, '
                             'execution, review, CI, merge-readiness, merge, or proof that the recipient used the '
                             'terminology.\n'
                             '\n'
                             '## Attribution\n'
                             '\n'
                             'The dependency tree, frontier rounds, recommendation pattern, fact/decision split, and '
                             "shared-understanding stop condition adapt ideas from Matt Pocock's `grilling` skill at "
                             '`mattpocock/skills@84fdeffd12f2ee307994d1eb6feb48173b6e0502`, MIT License, Copyright '
                             '2026 Matt Pocock. OMH keeps planning and executor handoff as separate confirmed '
                             'phases.\n',
                  'source_path': 'skills/ulw-context/references/decision-frontier.md',
                  'source_sha256': '122978a41c0a003f8b7a879b00c9ecc2417e75d5fbb787f24ecb3477403a67df'},
                 {'relative_path': 'ulw-context/references/project-terms.md',
                  'content': '# Project Terms Source and Review Boundary\n'
                             '\n'
                             'Load this reference for terminology lookup, source inspection, preview, staging, '
                             'freshness, or profile authority questions.\n'
                             '\n'
                             '## Authority\n'
                             '\n'
                             '- `PROJECT_TERMS.md` is an optional repository-root, human-reviewed source. Absence is a '
                             'clean no-op.\n'
                             '- `<!-- omh-project-terms/v1 -->` identifies the strict source grammar.\n'
                             '- Source edits have zero direct machine or routing authority. The active reviewed '
                             '`domain_intelligence_profile/v1` lifecycle remains the only machine-readable terminology '
                             'source.\n'
                             '- Definitions, localized labels, distinct-from notes, and say-instead guidance remain '
                             'human prose. They are never trigger, anti-trigger, reranking, dispatch, or matching '
                             'inputs.\n'
                             '\n'
                             '## Lookup\n'
                             '\n'
                             'Read only what the question needs. Report whether the answer came from repository '
                             'evidence, the optional source, an active reviewed profile, or an unresolved conflict. '
                             'Report exact-byte freshness only when explicitly inspected. `changed` or `missing` '
                             'requests review; neither mutates active behavior.\n'
                             '\n'
                             '## Capture\n'
                             '\n'
                             'Normal users describe the intent in Hermes chat. Agent/operator control-plane work may '
                             'preview repository-root `PROJECT_TERMS.md`; preview is `prepared_not_observed`, reports '
                             'no predicted candidate ids, and writes nothing. Before staging, show the machine-only '
                             'projection and ask for explicit confirmation. Staging is atomic and pending-only. '
                             'Approval is a separate review action.\n'
                             '\n'
                             'Never create, rewrite, synchronize, approve, retire, or commit the source automatically. '
                             'Never infer execution, review, model use, CI, or merge from source bytes, candidate '
                             'state, profile state, or freshness.\n'
                             '\n'
                             '## Attribution\n'
                             '\n'
                             "The separation of domain language from decision work adapts ideas from Matt Pocock's "
                             '`domain-modeling` skill at `mattpocock/skills@84fdeffd12f2ee307994d1eb6feb48173b6e0502`, '
                             'MIT License, Copyright 2026 Matt Pocock. OMH uses its own strict source and '
                             'reviewed-memory contracts.\n',
                  'source_path': 'skills/ulw-context/references/project-terms.md',
                  'source_sha256': '0b6baee554fc8fa813d9b4b86aab55a9858441d2c3b2d90ef0d037a8f12afd45'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member context is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep terminology '
                       'lookup, source inspection, and decision-frontier facilitation in Hermes. Stage project '
                       'candidates only after explicit confirmation, activate them only through the existing separate '
                       'review lifecycle, and prepare `ulw-plan` or a selected executor-neutral coding handoff only '
                       'after the user confirms shared understanding and the next path. No executor/provider/runtime '
                       'execution, observed result, review, CI, deploy, or merge evidence is implied.'})
