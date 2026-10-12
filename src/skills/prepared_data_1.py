"""Static prepared guidance records for partition one of the audited catalog.

The records are source-pinned metadata only; they never execute commands or providers.
"""
PREPARED_MEMBERS = ({'canonical_id': 'accessibility-audit',
  'family_id': 'accessibility',
  'description': '[omh] Screen-reader or keyboard accessibility gaps: prepare WCAG, keyboard, focus, screen-reader, '
                 'target-size, and reflow evidence gates for UI surfaces. Use when the user says: accessibility-audit, '
                 'accessibility audit, a11y audit, a11y architect, wcag audit, wcag 2.2, wcag 2.2 aa, accessibility '
                 'pass.',
  'triggers': ['accessibility-audit',
               'accessibility audit',
               'a11y audit',
               'a11y architect',
               'wcag audit',
               'wcag 2.2',
               'wcag 2.2 aa',
               'accessibility pass'],
  'category': 'accessibility',
  'phase': 'accessibility-audit',
  'role': 'reviewer',
  'source_folder': 'omh-accessibility-audit',
  'source_path': 'skills/omh-accessibility-audit/SKILL.md',
  'source_sha256': '90c554f1ed3cd2522c4c678f39de9a4aac8080c41c9ba9ffb0a3e1d712b3dca3',
  'required_inputs': ['target app, page, route, component, or design system',
                      'platform: web, iOS, Android, desktop, TUI, or unknown',
                      'available UI evidence: code, screenshots, DOM snapshots, accessibility tree, browser captures, '
                      'or design specs',
                      'interaction paths and critical tasks',
                      'required standard or policy such as WCAG 2.2 AA',
                      'known risk areas: keyboard traps, missing labels, low contrast, small targets, reflow, live '
                      'regions, or CJK/localization',
                      'observed accessibility evidence for PASS claims'],
  'expected_outputs': ['accessibility_audit_plan/v1',
                       'wcag_success_criteria_matrix/v1',
                       'semantic_structure_review/v1',
                       'focus_and_keyboard_trace/v1 when observed',
                       'screen_reader_announcement_map/v1 when observed',
                       'target_size_and_pointer_review/v1',
                       'contrast_and_reflow_review/v1',
                       'accessibility_remediation_handoff/v1 when needed',
                       'accessibility_audit_verdict/v1'],
  'artifact_expectations': ['accessibility_audit_plan/v1 with platform, surfaces, critical tasks, standard level, '
                            'supplied evidence, and missing observations',
                            'wcag_success_criteria_matrix/v1 covering perceivable, operable, understandable, robust '
                            'requirements with PASS/HOLD/BLOCK per criterion',
                            'semantic_structure_review/v1 with labels, roles, names, headings, landmarks, form errors, '
                            'live regions, and state semantics',
                            'focus_and_keyboard_trace/v1 only from observed keyboard navigation, tab order, focus '
                            'appearance, skip/focus-trap checks, and critical interaction paths',
                            'screen_reader_announcement_map/v1 only when announcements, accessible names, roles, '
                            'values, hints, and dynamic updates are observed or supplied',
                            'target_size_and_pointer_review/v1 with 24x24 CSS px / 44x44 mobile target expectations '
                            'and pointer gesture alternatives',
                            'contrast_and_reflow_review/v1 with measured contrast, zoom/reflow risk, clipping, '
                            'overflow, and CJK/localized text concerns',
                            'accessibility_audit_verdict/v1 returns PASS, HOLD, or BLOCK with missing evidence and '
                            'remediation route'],
  'acceptance_criteria': ['The platform, target surfaces, critical tasks, WCAG level, supplied evidence, and missing '
                          'observations are explicit.',
                          'The wcag_success_criteria_matrix/v1 separates PASS/HOLD/BLOCK and maps each issue to user '
                          'impact.',
                          'Semantic structure, focus/keyboard, screen-reader announcements, target size/pointer, '
                          'contrast/reflow, and form/status behavior are separate checks.',
                          'PASS is unavailable unless evidence is fresh after the latest UI edit and covers critical '
                          'tasks.',
                          'Remediation, frontend implementation, visual QA, browser proof, CI, release, and merge '
                          'remain separate observed states.'],
  'handoff_policy': 'Keep accessibility scope, WCAG mapping, focus-flow expectations, screen-reader semantics, and '
                    'remediation routing in Hermes. Automated scans, browser keyboard walks, screen-reader '
                    'observations, contrast measurements, and code fixes require observed wrapper, executor, or user '
                    'evidence.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The user needs initial frontend design or redesign planning before '
                    'accessibility-specific review; use `frontend` first.',
                    'Source routing exclusion: The user needs rendered layout, screenshot, CJK, or pixel-diff QA '
                    'rather than accessibility semantics; use `visual-qa`.',
                    'Source routing exclusion: The user needs a broad premium-quality gate across web, deck, PDF, or '
                    'posters; use `design-quality-gate`.',
                    'Source routing exclusion: The user asks to implement accessibility fixes directly; prepare a '
                    'selected executor/runtime handoff after the audit or use the coding workflow.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['code-review', 'ultraqa'],
  'references': [{'relative_path': 'omh-accessibility-audit/references/a11y-rules.md',
                  'content': '# Accessibility Rule IDs and the Fix Partition\n'
                             '\n'
                             'The finding vocabulary for an accessibility audit. Prose findings are not\n'
                             'comparable across reruns and cannot be handed to an executor in parts; a rule\n'
                             'ID, a severity, a WCAG criterion, and a fix class can.\n'
                             '\n'
                             '## How a finding is written\n'
                             '\n'
                             'Read the target surface completely, collect every finding, then report. One\n'
                             'row per finding:\n'
                             '\n'
                             '`rule ID | severity | location | WCAG criterion | fix class | the fix`\n'
                             '\n'
                             'Severity is `critical` (the surface is unusable for someone), `major` (a task\n'
                             'is degraded or a control is mislabelled to assistive technology), or `minor`\n'
                             '(comprehension or convention). Severity ranks findings; it is not the audit\n'
                             'verdict, which stays PASS/HOLD/BLOCK on observed evidence.\n'
                             '\n'
                             '## The fix partition, which is the load-bearing half\n'
                             '\n'
                             'A fix is `auto` **only when the correct output is derivable from the markup\n'
                             'itself**. It is `manual` whenever producing it requires knowing what the\n'
                             'content *means*.\n'
                             '\n'
                             '- Derivable: an image inside a control that already carries a text label is\n'
                             '  decorative, so its text alternative is the empty one. The structure decided\n'
                             '  it, not a reader.\n'
                             '- Not derivable: what a meaningful image actually depicts, what a link\n'
                             '  actually goes to, what a field actually asks for. No amount of markup\n'
                             '  yields those.\n'
                             '\n'
                             'Marking a meaning-dependent fix `auto` is a defect in the audit, not a\n'
                             'convenience for the fixer: it produces confident, wrong alternative text,\n'
                             'which reads worse to assistive technology than the missing attribute did.\n'
                             "When a rule's fix is partly structural and partly semantic, the row is split\n"
                             'into its `auto` half and its `manual` half rather than rounded to either.\n'
                             '\n'
                             '## Rules\n'
                             '\n'
                             '### Images\n'
                             '\n'
                             '| ID | Finding | Severity | WCAG | Fix class |\n'
                             '| --- | --- | --- | --- | --- |\n'
                             '| IMG-1 | Image with no text alternative | critical | 1.1.1 | `auto` when decorative by '
                             'context, else `manual` |\n'
                             '| IMG-2 | Decorative image not marked decorative to assistive technology | minor | 1.1.1 '
                             '| `auto` |\n'
                             '\n'
                             '### Links and buttons\n'
                             '\n'
                             '| ID | Finding | Severity | WCAG | Fix class |\n'
                             '| --- | --- | --- | --- | --- |\n'
                             '| LNK-1 | Link with no accessible name | critical | 2.4.4, 4.1.2 | `manual` |\n'
                             '| LNK-2 | Link text that does not describe its destination | minor | 2.4.4 | `manual` |\n'
                             '| LNK-3 | Link opening a new context with no warning | minor | 3.2.5 | `manual` |\n'
                             '| BTN-1 | Button with no accessible name | critical | 4.1.2 | `manual` |\n'
                             '\n'
                             '### Forms\n'
                             '\n'
                             '| ID | Finding | Severity | WCAG | Fix class |\n'
                             '| --- | --- | --- | --- | --- |\n'
                             '| FORM-1 | Control with no programmatically associated label | critical | 1.3.1, 3.3.2, '
                             '4.1.2 | `manual` |\n'
                             '| FORM-2 | Label associated with a control that does not exist | major | 1.3.1 | '
                             '`manual` |\n'
                             '| FORM-3 | Personal-data field with no autofill purpose declared | minor | 1.3.5 | '
                             '`manual` |\n'
                             '\n'
                             '### Roles and states\n'
                             '\n'
                             '| ID | Finding | Severity | WCAG | Fix class |\n'
                             '| --- | --- | --- | --- | --- |\n'
                             '| ARIA-1 | Role that is not a valid role name | major | 4.1.2 | `manual` |\n'
                             '| ARIA-2 | Focusable element hidden from assistive technology | critical | 2.4.3, 4.1.2 '
                             '| `auto` (unhide; the element is reachable by keyboard and must be announced) |\n'
                             '| ARIA-3 | Decorative vector graphic exposed to assistive technology | major | 1.1.1 | '
                             '`auto` when decorative by context, else `manual` |\n'
                             '\n'
                             '### Keyboard and focus\n'
                             '\n'
                             '| ID | Finding | Severity | WCAG | Fix class |\n'
                             '| --- | --- | --- | --- | --- |\n'
                             '| KEY-1 | Positive tab index overriding document order | major | 2.4.3 | `auto` '
                             '(neutralize), and the resulting order is re-walked |\n'
                             '| KEY-2 | Pointer handler on a non-interactive element with no keyboard path | major | '
                             '2.1.1 | split: role and focusability `auto`, the key handler `manual` |\n'
                             '\n'
                             '### Structure\n'
                             '\n'
                             '| ID | Finding | Severity | WCAG | Fix class |\n'
                             '| --- | --- | --- | --- | --- |\n'
                             '| SEM-1 | Page language not declared | critical | 3.1.1 | `auto` (the tag), with the '
                             'language value verified |\n'
                             '| SEM-2 | Heading level skipped | major | 1.3.1 | `manual` |\n'
                             '| SEM-3 | No main landmark | major | 1.3.1, 2.4.1 | `manual` |\n'
                             '| SEM-4 | Embedded frame with no title | major | 2.4.1, 4.1.2 | `manual` |\n'
                             '| SEM-5 | Layout table exposed as a data table | minor | 1.3.1 | `auto` |\n'
                             '\n'
                             '### Color and contrast\n'
                             '\n'
                             '| ID | Finding | Severity | WCAG | Fix class |\n'
                             '| --- | --- | --- | --- | --- |\n'
                             '| COL-1 | Color as the only carrier of meaning | minor | 1.4.1 | `manual` |\n'
                             '| COL-2 | Color declared inline, contrast unverifiable from source | minor | 1.4.3 | '
                             '`manual` (measure, then judge against 4.5:1 text / 3:1 large text and UI) |\n'
                             '\n'
                             "Detection criteria are written against structure, not one framework's syntax:\n"
                             'a rule holds for a template language when the same structural condition can be\n'
                             'seen in it, and a syntax that hides the condition (a fully dynamic binding, a\n'
                             'name computed at runtime) is reported as unverifiable-from-source rather than\n'
                             'as a pass.\n'
                             '\n'
                             '## Rerun and handoff\n'
                             '\n'
                             'Rule IDs are what make a second audit comparable to the first: a finding is\n'
                             'resolved when its ID no longer matches at that location, carried when it\n'
                             'still does, and new otherwise. The `auto` rows are the only ones that can be\n'
                             'handed to an executor as a batch; the `manual` rows go back with the question\n'
                             'each one needs answered.\n'
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'A rule ID classifies a finding and a fix class describes a fix - neither is\n'
                             'evidence the fix was applied. The audit verdict still requires observed\n'
                             'keyboard and assistive-technology evidence after the change, and a scan that\n'
                             'produced these findings is not a keyboard walk.\n',
                  'source_path': 'skills/omh-accessibility-audit/references/a11y-rules.md',
                  'source_sha256': 'cd7e0404576923cfd3bcec9e055b1de7a78f3fc55971fd033598aac1043e4469'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member accessibility-audit is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'app-debugging',
  'family_id': 'application-and-native-debug',
  'description': '[omh] Application code misbehaves -- a wrong value, a flaky test, a lost update: reproduce it first, '
                 'form competing hypotheses, discriminate them with the cheapest observation, and only then fix the '
                 'demonstrated root cause. Use when the user says: app-debugging, app debugging, application '
                 'debugging, root cause, root-cause, find the root cause, root cause analysis, flaky test.',
  'triggers': ['app-debugging',
               'app debugging',
               'application debugging',
               'root cause',
               'root-cause',
               'find the root cause',
               'root cause analysis',
               'flaky test'],
  'category': 'verification',
  'phase': 'app-root-cause',
  'role': 'reviewer',
  'source_folder': 'omh-app-debugging',
  'source_path': 'skills/omh-app-debugging/SKILL.md',
  'source_sha256': 'e60fe09f8b5bceff2ff7bf6344a85d6a289d9bb683b1f301294f587521099a47',
  'required_inputs': ['the wrong behaviour as observed, and the behaviour that was expected',
                      'the command, request, or test that shows it, and how often it shows it',
                      'language, framework, and what changed recently when known',
                      'logs, stack traces, or failing assertions already captured',
                      'observed reproduction and verification evidence for any root-cause or fix claim'],
  'expected_outputs': ['reproduction_record/v1',
                       'competing_hypotheses/v1 with at least three hypotheses on distinct axes',
                       'discriminating_observation_plan/v1',
                       'root_cause_record/v1',
                       'fix_handoff/v1 blocked until reproduction_record/v1 reads observed',
                       'observed_fix_verification/v1 when observed'],
  'artifact_expectations': ['reproduction_record/v1 names the exact command, the input, the observed output, the '
                            'expected output, and the hit rate over N runs; it reads observed or not_observed and '
                            'nothing between',
                            'competing_hypotheses/v1 spans distinct axes -- input and state, ordering and timing, '
                            'environment and build, dependency behaviour -- rather than three phrasings of one guess',
                            'discriminating_observation_plan/v1 orders the observations cheapest first and names, for '
                            'each, which hypotheses its result eliminates',
                            'root_cause_record/v1 cites the observation that demonstrated the cause and the one that '
                            'ruled out each rival',
                            'fix_handoff/v1 carries the reproduction as the regression test that must fail before the '
                            'fix and pass after it'],
  'acceptance_criteria': ['The reproduction names its command, observed output, expected output, and hit rate, and '
                          'reads observed before any fix is prepared.',
                          'At least three hypotheses on distinct axes were written before the first observation was '
                          'chosen.',
                          'Each observation records which hypotheses its result eliminated.',
                          'The root cause cites the demonstrating observation and the observation that ruled out each '
                          'rival.',
                          'The fix handoff carries the reproduction as a regression test that fails before and passes '
                          'after.'],
  'handoff_policy': 'Keep the symptom statement, the hypothesis set, the discriminating observations, and the '
                    'root-cause verdict in Hermes. Record every reproduction run, probe output, and fix verification '
                    'only from executor or wrapper observed evidence.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The fault is a crash, memory corruption, or core dump in a compiled '
                    'native binary that needs a debugger session; use `native-debugging`.',
                    'Source routing exclusion: The build, compile, or CI job fails the same way on every run; use '
                    '`build-failure-triage`.',
                    'Source routing exclusion: The subject is an agent or workflow run that misbehaved rather than the '
                    'application code; use `agent-debug`.',
                    'Source routing exclusion: The cause is already demonstrated and the request is to judge whether '
                    'the fix is proven; use `verification-gate`.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ultraqa', 'code-review'],
  'references': [{'relative_path': 'omh-app-debugging/references/hypothesis-and-race-method.md',
                  'content': '# Hypothesis, Flaky-Test, and Race Method\n'
                             '\n'
                             'Load this while taking an application fault to a demonstrated root cause. OMH executes '
                             'nothing: every run, probe, and read below is something the executor performs and reports '
                             'back, and the record takes only what was observed.\n'
                             '\n'
                             'The order never changes: an observed reproduction, then competing hypotheses, then the '
                             'cheapest observation that separates them, then the fix. A fix proposed before the '
                             'reproduction reads observed is a guess with a diff attached.\n'
                             '\n'
                             '## 1. The reproduction record\n'
                             '\n'
                             '| Field | What it holds |\n'
                             '| --- | --- |\n'
                             '| Command | the exact command, request, or test id, with its inputs |\n'
                             '| Observed | the output, value, or assertion as it came back |\n'
                             '| Expected | the output that would have been correct, and where that expectation comes '
                             'from |\n'
                             '| Hit rate | failures over runs, for example `4/20`; one sighting is a report, not a '
                             'reproduction |\n'
                             '| Environment | interpreter, dependency versions, OS, parallelism, and anything the '
                             'failing run had that the passing run did not |\n'
                             '| State | observed or not_observed; nothing between |\n'
                             '\n'
                             'An intermittent fault is reproduced when its rate is measured, not when it happened '
                             'once. Run it in a loop first (`for i in $(seq 50); do <cmd> || echo FAIL $i; done`) and '
                             'record the rate before changing anything; the same loop is what proves the fix later.\n'
                             '\n'
                             '## 2. Hypotheses on distinct axes\n'
                             '\n'
                             'Write at least three before choosing an observation. Three phrasings of one guess is one '
                             'hypothesis.\n'
                             '\n'
                             '| Axis | Example framing | Cheapest discriminating observation |\n'
                             '| --- | --- | --- |\n'
                             '| Input and state | a value, fixture, or cached row differs from the one assumed | print '
                             'or assert the actual input at the boundary |\n'
                             '| Ordering | the result depends on test order, iteration order, or arrival order | run '
                             'the one test alone, then in reverse or shuffled order |\n'
                             '| Timing | a deadline, sleep, or clock read races the work | shorten or lengthen the '
                             'delay and watch the rate move |\n'
                             '| Shared state | two runs, threads, or workers share a file, row, port, or global | '
                             'isolate the resource per run and watch the rate drop to zero |\n'
                             '| Environment and build | the running code is not the source being read | print the '
                             'imported module path and version from inside the failing run |\n'
                             '| Dependency behaviour | a library, service, or OS call behaves differently than '
                             'documented | pin or stub it and compare |\n'
                             '\n'
                             'For each hypothesis write the claim, the observation that would refute it, and which '
                             'other hypotheses the same observation also settles. Choose the next observation by cost '
                             'first, then by how many hypotheses its result eliminates; record the eliminations as '
                             'they happen.\n'
                             '\n'
                             '## 3. Flaky tests\n'
                             '\n'
                             'A test that fails some runs is a fault with a schedule. Treat the rate as the signal.\n'
                             '\n'
                             '- **Order dependence.** Run the test alone. Passing alone and failing in the suite means '
                             'another test leaks state into it -- a global, an environment variable, a module-level '
                             'cache, a patched attribute left unpatched.\n'
                             '- **Teardown races.** A test that reads a file or port its own fixture is still tearing '
                             'down fails only when teardown is slow. A background thread or worker that outlives the '
                             'test is the usual cause.\n'
                             '- **Clock and deadline.** A fixed date that goes stale, a timeout sized for an idle '
                             'machine, or a wall-clock assertion under load. Run the test with the machine loaded and '
                             'see whether the rate moves.\n'
                             '- **Parallel workers.** Two workers sharing one temp path, database, or port. Give each '
                             'worker its own and watch the rate.\n'
                             '- **Retries and sleeps are masks.** A sleep or a retry that makes the test pass removes '
                             'the reproduction and leaves the fault. Record it as a mask, never as the fix.\n'
                             '\n'
                             '## 4. Races and lost updates\n'
                             '\n'
                             '| Pattern | Symptom | Discriminating observation |\n'
                             '| --- | --- | --- |\n'
                             "| Read-modify-write without a lock | two writers, one update missing | log both writers' "
                             'read values; equal reads before two writes is the race |\n'
                             '| Check-then-act | a condition true at check, false at act | widen the gap with a delay '
                             'and watch the rate rise |\n'
                             '| Publication before initialisation | a reader sees a half-built object | assert the '
                             'invariant at the read site |\n'
                             '| Lost wakeup | a waiter never wakes after the signal | log signal and wait timestamps; '
                             'a signal before the wait is the loss |\n'
                             '| Stale cache after write | a read after a write returns the old value | read around the '
                             'cache and compare |\n'
                             '\n'
                             'A bug that disappears when a print statement or a debugger is added is a timing fault by '
                             'default: the observation changed the schedule. Prefer an observation that does not move '
                             'timing -- a counter, a post-mortem assert, a recorded trace -- over another print.\n'
                             '\n'
                             '## 5. When the running code is not the code being read\n'
                             '\n'
                             'Before trusting any reading, confirm the process executed the source you are looking '
                             'at.\n'
                             '\n'
                             '- A stale editable install or build directory serves an older copy of a module; a newly '
                             'added file is then missing and the failure reads as a regression in whoever added it.\n'
                             '- A cached bytecode file is validated by timestamp and size, so two edits of equal '
                             'length in the same second can reuse the old compile.\n'
                             '- A test that reads its own teardown output, or a lock that times out inside a '
                             'best-effort swallow, leaves the same trace as the fault being hunted; put the '
                             'discriminator in the assertion message.\n'
                             '\n'
                             '## 6. After three failed fixes\n'
                             '\n'
                             'Count fix attempts from executed results, never from the conversation. After each fix, '
                             'the executor runs the same reproduction command from section 1; for an intermittent '
                             'fault, the same loop at the same run count. A run that was planned but not executed, or '
                             'a run of some other command, does not count, so only executed runs of the one '
                             'reproduction move the count. On that run the fix failed when the original symptom is '
                             'still there. When the original symptom is gone and a new symptom shows up, one more '
                             'observation decides. The new symptom may have been there all along, hidden behind the '
                             'first: add that as a hypothesis in section 2 and test it cheaply on the tree before the '
                             'fix, for example by running only the later check or stubbing the step that failed first. '
                             'If the pre-fix tree already shows it, the fix holds, its hypothesis is not eliminated, '
                             'and the new symptom is a separate fault with its own count. If it does not, the fix '
                             'moved the fault, and a fault that moved is a failed fix, not progress.\n'
                             '\n'
                             'After the first or second failed fix, the root cause is open again. Record the fix as '
                             'the observation that eliminated its hypothesis, then return to section 2 and choose the '
                             'next observation from the hypotheses still standing.\n'
                             '\n'
                             'After the third failed fix, stop fixing. Every fix was tested against a structure all of '
                             'them assumed, and three failures on the same reproduction make that structure the '
                             'suspect.\n'
                             '\n'
                             '- **Prepare no fourth fix.** Another diff on the same assumption is the same guess '
                             'again.\n'
                             '- **Name the shared assumptions.** What owns the state, which boundary the data crosses, '
                             'what ordering the design relies on, whether the component is used the way it was built '
                             'to be. Write each with the observation that would refute it, as in section 2.\n'
                             '- **Look for the structural pattern.** Each fix surfaces coupling or shared state at a '
                             'new site, a fault that was fixed comes back as a different one, or the next fix would '
                             'need a wide restructuring to land.\n'
                             '- **Hand the choice back.** Present the re-examination and end the turn with the next '
                             'step as a question the user owns: fix inside the current design under a named new '
                             'hypothesis, or change the design at the assumption that failed.\n'
                             '\n'
                             '| Thought | Why it does not hold |\n'
                             '| --- | --- |\n'
                             '| One more fix will do it | After three failed fixes on the same reproduction, the '
                             'untested part is the assumption they shared, not the next diff. |\n'
                             '\n'
                             '## 7. Evidence boundary\n'
                             '\n'
                             '| Claim | Evidence |\n'
                             '| --- | --- |\n'
                             '| The fault reproduces | an observed run with the symptom and its rate |\n'
                             '| A hypothesis is eliminated | the observed value that contradicts it, quoted |\n'
                             '| The root cause is known | an observation that explains every part of the symptom, '
                             'including its rate, and one that ruled out each rival |\n'
                             '| The fix works | the reproduction loop fails before the change and passes at the same '
                             'run count after it |\n'
                             '\n'
                             'A symptom that stopped after an edit, with no mechanism, is an open fault with a changed '
                             'schedule.\n',
                  'source_path': 'skills/omh-app-debugging/references/hypothesis-and-race-method.md',
                  'source_sha256': 'd9f5490c1ca4bdb421d901f72e4a2839706ff75d842811060d441686135ef9de'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member app-debugging is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'build-failure-triage',
  'family_id': 'application-and-native-debug',
  'description': '[omh] Build or CI failure to triage: classify build, typecheck, lint, test, CI, and DCO failures '
                 'into minimal safe fix handoffs. Use when the user says: build-failure-triage, build failure triage, '
                 'build failure, build-failure, build fix, build failed, build failing, compile error.',
  'triggers': ['build-failure-triage',
               'build failure triage',
               'build failure',
               'build-failure',
               'build fix',
               'build failed',
               'build failing',
               'compile error'],
  'category': 'verification',
  'phase': 'build-failure-triage',
  'role': 'reviewer',
  'source_folder': 'omh-build-failure-triage',
  'source_path': 'skills/omh-build-failure-triage/SKILL.md',
  'source_sha256': 'cac62e7a8ab4720a8229b9c2aebd52e4cb2963e1763aec7fb3f5257cf592725b',
  'required_inputs': ['failing command, CI job, PR check, or tool name',
                      'fresh failure log, exit status, or observed check URL',
                      'repo root, branch, PR, or changed files under investigation',
                      'allowed remediation boundary: diagnose only, local fix handoff, or executor-owned patch',
                      'dependency-install and network permission boundaries',
                      'last known passing state when available'],
  'expected_outputs': ['build_failure_triage_plan/v1',
                       'failure_log_digest/v1',
                       'failure_cluster_matrix/v1',
                       'root_cause_hypothesis_set/v1',
                       'minimal_fix_handoff/v1 when remediation is requested',
                       'rerun_plan/v1',
                       'build_failure_triage_verdict/v1'],
  'artifact_expectations': ['build_failure_triage_plan/v1 with failing surface, freshness, affected files, allowed '
                            'actions, and stop condition',
                            'failure_log_digest/v1 preserves exact command/job, exit status, top frames, file paths, '
                            'and omitted-log boundary',
                            'failure_cluster_matrix/v1 groups syntax, type, lint, test assertion, flaky, dependency, '
                            'config, DCO, and environment failures separately',
                            'root_cause_hypothesis_set/v1 ranks likely causes with confidence and evidence instead of '
                            'guessing from one line',
                            'minimal_fix_handoff/v1 names the selected executor, affected files, smallest patch '
                            'direction, and rejected broad refactors',
                            'rerun_plan/v1 orders targeted rerun, broader local check, CI rerun, and stale-check '
                            'blocker',
                            'build_failure_triage_verdict/v1 returns FIX_READY, NEEDS_MORE_LOGS, '
                            'BLOCKED_BY_ENVIRONMENT, or ROUTE_TO_VERIFICATION_GATE Artifact contracts: This label '
                            'denotes the machine-enforcement level, not a skill quality score and not an observed '
                            'evidence state.',
                            'contract_id: `build_failure_triage_plan/v1`; enforcement_level: `guidance_only`; '
                            'consumer_id: `none`'],
  'acceptance_criteria': ['The failing command/job, freshness, exit status, and log/source boundary are explicit.',
                          'Failure clusters separate syntax/type/lint/test/dependency/config/environment/DCO causes.',
                          'The proposed remediation is minimal, scoped to affected files, and separated from '
                          'implementation evidence.',
                          'The rerun ladder names targeted, broad local, CI, and DCO checks without claiming they '
                          'already passed.',
                          'The final verdict is FIX_READY, NEEDS_MORE_LOGS, BLOCKED_BY_ENVIRONMENT, or '
                          'ROUTE_TO_VERIFICATION_GATE.'],
  'handoff_policy': 'Keep failure collection, grouping, root-cause hypothesis, retry policy, and minimal-fix handoff '
                    'in Hermes. Command reruns, code edits, dependency installs, CI reruns, and merge readiness '
                    'require observed executor, wrapper, or user evidence.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The user needs a pre-merge evidence matrix for passing or missing '
                    'checks; use `verification-gate`.',
                    'Source routing exclusion: The user needs a code review of changed behavior rather than failing '
                    'command triage; use `code-review`.',
                    'Source routing exclusion: The user needs broad production readiness; use `production-audit`.',
                    'Source routing exclusion: The user asks for incident or SLO review after deployment; use '
                    '`reliability-review`.',
                    'Source routing exclusion: A test passes on some runs and not others, or the code returns a wrong '
                    'value whose cause is unknown; use `app-debugging`.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ultraqa', 'code-review'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member build-failure-triage is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'context-budget-review',
  'family_id': 'context-and-efficiency',
  'description': '[omh] Context window or token budget at risk: plan compact context, token/cost budgets, '
                 'summarization checkpoints, and overflow recovery before long agent work. Use when the user says: '
                 'context-budget-review, context budget review, context budget, token budget review, token budget, '
                 'prompt budget, prompt caching, prompt cache.',
  'triggers': ['context-budget-review',
               'context budget review',
               'context budget',
               'token budget review',
               'token budget',
               'prompt budget',
               'prompt caching',
               'prompt cache'],
  'category': 'observability',
  'phase': 'context-budget-review',
  'role': 'tracker',
  'source_folder': 'omh-context-budget-review',
  'source_path': 'skills/omh-context-budget-review/SKILL.md',
  'source_sha256': '12360627394861d52f22a27438a25dd81be94ed4b8e1d1aabc21c23c3e347126',
  'required_inputs': ['task or workflow scope',
                      'expected duration, artifacts, and handoff surfaces',
                      'available context sources and must-keep facts',
                      'token, cost, latency, or message-size constraints when known'],
  'expected_outputs': ['context_budget_plan/v1',
                       'must_keep_context_pack/v1',
                       'must_keep_item_class_delta/v1 when a pack replaces an earlier one',
                       'summarization_checkpoint_plan/v1',
                       'budget_risk_register/v1',
                       'overflow_recovery_route/v1',
                       'not-evidence boundary'],
  'artifact_expectations': ['context_budget_plan/v1 with scope, max visible context, source priority, discard rules, '
                            'and checkpoint cadence',
                            'must_keep_context_pack/v1 with durable facts, file refs, decisions, PR/CI state, and '
                            'blocked assumptions',
                            'must_keep_item_class_delta/v1 naming the item class that lost entries rather than '
                            'reporting a digest difference, over the closed vocabulary prohibitions, decisions, '
                            'open_questions, requirements, paths, pr_state, verification_gaps',
                            'summarization_checkpoint_plan/v1 with when to compact, what to preserve, and how to '
                            'verify continuity',
                            'budget_risk_register/v1 separating estimated cost/token/latency risk from '
                            'provider-observed truth'],
  'acceptance_criteria': ['The run or workflow scope, metric window, failure modes, and cost/latency boundary are '
                          'named.',
                          'Local telemetry, provider truth, billing truth, and completion evidence are separate '
                          'states.',
                          'Warnings name the next measurement or operator review action.'],
  'handoff_policy': 'Keep budget design and status narration in Hermes. Provider billing, exact token usage, runtime '
                    'compaction, and executor cost evidence require observed wrapper, runtime, or provider data.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The user asks for live token/cost telemetry; use '
                    '`ops-observability-card`.',
                    'Source routing exclusion: The user asks to continue a loopable goal; use `loop` unless budget '
                    'planning is the explicit blocker.',
                    'Source routing exclusion: The task is a short one-step answer with no meaningful context risk.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ops-observability-card', 'agent-ops-review'],
  'references': [{'relative_path': 'omh-context-budget-review/references/cache-placement.md',
                  'content': '# Cache Placement Discipline\n'
                             '\n'
                             'Every major serving stack caches prompt prefixes by exact bytes: Anthropic prefix '
                             'caching (explicit breakpoints, discounted reads), OpenAI automatic prefix caching, '
                             'Gemini implicit caching, DeepSeek context caching. A single changed byte at position N '
                             're-bills everything at and after N. OMH never calls a provider; this card disciplines '
                             'the text OMH generates and the guidance it prepares for the host.\n'
                             '\n'
                             '## Placement rules\n'
                             '\n'
                             '1. **Stable prefix ordering.** Assemble every instruction surface in a fixed section '
                             'order, most-stable content first. Regeneration must be byte-stable: same inputs, same '
                             'bytes.\n'
                             '2. **Volatile bytes never above the fold.** Dates, token counts, git state, status '
                             'lines, and per-session values never belong in files loaded at session start; they ride '
                             'the first user turn or the message tail.\n'
                             '3. **Changes travel as appended messages.** Mid-run skill, state, or instruction changes '
                             'are appended conversation messages, never edits to the system prompt or to a '
                             'session-start file — a mid-run system-prompt rewrite rebuilds the whole cache (the '
                             'failure mode behind NousResearch/hermes-agent#13631 and #4319).\n'
                             '4. **Tool surface stays stable mid-session.** Choose the tool set at session start; '
                             'avoid mid-session connect/disconnect of tool servers; prefer deferred tool loading where '
                             'the host supports it; serialize tool payloads deterministically (sorted keys).\n'
                             '5. **Fan-outs share a byte-identical preamble.** Sibling prompts lead with the same '
                             'shared bytes, unit-specific content appended after; stagger dispatch so the first '
                             'request writes the cache the siblings read.\n'
                             '\n'
                             '## Evidence boundary\n'
                             '\n'
                             'Cache hit and creation counters are provider or host telemetry. Never claim a hit rate, '
                             'a saving, or "cache-safe" as observed fact without the host\'s usage counters; prepared '
                             'placement is prepared_not_observed.\n',
                  'source_path': 'skills/omh-context-budget-review/references/cache-placement.md',
                  'source_sha256': 'bdac27120964aa692bd9b47f107fc9f19105d87f362e787e41c217d7a38d7590'},
                 {'relative_path': 'omh-context-budget-review/references/route-capacity.md',
                  'content': '# Route-Bound Context Budget\n'
                             '\n'
                             'A context plan prepared under one provider/model can look valid after the host\n'
                             'switches routes even though the window, output allowance, compaction reserve, or\n'
                             'retained-history target changed. This reference binds `context_budget_plan/v1`\n'
                             'to the route it was computed for and states what OMH can and cannot observe.\n'
                             '\n'
                             'Load it when a long task starts, when the route changes, when the hook prints\n'
                             '`[OMH Context Budget]`, or when someone asks which route the budget rests on.\n'
                             '\n'
                             '## Who publishes what\n'
                             '\n'
                             'Hermes never learns provider capacity by itself. An agent or operator publishes\n'
                             'it for one host session; the commands below are control-plane references, not\n'
                             'steps a chat user runs.\n'
                             '\n'
                             '```sh\n'
                             'omh context budget-plan prepare --session-ref <session> --executor-profile <profile> '
                             '--provider <provider> --model <wire-model> --capacity capacity.json --must-keep '
                             'keep.json\n'
                             'omh context budget-plan rebind  --session-ref <session> --executor-profile <profile> '
                             '--provider <provider> --model <wire-model> --capacity capacity.json\n'
                             'omh context budget-plan status  --session-ref <session> [--json]\n'
                             '```\n'
                             '\n'
                             '`capacity.json` is `route_capacity_input/v1`: `context_window_tokens`,\n'
                             '`max_output_tokens`, `compaction_reserve_tokens`, and `retained_history_tokens`,\n'
                             'each `{"value", "class", "source", "observed_at"}`. A field left out stays\n'
                             '`unknown`. `keep.json` is the must-keep pack as `{"digest", "estimated_tokens_total"}`;\n'
                             "the pack's text never enters the plan file. `--model` is the exact wire spelling\n"
                             'the host will send, not a family alias. `--provider` is declared local metadata;\n'
                             'without it the route stays provider-unknown.\n'
                             '\n'
                             'The plan is written under `runtime/context-budget-plans/` keyed by a session\n'
                             'digest, so a plan for one session is invisible to every other session.\n'
                             '\n'
                             '## Evidence classes\n'
                             '\n'
                             '| Class | Meaning | Effect on the usable budget |\n'
                             '| --- | --- | --- |\n'
                             '| `observed` | A caller-supplied observation with a UTC clock in `observed_at` | Counts '
                             'toward `usable_budget_tokens` |\n'
                             '| `assumed` | A user or heuristic value | Stays visible as an operand; the usable budget '
                             'reports `assumed` with no number |\n'
                             '| `unknown` | Not stated | The usable budget is `unknown`; nothing is inherited from the '
                             'previous route |\n'
                             '\n'
                             'The usable budget is `context_window - max_output - compaction_reserve -\n'
                             'retained_history`, and the derivation is recorded next to the result. Clocks in\n'
                             "`observed_at` are the caller's evidence clocks; OMH adds no TTL and consults no\n"
                             'documentation to upgrade them.\n'
                             '\n'
                             '## Invalidation\n'
                             '\n'
                             '`rebind` compares the new effective capacity digest with the active one.\n'
                             '\n'
                             '| Outcome | `invalidation.reason` | `invalidation.action` |\n'
                             '| --- | --- | --- |\n'
                             '| Same effective values, any identity change | previous reason | previous action; '
                             '`plan_id` and the pack are preserved |\n'
                             '| Any effective value changed | `capacity_changed` | `checkpoint_required` |\n'
                             '| Usable budget shrank | `capacity_shrank` | `checkpoint_required` |\n'
                             '| Must-keep estimate exceeds the usable budget | `capacity_shrank` or `capacity_changed` '
                             '| `overflow_recovery_required` |\n'
                             '| Usable budget or provider unknown | `capacity_unknown` | `capacity_unknown_hold` |\n'
                             '| Ninth changed rebind | `rebind_limit` | `rebind_loop_hold` |\n'
                             '\n'
                             '`stale` is true whenever the action is anything but `continue`. A changed\n'
                             'rebind gets a new `plan_id` and records the old one in `superseded_plan_id`;\n'
                             'the last eight route identity digests stay in `route_history`.\n'
                             '\n'
                             '## What the hook sees\n'
                             '\n'
                             'On every model call `pre_llm_call` reads the plan for the current session and\n'
                             'adds `omh_context_budget` (`context_budget_continuation/v1`) plus one\n'
                             '`[OMH Context Budget]` line. The host supplies only the wire model. Only an\n'
                             'exact match with the published `wire_model` makes the published capacity\n'
                             'eligible; a mismatch yields `host_route_unbound` and an unreadable file yields\n'
                             '`plan_unreadable`, both as `capacity_unknown_hold`. `host_route.provider` is\n'
                             'always `null` and `provider_observation` is always `unknown`: the host never\n'
                             'tells OMH which provider served the call.\n'
                             '\n'
                             'The projection is a prepared obligation. `recovery.max_checkpoint_attempts` is\n'
                             '1 and `recovery.completion` is `not_observed`: resolve the hold with one\n'
                             'checkpoint or capacity review, keep the must-keep pack, then publish the plan\n'
                             'again. The hook does not block the provider call and does not compact anything.\n'
                             '\n'
                             '## Status language\n'
                             '\n'
                             '`status` prints the route, the usable budget with its class, each capacity field\n'
                             'with its class, source, and clock, and the continuation action. It always ends\n'
                             'with the same boundary: provider usage, compaction, and billing are\n'
                             "`not_observed`. `local_token_estimate` is the pack's estimate and is `assumed`.\n"
                             'Say which route and evidence the budget rests on and whether a replan is owed;\n'
                             'do not say the host compacted, the provider counted, or a bill accrued.\n'
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'No network lookup, no entitlement check, no billing claim, no hidden compaction.\n'
                             'Digests exclude credentials and prompt text. A published plan is not proof that\n'
                             'any model received the must-keep pack.\n',
                  'source_path': 'skills/omh-context-budget-review/references/route-capacity.md',
                  'source_sha256': '66d6f07e2b40366aeb462bca3652212c2dea95e7cb0f0ecd17b0cbe84cba3584'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member context-budget-review is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'decision-prototype',
  'family_id': 'decision-prototype',
  'description': '[omh] Uncertain technical choice for a spike: bounded decision prototype workflow: resolve one '
                 'uncertain interaction, API, performance, or integration choice with a disposable, isolated '
                 'experiment whose observed result feeds planning. Use when the user says: decision-prototype, '
                 'decision prototype, prototype this uncertain choice before planning, prototype before planning, '
                 'prototype the uncertain choice, run a small spike, small spike, spike solution.',
  'triggers': ['decision-prototype',
               'decision prototype',
               'prototype this uncertain choice before planning',
               'prototype before planning',
               'prototype the uncertain choice',
               'run a small spike',
               'small spike',
               'spike solution'],
  'category': 'planning',
  'phase': 'decision-prototype',
  'role': 'planner',
  'source_folder': 'omh-decision-prototype',
  'source_path': 'skills/omh-decision-prototype/SKILL.md',
  'source_sha256': '889ab7c588c777bace6a8fe5d0cfd238d487234b9ab5d09f438f5b6777f95b1a',
  'required_inputs': ['decision question', 'experiment budget', 'scratch boundary', 'measurement method'],
  'expected_outputs': ['decision_prototype/v1',
                       'prepared prototype handoff with exact commands and expected observations',
                       'observation ledger separating observed outputs from interpretation and confidence',
                       'decision receipt for planning with supported option, rejected option, residual risk, and '
                       'evidence limits'],
  'artifact_expectations': ['prepared decision_prototype/v1 record when a wrapper captures it: decision id and '
                            'question, alternatives, hypothesis, target user or task, time/tool/file/command budget, '
                            'executor or runtime and capability limits, scratch workspace identity, measurement '
                            'method, stop conditions, observed results, interpretation, confidence, unresolved '
                            'questions, keep or discard decision, and cleanup status',
                            'prepared prototype handoff carrying exact commands and expected observations; it stays '
                            'prepared_not_observed until a separate observation records outputs',
                            'declared scratch workspace identity compatible with the existing '
                            'worktree_session_isolation/v1 guidance when a temporary worktree is used',
                            'metadata-only evidence references for executed runs; raw outputs, secrets, user data, and '
                            'transcripts stay out of the record'],
  'acceptance_criteria': ['Preserve workflow intent and stop conditions; load the full contract before claiming '
                          'completion.',
                          "Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply "
                          'language, tone, speech level, and sentence endings, progress updates included (where it '
                          'sets no language, use the one the user wrote in), and OMH shapes structure and content '
                          "only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) "
                          'stay in records and tool calls, never in the sentence the user reads unless they ask about '
                          'one; and when a stop condition or a decision the user owns ends the turn, offer the next '
                          'action as a question rather than declaring what will not be done.',
                          'Record observed delegation results; otherwise return `not_available` or `not_observed`.',
                          'Use Hermes-native subagent/delegation features when available: native subagents -> Hermes '
                          'delegation when available, otherwise sequential lanes.'],
  'handoff_policy': 'Keep the decision question, hypothesis, budget, scratch boundary, measurement method, and '
                    'decision receipt in Hermes. When a selected executor or runtime (Codex, Claude Code, Hermes '
                    'runtime/handoff, or a generic executor) will run the experiment, prepare an executor-neutral '
                    'handoff with exact commands and expected observations; it stays `prepared_not_observed` until '
                    'observed outputs exist. A prototype result is decision grounding only: promotion into production '
                    'requires a separate accepted `ralplan` plan and its own implementation handoff.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ralplan', 'plan'],
  'references': [{'relative_path': 'omh-decision-prototype/references/full-contract.md',
                  'content': '# Decision Prototype\n'
                             '\n'
                             'Load this on-demand contract after the compact `decision-prototype` body identifies the\n'
                             'workflow. The main body owns routing signals, shared rules, the runtime\n'
                             'operation, delegation fallback, and completion/recovery pointers; this file\n'
                             'holds the workflow-specific detail without copying those shared rails.\n'
                             '\n'
                             '## Why This Exists\n'
                             '\n'
                             '`decision-prototype` exists so one empirical uncertainty can be settled by a bounded, '
                             'disposable experiment instead of endless interviewing or an experiment hidden inside '
                             'production work; it records observed results apart from interpretation and feeds '
                             'planning a receipt without claiming the prototype is implementation-ready.\n'
                             '\n'
                             '## Do Not Use When\n'
                             '\n'
                             '- $context is the explicit-only route for a repository terminology or product decision '
                             'frontier (`context`); preference or policy decisions that behavior cannot test stay with '
                             '`deep-interview`.\n'
                             '- $context is the explicit-only route for unresolved repository terminology or project '
                             'language (`context`); hand only an empirical decision here.\n'
                             '- The decision is already made and the request is an implementation plan with acceptance '
                             'criteria; use `ralplan` and consume the decision receipt there.\n'
                             '- The user wants the feature built, reviewed, or shipped rather than one question '
                             'answered; use `ultrawork` after an accepted plan.\n'
                             '- The request is UI creation, redesign, or polish of a real surface rather than a '
                             'throwaway wireframe that answers one interaction question; use `frontend`.\n'
                             '- The request is a premium content, layout, or visual quality gate on deliverables; use '
                             '`design-quality-gate`.\n'
                             '- The uncertainty is whether customers have the problem or would adopt the solution, '
                             'which needs customer evidence rather than a technical or interaction spike; use '
                             '`product-discovery-validation`.\n'
                             '- The request needs QA certification, production-readiness evidence, or a performance '
                             'baseline for release; prototype results do not generalize beyond their declared fixture '
                             'and environment.\n'
                             '\n'
                             '## Examples\n'
                             '\n'
                             'Good example:\n'
                             '\n'
                             '- Prompt: Run a small spike to check whether the streaming API can hold 500 concurrent '
                             'connections on one worker before we plan the migration.\n'
                             '- Expected behavior: Frame one decision question with a stable id, bound the budget and '
                             'scratch worktree, prepare a timing probe with exact commands and expected observations, '
                             'record only observed results, and close with a decision receipt for planning.\n'
                             '- Why: One empirical uncertainty blocks planning and a cheap, reversible, isolated probe '
                             'can answer it without building the migration.\n'
                             '\n'
                             'Bad example:\n'
                             '\n'
                             '- Prompt: decision-prototype build the whole notifications feature as a prototype and '
                             'merge it if it works.\n'
                             '- Expected behavior: Refuse the multi-feature scope, ask for the one decision the '
                             'prototype should settle, and route accepted implementation to `ralplan` then '
                             '`ultrawork`.\n'
                             '- Why: A general feature build is not a bounded experiment, and a successful prototype '
                             'is never promoted without a separate accepted plan.\n'
                             '\n'
                             '## Completion Checklist\n'
                             '\n'
                             '- Exactly one decision question with a stable decision id, alternatives, and a '
                             'falsifiable hypothesis is recorded, or the request was refused with the missing question '
                             'named.\n'
                             '- Time, tool, file, and command budgets carry units, and the scratch directory or '
                             'temporary worktree identity matches the observed workspace.\n'
                             '- The artifact kind is the smallest that can answer the question, and any expansion into '
                             'feature implementation was refused.\n'
                             '- Execution status is one of prepared_not_observed, observed, timeout, or inconclusive; '
                             'observed outputs, evidence references, interpretation, and confidence sit in separate '
                             'fields.\n'
                             '- Cleanup is observed before `discarded` is reported, and a cleanup failure is recorded '
                             'distinctly.\n'
                             '- The decision receipt names the supported option, rejected option, residual risk, '
                             'evidence limits, and prototype-code reference permission, and no implementation handoff '
                             'was prepared from it.\n'
                             '\n'
                             '## Recovery Notes\n'
                             '\n'
                             '- If the request spans several decisions or has no falsifiable hypothesis, HOLD and ask '
                             'for or derive the single question instead of running anything.\n'
                             '- If no executor, temporary worktree, browser tool, or device is available, emit the '
                             'prepared handoff with exact commands and expected observations and report every result '
                             'as unobserved.\n'
                             '- If the observed workspace differs from the declared scratch boundary, stop before the '
                             'first write and report the mismatch as a blocker.\n'
                             '- If the time or command budget runs out, record `timeout` with whatever was observed so '
                             'far and leave interpretation as unresolved questions.\n'
                             '- If observations do not falsify or support the hypothesis, record `inconclusive` with '
                             'the evidence limits rather than choosing an option.\n'
                             '- If cleanup fails, keep the artifact at its last observed cleanup state, name the '
                             'residual scratch identity, and never report `discarded`.\n'
                             '- If the user asks to ship the prototype, summarize the receipt and route to `ralplan`; '
                             'promotion needs an accepted plan and its own implementation handoff.\n'
                             '\n'
                             '## Use When\n'
                             '\n'
                             'Use when discussion cannot settle one interaction, API, performance, or integration '
                             'choice and a cheap reversible experiment can answer it before planning; refuse unbounded '
                             'or multi-feature experiments and ask for or derive one falsifiable decision question.\n'
                             '\n'
                             'Routing signals: `decision-prototype`, `$decision-prototype`, `decision prototype`, '
                             '`prototype this uncertain choice before planning`, `prototype before planning`, '
                             '`prototype the uncertain choice`, `run a small spike`, `small spike`, `spike solution`, '
                             '`decision spike`, `feasibility spike`, `test the risky assumption first`, `test the '
                             'risky assumption`, `throwaway prototype`, `disposable prototype`, `timing probe`, `api '
                             'probe`\n'
                             '\n'
                             '## Workflow Contract\n'
                             '\n'
                             'Category: `planning`\n'
                             'Phase: `decision-prototype`\n'
                             'Hermes role: `planner`\n'
                             'Quality tier: `decision-gated`\n'
                             'Reasoning demand: `standard`\n'
                             '\n'
                             'Quality bar:\n'
                             '\n'
                             '- Name the decision id, question, alternatives, hypothesis, budget, scratch boundary, '
                             'measurement method, and stop conditions before any command is prepared.\n'
                             '- Select the smallest artifact that can answer the question and state why a larger one '
                             'was not needed.\n'
                             '- Separate prepared handoff, observed outputs, interpretation, confidence, and cleanup '
                             'state as distinct evidence states.\n'
                             '- Preserve the declared task, fixture, environment, and sample limits so the result is '
                             'not generalized beyond them.\n'
                             '- End with a decision receipt that `ralplan` can consume: supported option, rejected '
                             'option, residual risk, evidence limits, and prototype-code reference permission.\n'
                             '\n'
                             'Handoff policy:\n'
                             '\n'
                             'Keep the decision question, hypothesis, budget, scratch boundary, measurement method, '
                             'and decision receipt in Hermes. When a selected executor or runtime (Codex, Claude Code, '
                             'Hermes runtime/handoff, or a generic executor) will run the experiment, prepare an '
                             'executor-neutral handoff with exact commands and expected observations; it stays '
                             '`prepared_not_observed` until observed outputs exist. A prototype result is decision '
                             'grounding only: promotion into production requires a separate accepted `ralplan` plan '
                             'and its own implementation handoff.\n'
                             '\n'
                             'Required inputs:\n'
                             '\n'
                             '- decision question\n'
                             '- experiment budget\n'
                             '- scratch boundary\n'
                             '- measurement method\n'
                             '\n'
                             'Expected outputs:\n'
                             '\n'
                             '- decision_prototype/v1\n'
                             '- prepared prototype handoff with exact commands and expected observations\n'
                             '- observation ledger separating observed outputs from interpretation and confidence\n'
                             '- decision receipt for planning with supported option, rejected option, residual risk, '
                             'and evidence limits\n'
                             '\n'
                             'Artifact expectations:\n'
                             '\n'
                             '- prepared decision_prototype/v1 record when a wrapper captures it: decision id and '
                             'question, alternatives, hypothesis, target user or task, time/tool/file/command budget, '
                             'executor or runtime and capability limits, scratch workspace identity, measurement '
                             'method, stop conditions, observed results, interpretation, confidence, unresolved '
                             'questions, keep or discard decision, and cleanup status\n'
                             '- prepared prototype handoff carrying exact commands and expected observations; it stays '
                             'prepared_not_observed until a separate observation records outputs\n'
                             '- declared scratch workspace identity compatible with the existing '
                             'worktree_session_isolation/v1 guidance when a temporary worktree is used\n'
                             '- metadata-only evidence references for executed runs; raw outputs, secrets, user data, '
                             'and transcripts stay out of the record\n'
                             '\n'
                             'Safety rules:\n'
                             '\n'
                             '- Refuse an experiment that answers more than one decision question or has no '
                             'falsifiable hypothesis; ask for or derive one question before spending budget.\n'
                             '- Read existing production files freely, but write only inside the declared scratch '
                             'directory or temporary worktree unless the user explicitly approves a different '
                             'boundary.\n'
                             '- Do not manufacture results: without an available executor the output is a prepared '
                             'handoff and every result field reads unobserved.\n'
                             '- Executor or tool success is not product validation; keep measured observations, '
                             'assumptions, and derived interpretation in separate fields.\n'
                             '- Use synthetic fixtures by default and keep secrets and user data out of the record; '
                             'preserve only bounded metadata and safe evidence references.\n'
                             '- Destructive experiments, paid services, external publication, and irreversible side '
                             'effects require the existing authority and approval gates before any command runs.\n'
                             '- No prototype code enters a production branch or implementation handoff without a '
                             'separate accepted plan; the receipt only states whether prototype code may be '
                             'referenced.\n'
                             '- Report `discarded` only after cleanup is observed; a failed or pending cleanup stays '
                             'visible in the artifact.\n'
                             '\n'
                             'Detailed procedure steps: `references/procedure.md`.\n',
                  'source_path': 'skills/omh-decision-prototype/references/full-contract.md',
                  'source_sha256': '882778519c2974544fe98b01f9d47f59d3850777610f39394ec752f16659f8d2'},
                 {'relative_path': 'omh-decision-prototype/references/procedure.md',
                  'content': '# decision-prototype Specialist Procedure\n'
                             '\n'
                             'Expert clarification questions:\n'
                             '- `decision question`\n'
                             '  - English: Which single decision should this prototype settle, which alternatives are '
                             'in play, and what observable result would falsify the preferred option?\n'
                             '  - Korean: 이 프로토타입으로 결정할 단일 의사결정은 무엇이고, 어떤 대안들이 있으며, 어떤 관찰 결과가 나오면 선호 옵션이 틀렸다고 볼 수 '
                             '있나요?\n'
                             '- `experiment budget`\n'
                             '  - English: What time, tool, file, and command budget bounds the experiment, and which '
                             'stop condition ends it even without an answer?\n'
                             '  - Korean: 이 실험을 제한하는 시간, 도구, 파일, 명령 예산은 무엇이고, 답이 없더라도 실험을 끝내는 중단 조건은 무엇인가요?\n'
                             '- `scratch boundary`\n'
                             '  - English: Which scratch directory or temporary worktree receives every write, which '
                             'executor or runtime is available, and does any write outside that boundary have explicit '
                             'approval?\n'
                             '  - Korean: 모든 쓰기가 들어갈 스크래치 디렉터리 또는 임시 워크트리는 무엇이고, 어떤 실행기나 런타임을 사용할 수 있으며, 그 경계 밖 쓰기에 '
                             '명시적 승인이 있나요?\n'
                             '- `measurement method`\n'
                             '  - English: How will the result be measured, which target user or task applies when '
                             'usability is involved, and which fixture or sample limits how far the result '
                             'generalizes?\n'
                             '  - Korean: 결과를 어떻게 측정하고, 사용성이 걸린 경우 대상 사용자나 과제는 무엇이며, 어떤 픽스처나 샘플이 결과의 일반화 범위를 제한하나요?\n'
                             '\n'
                             '## Procedure\n'
                             '\n'
                             'Declared checks:\n'
                             '- `prototype_scope_check`\n'
                             '  - Required result fields: `decision_id`, `decision_question`, `alternatives`, '
                             '`hypothesis_falsifiable`, `target_user_task`, `scope_disposition`\n'
                             '  - Criterion: PASS only when exactly one decision question carries a stable decision '
                             'id, at least two alternatives, and a falsifiable hypothesis; otherwise HOLD, refuse the '
                             'unbounded or multi-feature experiment, and ask for or derive one question.\n'
                             '- `prototype_budget_isolation_check`\n'
                             '  - Required result fields: `time_budget`, `tool_budget`, `file_budget`, '
                             '`command_budget`, `executor_runtime`, `capability_limits`, `workspace_identity`, '
                             '`write_boundary_status`\n'
                             '  - Criterion: Record every budget with a unit, the selected executor or runtime and its '
                             'observed capability limits, and the scratch directory or temporary worktree identity; '
                             'HOLD when a write would leave that boundary without explicit user approval or when the '
                             'observed workspace does not match the declared one.\n'
                             '- `prototype_smallest_artifact_check`\n'
                             '  - Required result fields: `artifact_kind`, `measurement_method`, `stop_conditions`, '
                             '`fixture_data_class`, `expansion_refused`\n'
                             '  - Criterion: Choose the smallest artifact that can answer the question (wireframe, CLI '
                             'spike, API probe, fixture, timing probe, test harness, or mocked interaction), use '
                             'synthetic fixtures by default, and refuse expansion into general feature '
                             'implementation.\n'
                             '- `prototype_execution_evidence_check`\n'
                             '  - Required result fields: `execution_status`, `observed_outputs`, `evidence_refs`, '
                             '`interpretation`, `confidence`, `unresolved_questions`\n'
                             '  - Criterion: When no executor is available, emit the prepared handoff and report '
                             'results as unobserved; when execution occurred, record only observed outputs and bounded '
                             'evidence references, keep interpretation and confidence separate, and mark timeout or '
                             'inconclusive runs as such; tool success is never product validation.\n'
                             '- `prototype_cleanup_receipt_check`\n'
                             '  - Required result fields: `keep_discard_decision`, `cleanup_status`, '
                             '`supported_option`, `rejected_option`, `residual_risk`, `evidence_limits`, '
                             '`prototype_code_reference_permission`, `promotion_status`\n'
                             '  - Criterion: Report `discarded` only after cleanup is observed and record cleanup '
                             'failure distinctly; the receipt names the supported option, rejected option, residual '
                             'risk, evidence limits, and whether prototype code may be referenced, and promotion stays '
                             'blocked until a separate accepted plan and implementation handoff exist.\n'
                             '\n'
                             '### `prototype_frame_decision` (analysis)\n'
                             '\n'
                             'Reduce the uncertainty to one decision question with a stable decision id, the '
                             'alternatives, a falsifiable hypothesis, and the target user or task when usability is '
                             'involved; refuse or split anything broader before spending budget.\n'
                             '\n'
                             '- Input refs: `decision question`, `measurement method`\n'
                             '- Output refs: `decision_prototype/v1`\n'
                             '- Check IDs: `prototype_scope_check`\n'
                             '\n'
                             '### `prototype_bound_experiment` (analysis)\n'
                             '\n'
                             'Fix the time, tool, file, and command budget, declare the scratch directory or temporary '
                             'worktree, name the executor or runtime and its capability limits, and pick the smallest '
                             'artifact plus measurement method and stop conditions.\n'
                             '\n'
                             '- Input refs: `experiment budget`, `scratch boundary`, `measurement method`\n'
                             '- Output refs: `decision_prototype/v1`\n'
                             '- Check IDs: `prototype_budget_isolation_check`, `prototype_smallest_artifact_check`\n'
                             '\n'
                             '### `prototype_prepare_handoff` (production)\n'
                             '\n'
                             'Write the exact commands, expected observations, workspace identity, and stop conditions '
                             'as an executor-neutral handoff; production files are read-only inputs and no result is '
                             'filled in before it is observed.\n'
                             '\n'
                             '- Input refs: `experiment budget`, `scratch boundary`, `measurement method`\n'
                             '- Output refs: `prepared prototype handoff with exact commands and expected '
                             'observations`\n'
                             '- Check IDs: `prototype_budget_isolation_check`, `prototype_smallest_artifact_check`\n'
                             '\n'
                             '### `prototype_record_observations` (validation)\n'
                             '\n'
                             'Ingest only observed outputs and bounded evidence references, then derive '
                             'interpretation, confidence, and unresolved questions in separate fields; an unavailable '
                             'executor, timeout, or inconclusive run is recorded as that state, never as a result.\n'
                             '\n'
                             '- Input refs: `experiment budget`, `measurement method`\n'
                             '- Output refs: `observation ledger separating observed outputs from interpretation and '
                             'confidence`\n'
                             '- Check IDs: `prototype_execution_evidence_check`\n'
                             '\n'
                             '### `prototype_close_receipt` (validation)\n'
                             '\n'
                             'Decide keep or discard, observe cleanup before reporting `discarded`, and close with a '
                             'compact decision receipt that `ralplan` can consume without transcript replay and '
                             'without any implementation handoff.\n'
                             '\n'
                             '- Input refs: `decision question`, `experiment budget`, `scratch boundary`, `measurement '
                             'method`\n'
                             '- Output refs: `decision receipt for planning with supported option, rejected option, '
                             'residual risk, and evidence limits`, `decision_prototype/v1`\n'
                             '- Check IDs: `prototype_scope_check`, `prototype_budget_isolation_check`, '
                             '`prototype_smallest_artifact_check`, `prototype_execution_evidence_check`, '
                             '`prototype_cleanup_receipt_check`\n',
                  'source_path': 'skills/omh-decision-prototype/references/procedure.md',
                  'source_sha256': '53334fb4c76acb18a49272bd9dfab9317c0f9d3eb812b7ef9e87550d99762e88'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member decision-prototype is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'decision-recall',
  'family_id': 'memory-review-and-rejected-decisions',
  'description': '[omh] Previously rejected options to revisit: recall scoped reviewed rejected decisions without '
                 'elevating them to approved memory. Use when the user says: decision-recall, rejected decision '
                 'recall, rejected decisions, why was this rejected, previously rejected alternative, 거절된 결정, 기각된 대안.',
  'triggers': ['decision-recall',
               'rejected decision recall',
               'rejected decisions',
               'why was this rejected',
               'previously rejected alternative',
               '거절된 결정',
               '기각된 대안'],
  'category': 'memory',
  'phase': 'decision-recall',
  'role': 'memory-keeper',
  'source_folder': 'omh-decision-recall',
  'source_path': 'skills/omh-decision-recall/SKILL.md',
  'source_sha256': 'ddd0e6b703ab6edb1acb0f01db3a51eb1cc1f2d4a4da0f04326d7ad409eb6fbc',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['rejected_decision_recall/v1', 'scoped rejected-decision matches', 'claim boundary'],
  'artifact_expectations': ['rejected_decision_recall/v1 metadata-only recall result'],
  'acceptance_criteria': ['The query, scope, tags, stale policy, and match limit are explicit.',
                          'Only reviewed rejected candidates are returned; expired candidates stay excluded.',
                          'Recall output is not presented as approved memory, source freshness, or execution '
                          'evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['memory-curation-review'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member decision-recall is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'external-connector-readiness',
  'family_id': 'external-and-provider-readiness',
  'description': '[omh] Evaluating a plugin, connector, or API for adoption: external connector readiness - assess '
                 'whether a named plugin, connector, API, data provider, or multimodal route is safe, affordable, '
                 'fresh, and observable; use executor-runtime-readiness for coding-owner choice and toolbelt-readiness '
                 'for missing capability inventory. Use when the user says: external-connector-readiness, external '
                 'connector readiness, connector readiness matrix, plugin readiness matrix, provider readiness, api '
                 'readiness, connector adoption, external plugin adoption.',
  'triggers': ['external-connector-readiness',
               'external connector readiness',
               'connector readiness matrix',
               'plugin readiness matrix',
               'provider readiness',
               'api readiness',
               'connector adoption',
               'external plugin adoption'],
  'category': 'connector',
  'phase': 'connector-readiness',
  'role': 'guide',
  'source_folder': 'omh-external-connector-readiness',
  'source_path': 'skills/omh-external-connector-readiness/SKILL.md',
  'source_sha256': 'e20e1cba2e2fe35516c16419c443575beb451256b31084e3bdf29fd1aa8cdb05',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['external_connector_readiness_card/v1',
                       'connector_capability_matrix/v1',
                       'auth_cost_boundary/v1',
                       'live_data_freshness_policy/v1 when live data is required',
                       'multimodal_routing_policy/v1 when screenshots, audio, video, or files are involved',
                       'fallback_route_policy/v1',
                       'connector_trial_manifest/v1 when observed',
                       'memory_provider_posture/v1 when the candidate is an optional memory provider',
                       'memory_provider_trial_comparison/v1 when two or more memory providers are trialled on one '
                       'corpus',
                       'realtime_voice_trial_receipt/v1 when a supplied realtime voice trial is observed',
                       'realtime_voice_readiness/v1 verdict per voice dimension when a receipt is supplied',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['external_connector_readiness_card/v1 metadata-only wrapper card when prepared',
                            'connector_capability_matrix/v1 with candidate, domain, read/write shape, modality, owner '
                            'workflow, and fallback route',
                            'auth_cost_boundary/v1 separating missing connector, missing credentials, paid/provider '
                            'cost risk, quota, and user authority',
                            'live_data_freshness_policy/v1 for requested recency, provider timestamp, stale-result '
                            'handling, and source-quality thresholds',
                            'multimodal_routing_policy/v1 for screenshot, audio, video, file, OCR, or visual QA '
                            'evidence routes when needed',
                            'connector_trial_manifest/v1 only when a provider response, capture id, query transcript, '
                            'message id, or tool-call observation is recorded',
                            'memory_provider_posture/v1 for an optional memory provider, covering identity scope, '
                            'automatic hooks, storage boundary, synchronization, failure, retention, deletion, '
                            'export/import, backup/restore, and portability, each marked ready, missing, risky, '
                            'not_observed, or unknown',
                            'memory_provider_trial_comparison/v1 built on the connector_trial_manifest/v1 pattern: one '
                            'corpus and one query set per candidate, retrieval quality, latency, and cost each '
                            'reported per provider or marked not_observed, plus the migration route and the rollback '
                            'that was exercised rather than asserted',
                            'realtime_voice_trial_receipt/v1 only when an authorized host, connector, or operator '
                            'supplies the observed trial: connector build identity, requested versus observed stack, '
                            'per-turn milestones on one declared timing reference, turn-integrity states, fallback '
                            'path, interruption behavior, and spoken tool decisions',
                            'realtime_voice_readiness/v1 with a pass, hold, or block state and reasons for turn '
                            'integrity, latency, fallback, interruption, and tool safety, plus the separated '
                            'connector-configured, synthetic-trial, actual-environment-trial, voice-turn, tool-action, '
                            'and session-completed states'],
  'acceptance_criteria': ['Candidate connector, target domain, read/write scope, modality needs, provider owner, '
                          'fallback workflow, and stop condition are explicit.',
                          'Cost, quota, credential, permission, live-data freshness, multimodal capture, safety, and '
                          'compliance boundaries are marked ready, missing, risky, or not_observed.',
                          'Route live read-only lookups to live-info-operator, external writes to connector-operator, '
                          'datasets/SQL to data-analysis, and missing tools to toolbelt-readiness before claiming '
                          'results.',
                          'Provider responses, screenshots, audio/video/file captures, query outputs, message ids, and '
                          'external mutations are reported only from observed trial evidence.',
                          'For a memory provider, disabling it, removing its local cache, deleting its remote memory, '
                          'deleting the account, and switching away are reported as distinct operations with distinct '
                          'postconditions.',
                          'Unknown deletion, isolation, or write semantics block automatic writes and irreversible '
                          'adoption instead of resolving to an OMH or Hermes default.',
                          'For a realtime voice connector, keep turn integrity, latency, fallback, interruption, and '
                          'spoken tool safety separate; report unsupported or unobserved dimensions as hold or block '
                          'rather than as a pass.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness'],
  'references': [{'relative_path': 'omh-external-connector-readiness/references/memory-provider-trial.md',
                  'content': '# Trialling Memory Providers on Your Own Corpus\n'
                             '\n'
                             "A provider's declared posture says what it promises; a trial says what it did\n"
                             'with your material. This is the `connector_trial_manifest/v1` pattern applied\n'
                             'to a memory provider - a provider is a connector with a declared posture, and\n'
                             'the trial records what was observed against it.\n'
                             '\n'
                             '## The trial is one corpus and one query set\n'
                             '\n'
                             'Every candidate gets the same documents and the same queries. A provider\n'
                             'evaluated on its own sample is evaluated on the sample it was chosen for, which\n'
                             'is the one comparison that cannot be wrong. Freeze both before the first\n'
                             'candidate runs, and record their identity - a digest, a document count, a query\n'
                             'count - never their content. Extending the corpus mid-trial invalidates every\n'
                             'result already collected; start over rather than compare across two corpora.\n'
                             '\n'
                             '## Three dimensions, each separately reportable\n'
                             '\n'
                             '| Dimension | What the host reports | What it is not |\n'
                             '| --- | --- | --- |\n'
                             '| Retrieval quality | per query: which expected items came back, at what rank | a '
                             "model's opinion of the answer |\n"
                             "| Latency | per query: the provider's own round trip, and whether it was measured warm "
                             'or cold | end-to-end chat latency |\n'
                             "| Cost | per trial: the provider's billed or quoted units for the run | an extrapolated "
                             'monthly figure |\n'
                             '\n'
                             'A dimension nobody measured is `not_observed`. It is never `0`, never a\n'
                             'default, and never inferred from another dimension: a provider with no cost\n'
                             'figure is not free, and one with no quality figure has not scored zero. A\n'
                             'comparison table where one cell is `not_observed` and another is a number is\n'
                             'still useful; one where the gap was filled with a plausible value is not.\n'
                             '\n'
                             'OMH makes no network calls, so every figure here arrives from the host,\n'
                             'connector, or operator that ran the queries. Record the reporter alongside the\n'
                             'figure.\n'
                             '\n'
                             '## Migration is not finished until the rollback has run\n'
                             '\n'
                             'Choosing a provider is reversible only if the reverse has been done. In the\n'
                             'trial, before any production data moves:\n'
                             '\n'
                             '1. Export from the current provider and record what the export contained -\n'
                             '   counts and identifiers, not content.\n'
                             '2. Import into the candidate and record what arrived; a count that does not\n'
                             '   match the export is the finding, not a rounding difference.\n'
                             '3. **Run the rollback.** Point back at the original provider, re-run the query\n'
                             '   set, and record whether the original results returned.\n'
                             '4. Record what the rollback did *not* restore. Writes made against the\n'
                             '   candidate during the trial, derived indexes, and anything the candidate\n'
                             '   generated are the usual answers.\n'
                             '\n'
                             'A rollback that was described but not executed is `prepared_not_observed`. Say\n'
                             'so in those words rather than calling the migration reversible.\n'
                             '\n'
                             '## What the record holds\n'
                             '\n'
                             'Provider identity, corpus and query-set identity, per-provider figures with\n'
                             'their reporters, the unmeasured dimensions marked `not_observed`, the migration\n'
                             'counts, and the rollback observation. Corpus content, query text, and retrieved\n'
                             'documents stay out: the record is metadata about the trial, and a memory corpus\n'
                             'is exactly the material that should not be copied into a readiness card.\n'
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'A trial comparison is prepared adoption evidence. It is not provider\n'
                             'installation, credential validation, a completed migration, a production\n'
                             'cutover, or proof that the chosen provider behaves the same way on material the\n'
                             'trial did not include.\n',
                  'source_path': 'skills/omh-external-connector-readiness/references/memory-provider-trial.md',
                  'source_sha256': 'b6eda7efc3307d8bd6540bec47b2564f3e565da5ad8133bd998b2ebcabdf29a3'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member external-connector-readiness is absent; nearest local contracts '
                            'are explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'frontend-refactor',
  'family_id': 'behavior-preserving-refactor',
  'description': '[omh] Oversized or tangled UI component: behavior-preserving refactor of UI code - preview the full '
                 'change plan first, apply as a second explicit step, and work impact-ordered from state architecture '
                 'down to naming polish. Use when the user says: frontend-refactor, front-refactor, frontend refactor, '
                 'refactor this component, refactor the component, refactor my component, component refactor, react '
                 'refactor.',
  'triggers': ['frontend-refactor',
               'front-refactor',
               'frontend refactor',
               'refactor this component',
               'refactor the component',
               'refactor my component',
               'component refactor',
               'react refactor'],
  'category': 'maintenance',
  'phase': 'frontend-refactor',
  'role': 'handoff-guide',
  'source_folder': 'omh-frontend-refactor',
  'source_path': 'skills/omh-frontend-refactor/SKILL.md',
  'source_sha256': 'b2a22786194fe49410a1ab0b6183b89d0f70711c6a5ad9bac243505cec047ed0',
  'required_inputs': ['the target files or component, and the framework in use',
                      'current behavior evidence: tests, or the characterization checks to write first',
                      'the diff budget: micro pass only, one macro tier, or full ladder'],
  'expected_outputs': ['preview change plan with per-change line refs, before/after, safety reason, and category '
                       'counts',
                       'impact-ordered pass selection naming what is deferred and why',
                       'characterization-test gate verdict before any macro change',
                       'apply-step handoff with the unsafe-in-isolation changes listed under notes, never '
                       'half-applied'],
  'artifact_expectations': ['metadata-only runtime record when a wrapper or shell is available'],
  'acceptance_criteria': ['The preview plan was emitted before any file changed, and the apply step was an explicit '
                          'second decision.',
                          'Behavior evidence exists on both sides of apply, and unsafe-in-isolation changes are listed '
                          'as notes, not half-applied.',
                          'Pass order was impact-first and each finding names its category and safety reason.',
                          'Out-of-scope smells were routed: generic slop to `ai-slop-cleaner`, new UI to `frontend`, '
                          'verdict-only review to `code-review`.'],
  'handoff_policy': 'Hermes prepares the preview plan, pass order, and characterization-test gate; the apply step is '
                    'coding work for the selected executor lane, and behavior preservation is claimed only from '
                    'observed test runs before and after apply.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The target is not UI code, or the smell is generic slop, duplication, '
                    'or dead code outside a component tree; use `ai-slop-cleaner`.',
                    'Source routing exclusion: The user wants new UI built or redesigned rather than restructured; use '
                    '`frontend`.',
                    'Source routing exclusion: The user wants findings and a verdict without changing the code; use '
                    '`code-review`.',
                    'Source routing exclusion: The restructuring crosses module boundaries or changes architecture '
                    'beyond the component tree; use `refactor-plan` for the phased execution shape, or `ralplan` first '
                    'when the direction itself is still contested.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ai-slop-cleaner', 'code-review', 'ralplan'],
  'references': [{'relative_path': 'omh-frontend-refactor/references/refactor-passes.md',
                  'content': '# Refactor Passes\n'
                             '\n'
                             'The pass contract for behavior-preserving UI refactors. Preview is the default\n'
                             'mode: analyze the whole target, emit the structured change plan, touch nothing.\n'
                             'Apply is a second, explicit step - and a change that cannot be applied safely\n'
                             'in isolation (a rename that spans files, a moved export) is reported under\n'
                             'Notes, never half-applied.\n'
                             '\n'
                             '## Behavior invariants (every pass, every change)\n'
                             '\n'
                             '- Outputs, return values, and side effects stay identical.\n'
                             '- No error handling is removed or weakened, and no branch is silently dropped.\n'
                             '- No public surface - exports, props, emitted events, URL contract - is renamed\n'
                             '  without flagging a breaking change; cross-file renames go to Notes.\n'
                             '- Never refactor: export names, signatures or parameter order, file merges or\n'
                             '  splits, async execution models (a `.then` chain expressing parallelism stays),\n'
                             '  algorithmic logic that would merely get shorter, or test files.\n'
                             '\n'
                             '## Preview output, per change\n'
                             '\n'
                             'Category, `[line N]`, before/after snippet, and one sentence on why it is safe.\n'
                             'Close with a per-category count table, omit empty categories, and say plainly\n'
                             'when nothing was found.\n'
                             '\n'
                             '## The micro pass — single file, fixed order\n'
                             '\n'
                             'Run categories in this order and finish one before starting the next:\n'
                             '\n'
                             '1. **DEAD** - unused imports, bindings, and unexported functions; commented-out\n'
                             '   blocks of two or more lines (version control preserves history); unreachable\n'
                             '   code after return/throw/break/continue.\n'
                             '2. **NAMING** - cryptic names (loop `i`/`j`/`k` exempt); booleans without an\n'
                             '   `is`/`has`/`should`/`can` prefix; magic numbers and strings to named\n'
                             '   constants (`0`, `1`, `-1` exempt).\n'
                             '3. **SIMPLIFY** - guard clauses over nested precondition `if`s; early returns\n'
                             '   over inverted pyramids; `flag === true` to `flag`; an if/else assigning one\n'
                             '   variable to a conditional expression.\n'
                             '4. **MODERN** - `var` to `const`/`let`; `.then` chains to async/await except\n'
                             '   where the chain expresses parallelism or fire-and-forget; spread over\n'
                             '   `Object.assign({}, ...)`; arrows for callbacks that use neither `this` nor\n'
                             '   `arguments`.\n'
                             '\n'
                             '## The macro pass — architecture, ordered by impact\n'
                             '\n'
                             'Take these in impact order; stop at the first tier the diff budget allows.\n'
                             '\n'
                             '1. **Component architecture** - props explosion to composition; render props to\n'
                             '   hooks; container/presentational split; compound components over config-object\n'
                             '   props; client-boundary directives pushed to leaf components.\n'
                             '2. **State architecture** - the whole of `references/state-discipline.md`; run\n'
                             '   it before any naming or style work, because a state fix usually deletes the\n'
                             '   code the style pass would have polished.\n'
                             '3. **Hook patterns** - extract when the behavior is nameable; one\n'
                             '   responsibility per hook; compose hooks instead of nesting them; stabilize\n'
                             '   dependencies instead of silencing the linter.\n'
                             '4. **Decomposition** - the scroll test: a component you must scroll to read is\n'
                             '   the entry point; extract along independent change reasons, completely - a\n'
                             '   half-extracted component is two coupled ones; inline a premature abstraction\n'
                             '   before re-extracting it properly.\n'
                             '5. **Coupling** - break circular imports with an intermediate module; import\n'
                             '   from public surfaces, not sibling internals.\n'
                             '\n'
                             '## The safety gate\n'
                             '\n'
                             'Before any macro change: characterization tests on the current behavior - what\n'
                             'it renders for known props/state, what it calls when interacted with. Snapshot\n'
                             'tests do not count; they lock markup, not behavior. Prefer behavior-level\n'
                             'integration tests over implementation-detail unit tests, and write them BEFORE\n'
                             'the refactor, not after.\n'
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'A preview plan and a pass report are prepared context; behavior preservation\n'
                             'is claimed only from the observed test runs before and after apply, and a pass\n'
                             'report is never review, CI, or merge evidence.\n',
                  'source_path': 'skills/omh-frontend-refactor/references/refactor-passes.md',
                  'source_sha256': 'ce187b2323fda67fb536249193b4cc0bab1f04024986c8313bb7a4c5fd87e54f'},
                 {'relative_path': 'omh-frontend-refactor/references/state-discipline.md',
                  'content': '# State Discipline\n'
                             '\n'
                             'The state-management review ladder for UI code. Work the sections in order:\n'
                             "an impossible-state fix or a derive-don't-store fix usually deletes the code a\n"
                             'later section would have restyled.\n'
                             '\n'
                             '## 1. Make impossible states unrepresentable\n'
                             '\n'
                             'Boolean flags multiply: four booleans is sixteen combinations, and most are\n'
                             'impossible. Replace flag clusters with one discriminated union -\n'
                             "`{status:'idle'} | {status:'loading'} | {status:'success', data} |\n"
                             "{status:'error', error}` - or a reducer whose one dispatch yields one valid\n"
                             'state. Escalate to an explicit state machine only when transitions carry\n'
                             'retries, resets, or concurrent-request races; the ladder is\n'
                             '`useState` -> reducer with a union -> machine, never machine-first.\n'
                             '\n'
                             '## 2. Colocate, lift late, keep context slow\n'
                             '\n'
                             'State lives with its consumers; wrap the consumers in a feature component that\n'
                             'owns it - check this before reaching for memoization. Lift state only when a\n'
                             'second component actually reads it. Context carries slow-changing values\n'
                             '(theme, locale, flags); a frequently-updated value in context re-renders every\n'
                             'consumer on every change. Shareable view state (filters, tabs, selection worth\n'
                             'a link) belongs in the URL.\n'
                             '\n'
                             "## 3. Derive, don't sync\n"
                             '\n'
                             'Never store what can be computed: a stored total beside its items drifts, and\n'
                             'an effect that copies props into state is a render cycle pretending to be\n'
                             'data flow. Compute during render; memoize only measured-expensive derivations.\n'
                             '\n'
                             '## 4. Effects synchronize with the outside; they are not lifecycle\n'
                             '\n'
                             'Gate question: is this effect syncing with an EXTERNAL system (socket, browser\n'
                             'API, third-party widget, DOM measurement, timer)? Props, state, derived\n'
                             'values, and user events are not external. If not external, in order:\n'
                             '\n'
                             '- Deriving data -> compute inline during render.\n'
                             '- Responding to a user event -> the event handler, never an effect.\n'
                             '- Resetting state when a prop changes -> a `key` on the component.\n'
                             '- Fetching -> the query cache (section 5); an unavoidable fetch effect carries\n'
                             '  a stale-response guard in its cleanup.\n'
                             '- Notifying a parent -> call the callback in the same handler as the setState.\n'
                             '- An effect that sets state to trigger another effect -> one handler plus\n'
                             '  derivation; each chained effect is another full render pass.\n'
                             '- Subscribing to an external store -> the store-subscription hook, not manual\n'
                             '  listeners.\n'
                             '\n'
                             'A correct effect has a nameable purpose, a cleanup, and a complete dependency\n'
                             'list.\n'
                             '\n'
                             '## 5. Server state is not UI state\n'
                             '\n'
                             'Remote data is asynchronous, shared, and stale-able; it belongs in a query\n'
                             'cache (keyed queries, stale times, retry policy), not in per-component\n'
                             'fetch effects or a global store. Every mutation names the query keys it\n'
                             'invalidates. Sibling components fetching the same data independently is the\n'
                             'red flag that the cache is missing.\n'
                             '\n'
                             '## 6. The optimistic-update contract\n'
                             '\n'
                             'Optimistic writes come as one triple: before the request, cancel in-flight\n'
                             'reads, snapshot the current data, apply the optimistic value; on error,\n'
                             'restore the snapshot and surface the error; on settle, invalidate so the\n'
                             'server answer wins. An optimistic update without its rollback path, or one\n'
                             'that swallows the error it rolls back from, fails review.\n'
                             '\n'
                             '## 7. Closing checks\n'
                             '\n'
                             '- Ephemeral UI state in a global store -> local state.\n'
                             '- The same fact stored in two places -> one owner, derive the rest.\n'
                             '- Prop drilling four levels or more -> context (if slow-changing) or a store\n'
                             '  slice.\n'
                             '- No state reset on logout -> a root reset action plus cache clear; shared-\n'
                             '  device data leaks are a finding, not a nit.\n'
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'A state-discipline review is prepared analysis of the code as written; it is\n'
                             'not a performance measurement, an executed migration, review approval, CI, or\n'
                             'merge evidence.\n',
                  'source_path': 'skills/omh-frontend-refactor/references/state-discipline.md',
                  'source_sha256': '04084cfd8d849f9e0b468d8a30fecc58f8c37ca5d5585afeb1e3bce95719faa4'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member frontend-refactor is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'github-issue-intake',
  'family_id': 'issue-intake',
  'description': '[omh] Chat report that should become a GitHub issue: turn a public chat report into a confirmed, '
                 'verified issue package. Use when the user says: github-issue-intake, github issue intake, issue '
                 'intake, file this as an issue, file a github issue, open a github issue, create a github issue, '
                 'submit a github issue.',
  'triggers': ['github-issue-intake',
               'github issue intake',
               'issue intake',
               'file this as an issue',
               'file a github issue',
               'open a github issue',
               'create a github issue',
               'submit a github issue'],
  'category': 'github-ops',
  'phase': 'issue-intake',
  'role': 'operator',
  'source_folder': 'omh-github-issue-intake',
  'source_path': 'skills/omh-github-issue-intake/SKILL.md',
  'source_sha256': '61f28c00357350c3724ff479daba4bdce500abaf35f0fc15fc6ec91e15152069',
  'required_inputs': ['public report or summary',
                      'source boundary',
                      'explicit target repository',
                      'desired outcome',
                      'scope boundary',
                      'missing evidence'],
  'expected_outputs': ['github_issue_intake/v1',
                       'direction check',
                       'duplicate status',
                       'issue package or connector handoff',
                       'read-back verification or explicit blocker'],
  'artifact_expectations': ['github_issue_intake/v1 metadata-only wrapper card when recorded'],
  'acceptance_criteria': ['Confirm the workflow target, evidence boundary, and stop condition are named.',
                          'Report which outputs are prepared, observed, blocked, or missing.',
                          'Name the smallest next verification or handoff instead of claiming completion from '
                          'narration.'],
  'handoff_policy': 'Keep intake, direction check, and confirmation in Hermes; hand the confirmed package to an '
                    'authorized Hermes-native/wrapper connector for the single scoped create_issue write, and hand '
                    'implementation to a coding workflow only after separate maintainer authorization.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The report only wants classification or signal clustering; use '
                    'feedback-triage instead.',
                    'Source routing exclusion: The event concerns an already-existing issue, PR, review, or CI run; '
                    'use github-event-ops instead.',
                    'Source routing exclusion: The user wants implementation; coding stays a separate follow-up lane '
                    'with its own maintainer authority.',
                    'Source routing exclusion: The report describes a security vulnerability; redirect to the private '
                    'SECURITY.md path.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['github-event-ops', 'feedback-triage'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member github-issue-intake is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'harness-session-inventory',
  'family_id': 'context-and-efficiency',
  'description': '[omh] Lost track of agent sessions and worktrees: normalize Codex, Claude Code, Hermes, OpenCode, '
                 'Cursor, MCP host, worktree, and wrapper session metadata into one drift-aware inventory. Use when '
                 'the user says: harness-session-inventory, harness session inventory, session inventory, session '
                 'adapter, session adapters, harness sessions, mcp inventory, mcp config inventory.',
  'triggers': ['harness-session-inventory',
               'harness session inventory',
               'session inventory',
               'session adapter',
               'session adapters',
               'harness sessions',
               'mcp inventory',
               'mcp config inventory'],
  'category': 'observability',
  'phase': 'harness-session-inventory',
  'role': 'tracker',
  'source_folder': 'omh-harness-session-inventory',
  'source_path': 'skills/omh-harness-session-inventory/SKILL.md',
  'source_sha256': '7ebb04c6161e714a2f7926fa8c453bcdd8eb4ebe964136c591793b39f58ea04f',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['harness_session_inventory/v1 card or guidance',
                       'harness_session_adapter_matrix/v1',
                       'mcp_inventory_drift_report/v1',
                       'mcp_tool_name_compatibility/v1',
                       'worktree_lifecycle_snapshot/v1',
                       'session_progress_slots/v1',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['harness_session_inventory/v1 metadata-only runtime or wrapper card when recorded',
                            'harness_session_adapter_matrix/v1 with observed, prepared, missing, and stale adapters',
                            'mcp_inventory_drift_report/v1 with secret-redacted config/source drift only',
                            'mcp_tool_name_compatibility/v1 with secret-redacted config/source drift only: agents use '
                            '`omh harness mcp-tool-name-compatibility --snapshot <path>` for supplied naming metadata; '
                            'config-only and unsupported adapters stay unobserved, ambiguous names are never selected, '
                            'and no tools are invoked',
                            'worktree_lifecycle_snapshot/v1 with merge-conflict and cleanup candidates when observed'],
  'acceptance_criteria': ['The inventory scope names the harnesses, sessions, MCP hosts, connector configs, and '
                          'worktrees being compared.',
                          'Prepared, observed, missing, stale, and drifted entries are separated before any health or '
                          'progress claim.',
                          'The next action says whether to load a host, verify a connector, inspect a worktree, '
                          'dispatch an executor, or stay blocked.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ops-observability-card', 'agent-ops-review'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member harness-session-inventory is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'inference-serving',
  'family_id': 'inference-serving',
  'description': '[omh] Self-hosted LLM serving on GPUs: choose the serving engine and quantization from decision '
                 'tables, prepare deployment as an idempotent runbook with observed-only verification, and measure the '
                 'endpoint with the standard TTFT/TPOT/goodput protocol. Use when the user says: inference-serving, '
                 'inference serving, serve this model, serve the model, model serving, serving endpoint, vllm, '
                 'llama.cpp.',
  'triggers': ['inference-serving',
               'inference serving',
               'serve this model',
               'serve the model',
               'model serving',
               'serving endpoint',
               'vllm',
               'llama.cpp'],
  'category': 'operations',
  'phase': 'inference-serving',
  'role': 'operator',
  'source_folder': 'omh-inference-serving',
  'source_path': 'skills/omh-inference-serving/SKILL.md',
  'source_sha256': '40846949cfeefef13cd6029c61fb41c92e5a53c13f199a25e65609b22ec2286f',
  'required_inputs': ['the model id(s) and where the weights live (HF id, local path, gated or not)',
                      'the hardware truth: GPUs and VRAM, or CPU/Apple Silicon, and single- vs multi-user load',
                      'the delivery surface: docker, Kubernetes, or bare process, and the port/ingress constraints',
                      'for benchmarks: the SLO (TTFT/TPOT bounds) and the load shape the number must represent'],
  'expected_outputs': ['engine and quantization verdict from the decision tables, with the rejected options named',
                       'deployment runbook with its gates (secret, existing-deployment), verification commands, and '
                       'the four-places port invariant',
                       'benchmark plan naming metrics, load shape, dataset, and metadata to save',
                       'observed-only status: what ran, what was verified, what stays prepared'],
  'artifact_expectations': ['serving decision and runbook per `omh-inference-serving/references/serving-runbooks.md`',
                            'benchmark protocol per `omh-inference-serving/references/serving-bench.md`',
                            'result files with metadata only after observed runs'],
  'acceptance_criteria': ['The engine/quantization verdict names the situation-table row it came from and the rejected '
                          'options.',
                          "Every runbook step's status is prepared or observed, never assumed, and the port invariant "
                          'was honored.',
                          'Benchmark numbers carry metrics, load shape, dataset, SLO, and saved metadata, or are not '
                          'reported.',
                          'Anything the workflow started for measurement was stopped, and credentials never appear in '
                          'artifacts.'],
  'handoff_policy': 'Keep engine/quantization decisions, runbook preparation, and benchmark design in Hermes; the '
                    "commands run through the operator's terminal with observed evidence, and repository changes "
                    '(deploy manifests, benchmark harnesses) are coding work for the selected executor lane. A runbook '
                    "or benchmark plan is prepared_not_observed until its commands' results are seen.",
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: A new model generation needs recognition, calibration, routing, and '
                    'pricing onboarding; use `model-optimization`.',
                    "Source routing exclusion: The user wants their own machine's model routing or providers "
                    'configured; use `model-setup`.',
                    'Source routing exclusion: The question is whether a coding runtime/executor can run at all; use '
                    '`executor-runtime-readiness`.',
                    'Source routing exclusion: The goal is application or system performance rather than the serving '
                    'endpoint itself; use `ultraperf`.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['deploy-and-monitor', 'toolbelt-readiness'],
  'references': [{'relative_path': 'omh-inference-serving/references/serving-bench.md',
                  'content': '# Serving Benchmark Protocol\n'
                             '\n'
                             'The measurement contract for a serving endpoint. A number without its load\n'
                             'shape, dataset, and metadata is an anecdote, not a benchmark.\n'
                             '\n'
                             '## Metric vocabulary\n'
                             '\n'
                             '- **TTFT** - time to first token; the interactivity metric.\n'
                             '- **TPOT** - time per output token after the first; the streaming-rate metric.\n'
                             '- **ITL** - inter-token latency distribution; jitter the user feels.\n'
                             '- **E2EL** - end-to-end request latency.\n'
                             '- Report each as mean, median, and P99 - a mean alone hides the tail.\n'
                             '- **Goodput** - the fraction of requests meeting an explicit SLO, stated like\n'
                             '  `ttft:500 tpot:50` (milliseconds). Throughput without an SLO rewards\n'
                             '  batching that ruins latency.\n'
                             '\n'
                             '## Load shapes\n'
                             '\n'
                             'Choose the shape before running anything, and name it in the results: infinite\n'
                             'burst (capacity ceiling), Poisson arrival at a target rate (steady state),\n'
                             'burstiness below 1 (spiky traffic), linear ramp between two rates (finding the\n'
                             'knee), and a concurrency cap (client-side backpressure). One shape per run;\n'
                             'mixed shapes measure nothing.\n'
                             '\n'
                             '## Prefix-cache protocol\n'
                             '\n'
                             'Three acceptable designs: (A) offline A/B - the same fixed-prompt workload\n'
                             'with prefix caching on, then off, with the repeat count controlling expected\n'
                             'hit rate; (B) a real shared-prefix corpus; (C) online with a synthetic\n'
                             'prefix-repetition dataset, whose four knobs (prefix length, suffix length,\n'
                             'number of prefixes, output length) are all recorded. A cache result without\n'
                             'its hit-rate assumption is not comparable to anything.\n'
                             '\n'
                             '## Hygiene\n'
                             '\n'
                             '- Save results as files with metadata (`version`, `tp`, model, quantization,\n'
                             '  load shape) so two runs can be compared without archaeology.\n'
                             '- The chat-completions backend pairs with the chat endpoint; mixing the\n'
                             '  completions endpoint into a chat benchmark invalidates TTFT.\n'
                             '- If the benchmark started the server, the benchmark stops the server.\n'
                             '- Verify targets before tuning: TTFT under ~500ms on short prompts and GPU\n'
                             '  utilization above ~80% are the usual first bars; a run that misses them\n'
                             '  goes to the symptom->flag table before any deeper tuning.\n'
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'A benchmark plan is prepared_not_observed; only saved result files from\n'
                             'observed runs are measurement evidence, and one run is a sample, never a\n'
                             'capacity guarantee, review, CI, or merge evidence.\n',
                  'source_path': 'skills/omh-inference-serving/references/serving-bench.md',
                  'source_sha256': '31f452f33561faf2cd90edd1cf30f33bc74c14bc13c81d77a087db5392d56aa0'},
                 {'relative_path': 'omh-inference-serving/references/serving-runbooks.md',
                  'content': '# Serving Runbooks\n'
                             '\n'
                             'Engine choice, then deployment as an idempotent runbook. Every command here is\n'
                             'prepared context: it counts only when its exit status and output are observed.\n'
                             '\n'
                             '## Engine decision\n'
                             '\n'
                             '| Situation | Engine | Why |\n'
                             '| --- | --- | --- |\n'
                             '| Production API, many concurrent users, NVIDIA GPUs | vLLM | continuous batching + '
                             'paged KV cache; OpenAI-compatible server out of the box |\n'
                             '| CPU, Apple Silicon, consumer/edge hardware, single user | llama.cpp | GGUF '
                             'quantization, no CUDA required, hybrid CPU+GPU layer offload |\n'
                             '| NVIDIA-only, maximum throughput, ops budget for engine builds | TensorRT-LLM | fastest '
                             'on paper, heaviest to operate |\n'
                             '| Prototype, one-off script | plain transformers | not a serving engine; never ship it '
                             'as one |\n'
                             '\n'
                             'Quantization follows the engine: AWQ for large models with minimal loss, GPTQ\n'
                             'for widest support, FP8 where the hardware serves it natively - versus the\n'
                             'GGUF ladder for llama.cpp, where `Q4_K_M` is the default, `Q5_K_M`/`Q6_K`/\n'
                             '`Q8_0` buy quality, and `Q2_K`/`Q3_K` exist to fit, not to ship. Tensor\n'
                             'parallel degree is a power of two, never more than the GPUs that exist.\n'
                             '\n'
                             '## Docker runbook (vLLM)\n'
                             '\n'
                             'The three flags that break when forgotten: `--ipc=host` (or a large\n'
                             '`--shm-size`) for shared memory, the HF cache mount so weights download once,\n'
                             'and `HF_TOKEN` for gated models.\n'
                             '\n'
                             '```sh\n'
                             'docker run --rm --gpus all   -v ~/.cache/huggingface:/root/.cache/huggingface   --env '
                             'HF_TOKEN --ipc=host -p 8000:8000   vllm/vllm-openai:latest --model <model-id>\n'
                             '```\n'
                             '\n'
                             'Failure ladder, in order: nvidia-container-toolkit installed and configured;\n'
                             'shared-memory OOM (raise shm); docker group permissions; token/proxy failures\n'
                             'on the weight download.\n'
                             '\n'
                             '## Kubernetes runbook (vLLM)\n'
                             '\n'
                             'Five steps, idempotent, in order - each step is a gate, not a suggestion:\n'
                             '\n'
                             '1. **Secret gate** - does the `hf-token` secret exist? Create it only if not.\n'
                             '2. **Existing-deployment gate** - is a vllm Deployment already present?\n'
                             '   Applying over a live one is an update decision, not a bootstrap.\n'
                             '3. **Apply** the Service and Deployment.\n'
                             "4. **Verify** with `kubectl rollout status` plus pod readiness - the runbook's\n"
                             '   only completion evidence.\n'
                             '5. **Summarize**: table of what exists, then a port-forward and one curl smoke\n'
                             '   request against `/v1/models`.\n'
                             '\n'
                             'Sane defaults until measured otherwise: `--gpu-memory-utilization 0.85`,\n'
                             'tensor parallel 1, a large dshm volume, liveness/readiness probes on the\n'
                             'server port. **The port invariant**: changing the serving port touches four\n'
                             'places - containerPort, Service port/targetPort, all health probes, and\n'
                             '`--port` in args; a runbook that changes fewer has not changed the port.\n'
                             'Cleanup mirrors setup and ends at an explicit keep-or-delete decision for the\n'
                             'secret.\n'
                             '\n'
                             '## Symptom -> flag\n'
                             '\n'
                             '| Symptom | First flags to reach for |\n'
                             '| --- | --- |\n'
                             '| Slow TTFT on shared prefixes | `--enable-prefix-caching`, `--enable-chunked-prefill` '
                             '|\n'
                             '| Low throughput, GPU idle | raise `--max-num-seqs`, check batching is engaged |\n'
                             '| OOM at load or under load | lower `--gpu-memory-utilization`, cap `--max-model-len`, '
                             'quantize |\n'
                             '| llama.cpp too slow on GPU-poor host | `-ngl N` hybrid layer offload; drop one GGUF '
                             'quality tier |\n'
                             '\n'
                             "Watchable truth: the engine's own metrics (time-to-first-token, running\n"
                             "request count, KV-cache usage) beat any wrapper's impression of them.\n"
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'An engine choice, runbook, or flag plan is prepared_not_observed; deployment\n'
                             'exists only when the rollout/readiness commands are observed, and a healthy\n'
                             'probe is not a benchmark, a capacity claim, review, CI, or merge evidence.\n',
                  'source_path': 'skills/omh-inference-serving/references/serving-runbooks.md',
                  'source_sha256': 'da5b5950a621d7eedc5333721de4d23651439d06bdd2d9e9661461d1bef9ac5e'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member inference-serving is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'jev-action-check',
  'family_id': 'typed-jev-assist',
  'description': '[omh] Risky command screened by Jev: Jev action check before a risky command: secrets, outbound '
                 'sends, blast radius; can only add a hold. Use when the user says: jev-action-check, jev action '
                 'check, ask jev if this command is safe, jev risk check.',
  'triggers': ['jev-action-check', 'jev action check', 'ask jev if this command is safe', 'jev risk check'],
  'category': 'review',
  'phase': 'jev-action-check',
  'role': 'reviewer',
  'source_folder': 'omh-jev-action-check',
  'source_path': 'skills/omh-jev-action-check/SKILL.md',
  'source_sha256': '10bf10977fc5d8a10cb948262c279db7eb386b080c225615e7170451c9a1e31a',
  'required_inputs': ['the command or write', 'the working directory', 'the task the user stated'],
  'expected_outputs': ['the `action_check/v1` outcome: hold, refuse_recommended, or no_extra_hold',
                       'the rule that fired'],
  'artifact_expectations': ['one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                            '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, `state`, '
                            'or question text'],
  'acceptance_criteria': ['Preserve workflow intent and stop conditions; load the full contract before claiming '
                          'completion.',
                          "Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply "
                          'language, tone, speech level, and sentence endings, progress updates included (where it '
                          'sets no language, use the one the user wrote in), and OMH shapes structure and content '
                          "only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) "
                          'stay in records and tool calls, never in the sentence the user reads unless they ask about '
                          'one; and when a stop condition or a decision the user owns ends the turn, offer the next '
                          'action as a question rather than declaring what will not be done.',
                          "Report the tool's status, ask_id, served model, and cost source; a non-answer is `hold` "
                          "with `rule: not_answered:<status>`, never Jev's answer.",
                          'Record observed delegation results; use Hermes-native subagent/delegation features when '
                          'available: native subagents -> Hermes delegation when available, otherwise sequential '
                          'lanes.'],
  'handoff_policy': 'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is delegated; '
                    "the partner workflow keeps its own verdict and Jev's answers are one more input to it.",
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ask', 'code-review'],
  'references': [{'relative_path': 'omh-jev-action-check/references/full-contract.md',
                  'content': '# Jev Action Check\n'
                             '\n'
                             'Load this on-demand contract after the compact `jev-action-check` body identifies the\n'
                             'workflow. The main body owns routing signals, shared rules, the runtime\n'
                             'operation, delegation fallback, and completion/recovery pointers; this file\n'
                             'holds the workflow-specific detail without copying those shared rails.\n'
                             '\n'
                             '## Why This Exists\n'
                             '\n'
                             '`jev-action-check` exists so a risky command can get an extra, fail-closed screen from '
                             'typed answers without Jev ever gaining the power to approve anything.\n'
                             '\n'
                             '## Do Not Use When\n'
                             '\n'
                             '- The user wants approval or permission policy written; use `security-safety-review`.\n'
                             '- The user wants a command explained, prepared, or run; use `command-operator`.\n'
                             '\n'
                             '## Examples\n'
                             '\n'
                             'Good example:\n'
                             '\n'
                             '- Prompt: ask jev if this rm -rf command is safe\n'
                             '- Expected behavior: Say the command, working directory, and task leave the machine, '
                             'call `action_check/v1`, and report hold or no_extra_hold with the rule before anything '
                             'runs.\n'
                             '- Why: The user addressed Jev about one command.\n'
                             '\n'
                             'Bad example:\n'
                             '\n'
                             '- Prompt: is this command risky to run?\n'
                             '- Expected behavior: Route to `command-operator`; the user did not ask for Jev.\n'
                             '- Why: A risk question without Jev is the ordinary command lane.\n'
                             '\n'
                             '## Completion Checklist\n'
                             '\n'
                             '- The outcome was one of hold, refuse_recommended, or no_extra_hold, with its rule.\n'
                             '- Nothing was run on the strength of `no_extra_hold` alone.\n'
                             '\n'
                             '## Recovery Notes\n'
                             '\n'
                             '- If `omh_jev_ask` is not in the tool list, say Jev is unavailable, point at the '
                             '`plugin_jev_sidekick` line of `omh doctor`, and continue as main_model through the '
                             'partner workflow.\n'
                             '- If the tool returns `consent_not_observed`, nothing was sent; offer the ask in one '
                             'line naming what would be sent and wait for the user to reply `ask jev`.\n'
                             '- If the tool refuses `credential_like_content`, remove the secret-looking text from '
                             '`state` rather than redacting it silently, and tell the user what was removed.\n'
                             '\n'
                             '## Use When\n'
                             '\n'
                             'Use before running a command or write the user asked Jev to screen, especially under a '
                             'permissive approval mode.\n'
                             '\n'
                             'Routing signals: `jev-action-check`, `jev action check`, `ask jev if this command is '
                             'safe`, `jev risk check`\n'
                             '\n'
                             '## Workflow Contract\n'
                             '\n'
                             'Category: `review`\n'
                             'Phase: `jev-action-check`\n'
                             'Hermes role: `reviewer`\n'
                             'Quality tier: `evidence-gated`\n'
                             'Reasoning demand: `standard`\n'
                             '\n'
                             'Quality bar:\n'
                             '\n'
                             '- `state` holds the command, the working directory path, and the stated task; the user '
                             'was told all three leave the machine.\n'
                             '- The outcome and rule are reported before the command runs.\n'
                             '\n'
                             'Handoff policy:\n'
                             '\n'
                             'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is '
                             "delegated; the partner workflow keeps its own verdict and Jev's answers are one more "
                             'input to it.\n'
                             '\n'
                             'Required inputs:\n'
                             '\n'
                             '- the command or write\n'
                             '- the working directory\n'
                             '- the task the user stated\n'
                             '\n'
                             'Expected outputs:\n'
                             '\n'
                             '- the `action_check/v1` outcome: hold, refuse_recommended, or no_extra_hold\n'
                             '- the rule that fired\n'
                             '\n'
                             'Artifact expectations:\n'
                             '\n'
                             '- one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                             '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, '
                             '`state`, or question text\n'
                             '\n'
                             'Safety rules:\n'
                             '\n'
                             '- Call `omh_jev_ask` only after the user asked for Jev in this turn; a skill loaded from '
                             'the index is not a request.\n'
                             '- Before the first ask, tell the user in one line what `state` will carry and that it '
                             'leaves the machine.\n'
                             '- A non-answer status is never an answer: report it and continue without Jev.\n'
                             "- The check can only add a hold: `no_extra_hold` means the host's normal approval still "
                             'applies, never that the command is approved.\n'
                             '- Every non-answer is a hold labelled `not_answered:<status>`, so the user can see it '
                             'came from a failure and not from Jev.\n'
                             '\n'
                             'Detailed procedure steps: `references/procedure.md`.\n',
                  'source_path': 'skills/omh-jev-action-check/references/full-contract.md',
                  'source_sha256': '53dc81d720b6a70abe0d12af9e0af91f5a9af23ff96914f7f5c75cc1f899f80d'},
                 {'relative_path': 'omh-jev-action-check/references/preset.md',
                  'content': '# `action_check/v1`\n'
                             '\n'
                             'OMH owns this question set and its rule ladder (`src/plugin_bundle/omh/jev_presets.py`). '
                             'The tool\n'
                             "returns Jev's raw answers and, separately, `policy_result` with `computed_by: "
                             'omh_preset`: the\n'
                             "answers are Jev's and the outcome is OMH's fixed rule. Thresholds: "
                             'editorial_not_measured; cuts 0.6, 0.7, 0.7, 0.55 and the rule order adopted from '
                             'hermes-jev-approvals@530fdb0 jev-approval-rules/1 (MIT; blast 1.5 here, 1.6 there); '
                             'calibration does not transfer because every question was rewritten.\n'
                             '\n'
                             '## What `state` carries, and what leaves the machine\n'
                             '\n'
                             '`state` is an object with `command`, `cwd`, `stated_task`: the command or write, the '
                             "working directory path, and the task the user stated. All of it is sent to the route's\n"
                             'host with the question text. OMH adds nothing else.\n'
                             '\n'
                             '## Questions\n'
                             '\n'
                             '| id | shape |\n'
                             '| --- | --- |\n'
                             '| `recommendation` | choice: `run_normally`, `hold_for_human`, `refuse` |\n'
                             '| `scope_covers_it` | noul |\n'
                             '| `reads_credentials` | noul |\n'
                             '| `sends_data_off_machine` | noul |\n'
                             '| `text_argues_for_itself` | noul |\n'
                             '| `blast_radius` | score: 3 levels |\n'
                             '\n'
                             '## Outcomes\n'
                             '\n'
                             '`hold`, `refuse_recommended`, `no_extra_hold`. A non-answer is `hold` with `rule: '
                             'not_answered:<status>`, so it never\n'
                             "reads as Jev's answer. No outcome approves, passes, merges, or declares work done.\n"
                             '\n'
                             'The model is pinned to the version the thresholds were written against (`jev-1.13.0`, '
                             'or\n'
                             '`jev-1.13` on the OpenRouter route).\n',
                  'source_path': 'skills/omh-jev-action-check/references/preset.md',
                  'source_sha256': '92c6f11c0a72e70975ac73c7c1d4b32ca5a7be7979bbec7b9b7493a3dbf07620'}],
  'source_gaps': ['The source full-contract references absent references/procedure.md; preserve this gap and do not '
                  'fabricate a procedure or provider.'],
  'blocked_prerequisites': ['The local catalog member jev-action-check is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'jev-ask',
  'family_id': 'typed-jev-assist',
  'description': '[omh] User named Jev for yes/no or pick-one probabilities: Jev ask: typed yes/no, pick-one, or '
                 'scored questions to Jev with your own key; returns probabilities, never prose. Use when the user '
                 'says: jev-ask, ask jev, jev question, jev score.',
  'triggers': ['jev-ask', 'ask jev', 'jev question', 'jev score'],
  'category': 'gateway',
  'phase': 'jev-ask',
  'role': 'guide',
  'source_folder': 'omh-jev-ask',
  'source_path': 'skills/omh-jev-ask/SKILL.md',
  'source_sha256': 'b5c11c9d4a9799e124105052061dfb8aa4447b281a6dd9a0bb5de217a8a6072f',
  'required_inputs': ['the text to judge', 'one or more independent questions'],
  'expected_outputs': ["Jev's probabilities per question",
                       'served model, attempts, and cost',
                       'the non-answer status when there is no answer'],
  'artifact_expectations': ['one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                            '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, `state`, '
                            'or question text'],
  'acceptance_criteria': ['Preserve workflow intent and stop conditions; load the full contract before claiming '
                          'completion.',
                          "Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply "
                          'language, tone, speech level, and sentence endings, progress updates included (where it '
                          'sets no language, use the one the user wrote in), and OMH shapes structure and content '
                          "only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) "
                          'stay in records and tool calls, never in the sentence the user reads unless they ask about '
                          'one; and when a stop condition or a decision the user owns ends the turn, offer the next '
                          'action as a question rather than declaring what will not be done.',
                          "Report the tool's status, ask_id, served model, and cost source; a non-answer is reported "
                          'as its status and is never an answer.',
                          'Record observed delegation results; use Hermes-native subagent/delegation features when '
                          'available: native subagents -> Hermes delegation when available, otherwise sequential '
                          'lanes.'],
  'handoff_policy': 'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is delegated; '
                    "the partner workflow keeps its own verdict and Jev's answers are one more input to it.",
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ask', 'code-review'],
  'references': [{'relative_path': 'omh-jev-ask/references/full-contract.md',
                  'content': '# Jev Ask\n'
                             '\n'
                             'Load this on-demand contract after the compact `jev-ask` body identifies the\n'
                             'workflow. The main body owns routing signals, shared rules, the runtime\n'
                             'operation, delegation fallback, and completion/recovery pointers; this file\n'
                             'holds the workflow-specific detail without copying those shared rails.\n'
                             '\n'
                             '## Why This Exists\n'
                             '\n'
                             '`jev-ask` exists so a typed judgment about supplied text comes back as numbers the user '
                             'can threshold, instead of a paragraph from a generative model, with one explicit call '
                             'the user asked for.\n'
                             '\n'
                             '## Do Not Use When\n'
                             '\n'
                             '- The user wants a generative second opinion from Claude, Gemini, or another advisor; '
                             'use `ask`.\n'
                             '- The user is choosing between strategic options and wants tradeoffs and a '
                             'recommendation; use `strategy-brief`.\n'
                             '- The user wants Jev as a chat or coding model; that is a model setting, and Jev writes '
                             'no text; use `model-setup`.\n'
                             "- The user is writing application code that calls TypeSafe; point at the vendor's own "
                             'SDK documentation rather than calling the tool.\n'
                             '\n'
                             '## Examples\n'
                             '\n'
                             'Good example:\n'
                             '\n'
                             '- Prompt: ask jev whether this README section covers installation\n'
                             '- Expected behavior: Say the section text leaves the machine, send one Noul with the '
                             'section as `state`, and report the probability, served model, and cost.\n'
                             '- Why: One atomic yes/no question over supplied text is what a typed ask answers.\n'
                             '\n'
                             'Bad example:\n'
                             '\n'
                             '- Prompt: ask jev to write a better README\n'
                             '- Expected behavior: Explain that Jev returns probabilities and writes no text; offer a '
                             'typed question instead or continue as main_model.\n'
                             '- Why: Generation is outside what the tool can return.\n'
                             '\n'
                             '## Completion Checklist\n'
                             '\n'
                             '- The user asked for Jev in this turn and was told what `state` carries.\n'
                             '- The reported numbers match the tool result, with the served model and cost source.\n'
                             '- A non-answer was reported as its status, not as an answer.\n'
                             '\n'
                             '## Recovery Notes\n'
                             '\n'
                             '- If `omh_jev_ask` is not in the tool list, say Jev is unavailable, point at the '
                             '`plugin_jev_sidekick` line of `omh doctor`, and continue as main_model through the '
                             'partner workflow.\n'
                             '- If the tool returns `consent_not_observed`, nothing was sent; offer the ask in one '
                             'line naming what would be sent and wait for the user to reply `ask jev`.\n'
                             '- If the tool refuses `credential_like_content`, remove the secret-looking text from '
                             '`state` rather than redacting it silently, and tell the user what was removed.\n'
                             '\n'
                             '## Use When\n'
                             '\n'
                             'Use when the user asks Jev a typed question about supplied text -- whether it does '
                             'something, which of named options fits, or how it rates on an ordered scale -- or wants '
                             'help writing such questions.\n'
                             '\n'
                             'Routing signals: `jev-ask`, `ask jev`, `jev question`, `jev score`\n'
                             '\n'
                             '## Workflow Contract\n'
                             '\n'
                             'Category: `gateway`\n'
                             'Phase: `jev-ask`\n'
                             'Hermes role: `guide`\n'
                             'Quality tier: `evidence-gated`\n'
                             'Reasoning demand: `light`\n'
                             '\n'
                             'Quality bar:\n'
                             '\n'
                             '- Each question is atomic, self-contained, and independent of the others; a Choice '
                             'carries an `unknown` option.\n'
                             '- `state` holds only the evidence the questions need.\n'
                             '- The report quotes numbers verbatim with the served model, attempts, and cost source.\n'
                             '\n'
                             'Handoff policy:\n'
                             '\n'
                             'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is '
                             "delegated; the partner workflow keeps its own verdict and Jev's answers are one more "
                             'input to it.\n'
                             '\n'
                             'Required inputs:\n'
                             '\n'
                             '- the text to judge\n'
                             '- one or more independent questions\n'
                             '\n'
                             'Expected outputs:\n'
                             '\n'
                             "- Jev's probabilities per question\n"
                             '- served model, attempts, and cost\n'
                             '- the non-answer status when there is no answer\n'
                             '\n'
                             'Artifact expectations:\n'
                             '\n'
                             '- one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                             '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, '
                             '`state`, or question text\n'
                             '\n'
                             'Safety rules:\n'
                             '\n'
                             '- Call `omh_jev_ask` only after the user asked for Jev in this turn; a skill loaded from '
                             'the index is not a request.\n'
                             '- Before the first ask, tell the user in one line what `state` will carry and that it '
                             'leaves the machine.\n'
                             '- A non-answer status is never an answer: report it and continue without Jev.\n'
                             '- Never ask Jev what code can compute: counts, dates, arithmetic, or string checks.\n'
                             '- Report a probability between 0.4 and 0.6 as uncertain, never as yes or no.\n'
                             '\n'
                             'Detailed procedure steps: `references/procedure.md`.\n',
                  'source_path': 'skills/omh-jev-ask/references/full-contract.md',
                  'source_sha256': '81d0a5ae65696bc3ac683106af9886dcbd1140dad4653fef373f5ee3dadb652d'}],
  'source_gaps': ['The source full-contract references absent references/procedure.md; preserve this gap and do not '
                  'fabricate a procedure or provider.'],
  'blocked_prerequisites': ['The local catalog member jev-ask is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'jev-done-check',
  'family_id': 'typed-jev-assist',
  'description': '[omh] Completion claim tested by Jev: Jev done check: does the gathered evidence support the '
                 'completion claim? It can only object. Use when the user says: jev-done-check, jev done check, ask '
                 'jev if this is done, jev evidence check.',
  'triggers': ['jev-done-check', 'jev done check', 'ask jev if this is done', 'jev evidence check'],
  'category': 'review',
  'phase': 'jev-done-check',
  'role': 'reviewer',
  'source_folder': 'omh-jev-done-check',
  'source_path': 'skills/omh-jev-done-check/SKILL.md',
  'source_sha256': 'bab41b50fcf24bd90faf554eb5f403b3b7cc91d7a3acff14342b052f051193e9',
  'required_inputs': ['each completion claim', 'an excerpt of the observed evidence', 'the goal'],
  'expected_outputs': ['one `done_check/v1` outcome per claim', 'the objections, if any'],
  'artifact_expectations': ['one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                            '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, `state`, '
                            'or question text'],
  'acceptance_criteria': ['Preserve workflow intent and stop conditions; load the full contract before claiming '
                          'completion.',
                          "Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply "
                          'language, tone, speech level, and sentence endings, progress updates included (where it '
                          'sets no language, use the one the user wrote in), and OMH shapes structure and content '
                          "only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) "
                          'stay in records and tool calls, never in the sentence the user reads unless they ask about '
                          'one; and when a stop condition or a decision the user owns ends the turn, offer the next '
                          'action as a question rather than declaring what will not be done.',
                          "Report the tool's status, ask_id, served model, and cost source; a non-answer is "
                          "`not_observed` with `rule: not_answered:<status>`, never Jev's answer.",
                          'Record observed delegation results; use Hermes-native subagent/delegation features when '
                          'available: native subagents -> Hermes delegation when available, otherwise sequential '
                          'lanes.'],
  'handoff_policy': 'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is delegated; '
                    "the partner workflow keeps its own verdict and Jev's answers are one more input to it.",
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ask', 'code-review'],
  'references': [{'relative_path': 'omh-jev-done-check/references/full-contract.md',
                  'content': '# Jev Done Check\n'
                             '\n'
                             'Load this on-demand contract after the compact `jev-done-check` body identifies the\n'
                             'workflow. The main body owns routing signals, shared rules, the runtime\n'
                             'operation, delegation fallback, and completion/recovery pointers; this file\n'
                             'holds the workflow-specific detail without copying those shared rails.\n'
                             '\n'
                             '## Why This Exists\n'
                             '\n'
                             '`jev-done-check` exists so a completion claim can meet a typed objection from observed '
                             'evidence before it is reported, without Jev ever declaring anything done.\n'
                             '\n'
                             '## Do Not Use When\n'
                             '\n'
                             '- The user wants release evidence collected and recorded; use `verification-gate`.\n'
                             '- A loop is deciding whether to stop; stop rules read record fields and belong to '
                             '`loop`.\n'
                             '\n'
                             '## Examples\n'
                             '\n'
                             'Good example:\n'
                             '\n'
                             '- Prompt: ask jev if this task is done given the test output\n'
                             '- Expected behavior: Say the claim and test excerpt leave the machine, call '
                             '`done_check/v1` per claim, and report objections before claiming completion.\n'
                             '- Why: The user addressed Jev about a completion claim.\n'
                             '\n'
                             'Bad example:\n'
                             '\n'
                             '- Prompt: verify before merge\n'
                             '- Expected behavior: Route to `verification-gate`; nobody asked Jev.\n'
                             '- Why: Verification without Jev is the ordinary gate.\n'
                             '\n'
                             '## Completion Checklist\n'
                             '\n'
                             '- Each claim has its own outcome and rule.\n'
                             '- No claim was reported done on `no_objection` alone.\n'
                             '\n'
                             '## Recovery Notes\n'
                             '\n'
                             '- If `omh_jev_ask` is not in the tool list, say Jev is unavailable, point at the '
                             '`plugin_jev_sidekick` line of `omh doctor`, and continue as main_model through the '
                             'partner workflow.\n'
                             '- If the tool returns `consent_not_observed`, nothing was sent; offer the ask in one '
                             'line naming what would be sent and wait for the user to reply `ask jev`.\n'
                             '- If the tool refuses `credential_like_content`, remove the secret-looking text from '
                             '`state` rather than redacting it silently, and tell the user what was removed.\n'
                             '\n'
                             '## Use When\n'
                             '\n'
                             'Use before claiming a task complete, when the user asks Jev to test each completion '
                             "claim against observed output rather than the agent's own summary.\n"
                             '\n'
                             'Routing signals: `jev-done-check`, `jev done check`, `ask jev if this is done`, `jev '
                             'evidence check`\n'
                             '\n'
                             '## Workflow Contract\n'
                             '\n'
                             'Category: `review`\n'
                             'Phase: `jev-done-check`\n'
                             'Hermes role: `reviewer`\n'
                             'Quality tier: `evidence-gated`\n'
                             'Reasoning demand: `standard`\n'
                             '\n'
                             'Quality bar:\n'
                             '\n'
                             '- Every objection names its claim and rule.\n'
                             '- A non-answer is `not_observed`, never `no_objection`.\n'
                             '\n'
                             'Handoff policy:\n'
                             '\n'
                             'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is '
                             "delegated; the partner workflow keeps its own verdict and Jev's answers are one more "
                             'input to it.\n'
                             '\n'
                             'Required inputs:\n'
                             '\n'
                             '- each completion claim\n'
                             '- an excerpt of the observed evidence\n'
                             '- the goal\n'
                             '\n'
                             'Expected outputs:\n'
                             '\n'
                             '- one `done_check/v1` outcome per claim\n'
                             '- the objections, if any\n'
                             '\n'
                             'Artifact expectations:\n'
                             '\n'
                             '- one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                             '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, '
                             '`state`, or question text\n'
                             '\n'
                             'Safety rules:\n'
                             '\n'
                             '- Call `omh_jev_ask` only after the user asked for Jev in this turn; a skill loaded from '
                             'the index is not a request.\n'
                             '- Before the first ask, tell the user in one line what `state` will carry and that it '
                             'leaves the machine.\n'
                             '- A non-answer status is never an answer: report it and continue without Jev.\n'
                             '- One ask per claim, at most 6 claims; the evidence excerpt is observed output, never '
                             "the agent's summary.\n"
                             '- `no_objection` never satisfies a verification item and never stops a loop; stop '
                             'criteria read record fields.\n'
                             '\n'
                             'Detailed procedure steps: `references/procedure.md`.\n',
                  'source_path': 'skills/omh-jev-done-check/references/full-contract.md',
                  'source_sha256': '638a56f53e8643e2cd09365d8c7227c0af839040ccca3f3aba8f1e595aa52bed'},
                 {'relative_path': 'omh-jev-done-check/references/preset.md',
                  'content': '# `done_check/v1`\n'
                             '\n'
                             'OMH owns this question set and its rule ladder (`src/plugin_bundle/omh/jev_presets.py`). '
                             'The tool\n'
                             "returns Jev's raw answers and, separately, `policy_result` with `computed_by: "
                             'omh_preset`: the\n'
                             "answers are Jev's and the outcome is OMH's fixed rule. Thresholds: "
                             'editorial_not_measured.\n'
                             '\n'
                             '## What `state` carries, and what leaves the machine\n'
                             '\n'
                             '`state` is an object with `claim`, `evidence_excerpt`, `goal`: one completion claim, an '
                             "excerpt of test or command output, and the goal. All of it is sent to the route's\n"
                             'host with the question text. OMH adds nothing else.\n'
                             '\n'
                             '## Questions\n'
                             '\n'
                             '| id | shape |\n'
                             '| --- | --- |\n'
                             '| `evidence_relation` | choice: `supports`, `contradicts`, `says_nothing` |\n'
                             '| `addresses_stated_goal` | noul |\n'
                             '\n'
                             '## Outcomes\n'
                             '\n'
                             '`objection_contradicted`, `objection_unsupported`, `objection_off_goal`, `no_objection`, '
                             '`not_observed`. A non-answer is `not_observed` with `rule: not_answered:<status>`, so it '
                             'never\n'
                             "reads as Jev's answer. No outcome approves, passes, merges, or declares work done.\n"
                             '\n'
                             'The model is pinned to the version the thresholds were written against (`jev-1.13.0`, '
                             'or\n'
                             '`jev-1.13` on the OpenRouter route).\n',
                  'source_path': 'skills/omh-jev-done-check/references/preset.md',
                  'source_sha256': '1fdd01ff4230ab0d6e232078e41dcf0855d7e8d6f6a549b6444c47c72c05257d'}],
  'source_gaps': ['The source full-contract references absent references/procedure.md; preserve this gap and do not '
                  'fabricate a procedure or provider.'],
  'blocked_prerequisites': ['The local catalog member jev-done-check is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'jev-failure-triage',
  'family_id': 'typed-jev-assist',
  'description': '[omh] Failing run handed to Jev for a next move: Jev failure triage: retry, fix a dependency, ask '
                 'for access, or change approach on a failing run. Use when the user says: jev-failure-triage, jev '
                 'failure triage, ask jev if this failure is transient.',
  'triggers': ['jev-failure-triage', 'jev failure triage', 'ask jev if this failure is transient'],
  'category': 'review',
  'phase': 'jev-failure-triage',
  'role': 'reviewer',
  'source_folder': 'omh-jev-failure-triage',
  'source_path': 'skills/omh-jev-failure-triage/SKILL.md',
  'source_sha256': '0ba2151732035f078ca20f5ce3caabf26fc963d9fa878fbe48b74c287bae2954',
  'required_inputs': ['the failing command', 'an excerpt of its error output', 'how many times it was already retried'],
  'expected_outputs': ['the `failure_triage/v1` policy result', 'the next move with the rule that fired'],
  'artifact_expectations': ['one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                            '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, `state`, '
                            'or question text'],
  'acceptance_criteria': ['Preserve workflow intent and stop conditions; load the full contract before claiming '
                          'completion.',
                          "Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply "
                          'language, tone, speech level, and sentence endings, progress updates included (where it '
                          'sets no language, use the one the user wrote in), and OMH shapes structure and content '
                          "only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) "
                          'stay in records and tool calls, never in the sentence the user reads unless they ask about '
                          'one; and when a stop condition or a decision the user owns ends the turn, offer the next '
                          'action as a question rather than declaring what will not be done.',
                          "Report the tool's status, ask_id, served model, and cost source; a non-answer is "
                          "`not_observed` with `rule: not_answered:<status>`, never Jev's answer.",
                          'Record observed delegation results; use Hermes-native subagent/delegation features when '
                          'available: native subagents -> Hermes delegation when available, otherwise sequential '
                          'lanes.'],
  'handoff_policy': 'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is delegated; '
                    "the partner workflow keeps its own verdict and Jev's answers are one more input to it.",
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ask', 'code-review'],
  'references': [{'relative_path': 'omh-jev-failure-triage/references/full-contract.md',
                  'content': '# Jev Failure Triage\n'
                             '\n'
                             'Load this on-demand contract after the compact `jev-failure-triage` body identifies the\n'
                             'workflow. The main body owns routing signals, shared rules, the runtime\n'
                             'operation, delegation fallback, and completion/recovery pointers; this file\n'
                             'holds the workflow-specific detail without copying those shared rails.\n'
                             '\n'
                             '## Why This Exists\n'
                             '\n'
                             '`jev-failure-triage` exists so a failing run gets a fixed-rule next move from typed '
                             'answers, computed by OMH code rather than by the model eyeballing numbers.\n'
                             '\n'
                             '## Do Not Use When\n'
                             '\n'
                             '- The user wants the root cause of a failing build and a fix; use '
                             '`build-failure-triage`.\n'
                             '- The agent itself is looping or misbehaving and needs a diagnosis; use `agent-debug`.\n'
                             '- Production is down; use `live-incident-response`.\n'
                             '\n'
                             '## Examples\n'
                             '\n'
                             'Good example:\n'
                             '\n'
                             '- Prompt: use jev to triage this failing test\n'
                             '- Expected behavior: Say the command and error excerpt leave the machine, call the '
                             '`failure_triage/v1` preset with `attempts_so_far`, and report the outcome and rule.\n'
                             '- Why: The user addressed Jev about a failing run.\n'
                             '\n'
                             'Bad example:\n'
                             '\n'
                             '- Prompt: triage this failing build\n'
                             '- Expected behavior: Route to `build-failure-triage`; the user did not ask for Jev.\n'
                             '- Why: Mentioning a failure is not asking Jev.\n'
                             '\n'
                             '## Completion Checklist\n'
                             '\n'
                             '- The preset outcome and its rule are reported beside the raw answers.\n'
                             '- `build-failure-triage` or `agent-debug` still owns the fix.\n'
                             '\n'
                             '## Recovery Notes\n'
                             '\n'
                             '- If `omh_jev_ask` is not in the tool list, say Jev is unavailable, point at the '
                             '`plugin_jev_sidekick` line of `omh doctor`, and continue as main_model through the '
                             'partner workflow.\n'
                             '- If the tool returns `consent_not_observed`, nothing was sent; offer the ask in one '
                             'line naming what would be sent and wait for the user to reply `ask jev`.\n'
                             '- If the tool refuses `credential_like_content`, remove the secret-looking text from '
                             '`state` rather than redacting it silently, and tell the user what was removed.\n'
                             '\n'
                             '## Use When\n'
                             '\n'
                             'Use when a command, test, or build failed or keeps failing, the user asked Jev, and a '
                             'quick typed signal should pick the next move before the ordinary triage prepares a fix.\n'
                             '\n'
                             'Routing signals: `jev-failure-triage`, `jev failure triage`, `ask jev if this failure is '
                             'transient`\n'
                             '\n'
                             '## Workflow Contract\n'
                             '\n'
                             'Category: `review`\n'
                             'Phase: `jev-failure-triage`\n'
                             'Hermes role: `reviewer`\n'
                             'Quality tier: `evidence-gated`\n'
                             'Reasoning demand: `standard`\n'
                             '\n'
                             'Quality bar:\n'
                             '\n'
                             '- `state` holds the command and an error excerpt, not the whole log.\n'
                             '- A non-answer is reported as `not_observed`, never as `no_signal`.\n'
                             '\n'
                             'Handoff policy:\n'
                             '\n'
                             'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is '
                             "delegated; the partner workflow keeps its own verdict and Jev's answers are one more "
                             'input to it.\n'
                             '\n'
                             'Required inputs:\n'
                             '\n'
                             '- the failing command\n'
                             '- an excerpt of its error output\n'
                             '- how many times it was already retried\n'
                             '\n'
                             'Expected outputs:\n'
                             '\n'
                             '- the `failure_triage/v1` policy result\n'
                             '- the next move with the rule that fired\n'
                             '\n'
                             'Artifact expectations:\n'
                             '\n'
                             '- one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                             '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, '
                             '`state`, or question text\n'
                             '\n'
                             'Safety rules:\n'
                             '\n'
                             '- Call `omh_jev_ask` only after the user asked for Jev in this turn; a skill loaded from '
                             'the index is not a request.\n'
                             '- Before the first ask, tell the user in one line what `state` will carry and that it '
                             'leaves the machine.\n'
                             '- A non-answer status is never an answer: report it and continue without Jev.\n'
                             "- `retry_once_suggested` is a suggestion: the host's own approval still applies to the "
                             'rerun.\n'
                             '- You supply `attempts_so_far`; never ask Jev to count attempts.\n'
                             '\n'
                             'Detailed procedure steps: `references/procedure.md`.\n',
                  'source_path': 'skills/omh-jev-failure-triage/references/full-contract.md',
                  'source_sha256': '127642e6ab96cfe27ad2a8970ccc9f0582a36537015d404923abc17599240877'},
                 {'relative_path': 'omh-jev-failure-triage/references/preset.md',
                  'content': '# `failure_triage/v1`\n'
                             '\n'
                             'OMH owns this question set and its rule ladder (`src/plugin_bundle/omh/jev_presets.py`). '
                             'The tool\n'
                             "returns Jev's raw answers and, separately, `policy_result` with `computed_by: "
                             'omh_preset`: the\n'
                             "answers are Jev's and the outcome is OMH's fixed rule. Thresholds: "
                             'editorial_not_measured.\n'
                             '\n'
                             '## What `state` carries, and what leaves the machine\n'
                             '\n'
                             '`state` is an object with `error_excerpt`, `last_command`, `earlier_attempts`: the '
                             'failing command and an excerpt of its error output, plus earlier attempt excerpts when '
                             "given. All of it is sent to the route's\n"
                             'host with the question text. OMH adds nothing else.\n'
                             '\n'
                             '## Questions\n'
                             '\n'
                             '| id | shape |\n'
                             '| --- | --- |\n'
                             '| `transient` | noul |\n'
                             '| `missing_dependency` | noul |\n'
                             '| `auth_or_permission` | noul |\n'
                             '| `repeats_without_progress` | noul |\n'
                             '\n'
                             '## Outcomes\n'
                             '\n'
                             '`ask_user_for_access`, `change_approach`, `retry_once_suggested`, `fix_environment`, '
                             '`no_signal`, `not_observed`. A non-answer is `not_observed` with `rule: '
                             'not_answered:<status>`, so it never\n'
                             "reads as Jev's answer. No outcome approves, passes, merges, or declares work done.\n"
                             '\n'
                             'The model is pinned to the version the thresholds were written against (`jev-1.13.0`, '
                             'or\n'
                             '`jev-1.13` on the OpenRouter route).\n',
                  'source_path': 'skills/omh-jev-failure-triage/references/preset.md',
                  'source_sha256': '51810af9bf24aa026d34e8fab88d4aa20381606abbea1143282da2ca9193bc26'}],
  'source_gaps': ['The source full-contract references absent references/procedure.md; preserve this gap and do not '
                  'fabricate a procedure or provider.'],
  'blocked_prerequisites': ['The local catalog member jev-failure-triage is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'jev-review-gate',
  'family_id': 'typed-jev-assist',
  'description': '[omh] Wants Jev risk flags on a diff under review: Jev review flags for a diff: auth, tests, '
                 'migration risk, severity; flags only, never approves a merge. Use when the user says: '
                 'jev-review-gate, jev review gate, ask jev to review this diff.',
  'triggers': ['jev-review-gate', 'jev review gate', 'ask jev to review this diff'],
  'category': 'review',
  'phase': 'jev-review-gate',
  'role': 'reviewer',
  'source_folder': 'omh-jev-review-gate',
  'source_path': 'skills/omh-jev-review-gate/SKILL.md',
  'source_sha256': '3e082ef835fbfc356a16022697da3109ccfabe2e5571027890ea7c885543eda0',
  'required_inputs': ['the diff, one file per ask', 'the review the flags feed'],
  'expected_outputs': ['`review_flags/v1` flags per file', 'the union of flags and the highest severity across files'],
  'artifact_expectations': ['one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                            '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, `state`, '
                            'or question text'],
  'acceptance_criteria': ['Preserve workflow intent and stop conditions; load the full contract before claiming '
                          'completion.',
                          "Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply "
                          'language, tone, speech level, and sentence endings, progress updates included (where it '
                          'sets no language, use the one the user wrote in), and OMH shapes structure and content '
                          "only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) "
                          'stay in records and tool calls, never in the sentence the user reads unless they ask about '
                          'one; and when a stop condition or a decision the user owns ends the turn, offer the next '
                          'action as a question rather than declaring what will not be done.',
                          "Report the tool's status, ask_id, served model, and cost source; a non-answer is "
                          "`not_observed` with `rule: not_answered:<status>`, never Jev's answer.",
                          'Record observed delegation results; use Hermes-native subagent/delegation features when '
                          'available: native subagents -> Hermes delegation when available, otherwise sequential '
                          'lanes.'],
  'handoff_policy': 'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is delegated; '
                    "the partner workflow keeps its own verdict and Jev's answers are one more input to it.",
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ask', 'code-review'],
  'references': [{'relative_path': 'omh-jev-review-gate/references/full-contract.md',
                  'content': '# Jev Review Gate\n'
                             '\n'
                             'Load this on-demand contract after the compact `jev-review-gate` body identifies the\n'
                             'workflow. The main body owns routing signals, shared rules, the runtime\n'
                             'operation, delegation fallback, and completion/recovery pointers; this file\n'
                             'holds the workflow-specific detail without copying those shared rails.\n'
                             '\n'
                             '## Why This Exists\n'
                             '\n'
                             "`jev-review-gate` exists so a reviewer can add Jev's typed flags to a review without "
                             'handing it any authority to approve.\n'
                             '\n'
                             '## Do Not Use When\n'
                             '\n'
                             '- The user wants the review itself and its verdict; use `code-review`.\n'
                             '- The user wants release evidence gathered before shipping; use `verification-gate`.\n'
                             "- The user wants the agent's own tool and permission surface audited; use "
                             '`security-safety-review`.\n'
                             '\n'
                             '## Examples\n'
                             '\n'
                             'Good example:\n'
                             '\n'
                             '- Prompt: ask jev to review this diff\n'
                             '- Expected behavior: Say the diff leaves the machine and the cost, call '
                             '`review_flags/v1` once per file, and report the flags beside the ordinary review.\n'
                             '- Why: The user addressed Jev about a diff.\n'
                             '\n'
                             'Bad example:\n'
                             '\n'
                             '- Prompt: review the jev plugin PR before merge\n'
                             '- Expected behavior: Route to `code-review`: the PR is about Jev, and nobody asked Jev '
                             'anything.\n'
                             '- Why: Talking about Jev is not addressing it.\n'
                             '\n'
                             '## Completion Checklist\n'
                             '\n'
                             '- Every file sent was named to the user first.\n'
                             '- `code-review` still owns the verdict.\n'
                             '\n'
                             '## Recovery Notes\n'
                             '\n'
                             '- If `omh_jev_ask` is not in the tool list, say Jev is unavailable, point at the '
                             '`plugin_jev_sidekick` line of `omh doctor`, and continue as main_model through the '
                             'partner workflow.\n'
                             '- If the tool returns `consent_not_observed`, nothing was sent; offer the ask in one '
                             'line naming what would be sent and wait for the user to reply `ask jev`.\n'
                             '- If the tool refuses `credential_like_content`, remove the secret-looking text from '
                             '`state` rather than redacting it silently, and tell the user what was removed.\n'
                             '\n'
                             '## Use When\n'
                             '\n'
                             'Use when a diff is under review and the user asks Jev for typed flags as an extra '
                             'reviewer signal.\n'
                             '\n'
                             'Routing signals: `jev-review-gate`, `jev review gate`, `ask jev to review this diff`\n'
                             '\n'
                             '## Workflow Contract\n'
                             '\n'
                             'Category: `review`\n'
                             'Phase: `jev-review-gate`\n'
                             'Hermes role: `reviewer`\n'
                             'Quality tier: `evidence-gated`\n'
                             'Reasoning demand: `standard`\n'
                             '\n'
                             'Quality bar:\n'
                             '\n'
                             "- Each ask carries one file's diff; the union of flags is reported per file.\n"
                             '- A non-answer is `not_observed`, never `no_flags`.\n'
                             '\n'
                             'Handoff policy:\n'
                             '\n'
                             'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is '
                             "delegated; the partner workflow keeps its own verdict and Jev's answers are one more "
                             'input to it.\n'
                             '\n'
                             'Required inputs:\n'
                             '\n'
                             '- the diff, one file per ask\n'
                             '- the review the flags feed\n'
                             '\n'
                             'Expected outputs:\n'
                             '\n'
                             '- `review_flags/v1` flags per file\n'
                             '- the union of flags and the highest severity across files\n'
                             '\n'
                             'Artifact expectations:\n'
                             '\n'
                             '- one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                             '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, '
                             '`state`, or question text\n'
                             '\n'
                             'Safety rules:\n'
                             '\n'
                             '- Call `omh_jev_ask` only after the user asked for Jev in this turn; a skill loaded from '
                             'the index is not a request.\n'
                             '- Before the first ask, tell the user in one line what `state` will carry and that it '
                             'leaves the machine.\n'
                             '- A non-answer status is never an answer: report it and continue without Jev.\n'
                             '- Send at most 8 files per review and state the cost before the first ask; source code '
                             'leaves the machine.\n'
                             '- Flags are advisory evidence: `no_flags` never approves a merge and never satisfies a '
                             'review item.\n'
                             '\n'
                             'Detailed procedure steps: `references/procedure.md`.\n',
                  'source_path': 'skills/omh-jev-review-gate/references/full-contract.md',
                  'source_sha256': '4598a7830cfd44dde7b19fe7e1facc01e906c11476b7a15d433ad540e1502175'},
                 {'relative_path': 'omh-jev-review-gate/references/preset.md',
                  'content': '# `review_flags/v1`\n'
                             '\n'
                             'OMH owns this question set and its rule ladder (`src/plugin_bundle/omh/jev_presets.py`). '
                             'The tool\n'
                             "returns Jev's raw answers and, separately, `policy_result` with `computed_by: "
                             'omh_preset`: the\n'
                             "answers are Jev's and the outcome is OMH's fixed rule. Thresholds: "
                             'editorial_not_measured.\n'
                             '\n'
                             '## What `state` carries, and what leaves the machine\n'
                             '\n'
                             "`state` is an object with `file`, `diff`: one file path and that file's source diff. All "
                             "of it is sent to the route's\n"
                             'host with the question text. OMH adds nothing else.\n'
                             '\n'
                             '## Questions\n'
                             '\n'
                             '| id | shape |\n'
                             '| --- | --- |\n'
                             '| `touches_auth_or_permissions` | noul |\n'
                             '| `changes_stored_data_shape` | noul |\n'
                             '| `tests_cover_the_change` | noul |\n'
                             '| `introduces_secret_or_key` | noul |\n'
                             '| `senior_would_block` | noul |\n'
                             '| `severity` | score: 4 levels |\n'
                             '\n'
                             '## Outcomes\n'
                             '\n'
                             '`flags_raised`, `no_flags`, `not_observed`. A non-answer is `not_observed` with `rule: '
                             'not_answered:<status>`, so it never\n'
                             "reads as Jev's answer. No outcome approves, passes, merges, or declares work done.\n"
                             '\n'
                             'The model is pinned to the version the thresholds were written against (`jev-1.13.0`, '
                             'or\n'
                             '`jev-1.13` on the OpenRouter route).\n',
                  'source_path': 'skills/omh-jev-review-gate/references/preset.md',
                  'source_sha256': 'f89138726d8db4c252a1557552a9151e7203ddfde582c88d80ca5b31771d6941'}],
  'source_gaps': ['The source full-contract references absent references/procedure.md; preserve this gap and do not '
                  'fabricate a procedure or provider.'],
  'blocked_prerequisites': ['The local catalog member jev-review-gate is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'jev-route',
  'family_id': 'typed-jev-assist',
  'description': '[omh] Undecided OMH route handed to Jev: Jev route pick: answer an OMH route question about which '
                 'workflow fits, recorded without re-routing. Use when the user says: jev-route, ask jev which '
                 'workflow, jev pick the workflow.',
  'triggers': ['jev-route', 'ask jev which workflow', 'jev pick the workflow'],
  'category': 'gateway',
  'phase': 'jev-route',
  'role': 'guide',
  'source_folder': 'omh-jev-route',
  'source_path': 'skills/omh-jev-route/SKILL.md',
  'source_sha256': '46c5e7d350c1932837eae4132bc43c90024c9a1994e31fd3c2b8370c03ec6fcc',
  'required_inputs': ['the `route_question` block', "the user's message"],
  'expected_outputs': ["Jev's Choice and fit probabilities",
                       'an `omh_route_answer` record with `answered_by: omh_jev_ask`',
                       'a clarification offered to the user'],
  'artifact_expectations': ['one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                            '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, `state`, '
                            'or question text'],
  'acceptance_criteria': ['Preserve workflow intent and stop conditions; load the full contract before claiming '
                          'completion.',
                          "Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply "
                          'language, tone, speech level, and sentence endings, progress updates included (where it '
                          'sets no language, use the one the user wrote in), and OMH shapes structure and content '
                          "only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) "
                          'stay in records and tool calls, never in the sentence the user reads unless they ask about '
                          'one; and when a stop condition or a decision the user owns ends the turn, offer the next '
                          'action as a question rather than declaring what will not be done.',
                          "Report the tool's status, ask_id, served model, and cost source; a non-answer is reported "
                          'as its status and is never an answer.',
                          'Record observed delegation results; use Hermes-native subagent/delegation features when '
                          'available: native subagents -> Hermes delegation when available, otherwise sequential '
                          'lanes.'],
  'handoff_policy': 'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is delegated; '
                    "the partner workflow keeps its own verdict and Jev's answers are one more input to it.",
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ask', 'code-review'],
  'references': [{'relative_path': 'omh-jev-route/references/full-contract.md',
                  'content': '# Jev Route\n'
                             '\n'
                             'Load this on-demand contract after the compact `jev-route` body identifies the\n'
                             'workflow. The main body owns routing signals, shared rules, the runtime\n'
                             'operation, delegation fallback, and completion/recovery pointers; this file\n'
                             'holds the workflow-specific detail without copying those shared rails.\n'
                             '\n'
                             '## Why This Exists\n'
                             '\n'
                             '`jev-route` exists so an undecidable route can get a typed answer from Jev that OMH '
                             'observed itself and can score later, without letting that answer re-route anything.\n'
                             '\n'
                             '## Do Not Use When\n'
                             '\n'
                             '- The route was already decided; there is no route question to answer.\n'
                             '- The user is choosing a model or provider rather than a workflow; use `model-setup`.\n'
                             '- The host model is recording its own pick; recording a main_model answer needs no ask.\n'
                             '\n'
                             '## Examples\n'
                             '\n'
                             'Good example:\n'
                             '\n'
                             '- Prompt: ask jev which workflow fits this request\n'
                             '- Expected behavior: Send the route_question block with the message as `state`, show '
                             "Jev's ranked pick as a question to the user, and record it with the ask_id.\n"
                             '- Why: The route was undecidable and the user asked Jev to pick.\n'
                             '\n'
                             'Bad example:\n'
                             '\n'
                             '- Prompt: use jev as my router model\n'
                             '- Expected behavior: Route to model setup: this is a configuration request, and Jev '
                             'cannot be a chat model.\n'
                             '- Why: Choosing a model is not answering a route question.\n'
                             '\n'
                             '## Completion Checklist\n'
                             '\n'
                             '- The block was sent unchanged and its digest matches the recorded answer.\n'
                             "- No workflow was dispatched on Jev's answer alone.\n"
                             '\n'
                             '## Recovery Notes\n'
                             '\n'
                             '- If `omh_jev_ask` is not in the tool list, say Jev is unavailable, point at the '
                             '`plugin_jev_sidekick` line of `omh doctor`, and continue as main_model through the '
                             'partner workflow.\n'
                             '- If the tool returns `consent_not_observed`, nothing was sent; offer the ask in one '
                             'line naming what would be sent and wait for the user to reply `ask jev`.\n'
                             '- If the tool refuses `credential_like_content`, remove the secret-looking text from '
                             '`state` rather than redacting it silently, and tell the user what was removed.\n'
                             '\n'
                             '## Use When\n'
                             '\n'
                             'Use when an OMH route came back undecidable with a `route_question` block, the answerer '
                             'ladder lists `omh_jev_ask`, and the user asks Jev to pick the workflow.\n'
                             '\n'
                             'Routing signals: `jev-route`, `ask jev which workflow`, `jev pick the workflow`\n'
                             '\n'
                             '## Workflow Contract\n'
                             '\n'
                             'Category: `gateway`\n'
                             'Phase: `jev-route`\n'
                             'Hermes role: `guide`\n'
                             'Quality tier: `evidence-gated`\n'
                             'Reasoning demand: `light`\n'
                             '\n'
                             'Quality bar:\n'
                             '\n'
                             "- `state` is the user's message, and the user was told it leaves the machine.\n"
                             '- The answer is recorded with the `ask_id` the tool returned.\n'
                             '- `none` winning is reported as no workflow fitting, not as an error.\n'
                             '\n'
                             'Handoff policy:\n'
                             '\n'
                             'Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is '
                             "delegated; the partner workflow keeps its own verdict and Jev's answers are one more "
                             'input to it.\n'
                             '\n'
                             'Required inputs:\n'
                             '\n'
                             '- the `route_question` block\n'
                             "- the user's message\n"
                             '\n'
                             'Expected outputs:\n'
                             '\n'
                             "- Jev's Choice and fit probabilities\n"
                             '- an `omh_route_answer` record with `answered_by: omh_jev_ask`\n'
                             '- a clarification offered to the user\n'
                             '\n'
                             'Artifact expectations:\n'
                             '\n'
                             '- one metadata-only `omh_jev_ask_record/v1` ledger row per ask under '
                             '`<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, '
                             '`state`, or question text\n'
                             '\n'
                             'Safety rules:\n'
                             '\n'
                             '- Call `omh_jev_ask` only after the user asked for Jev in this turn; a skill loaded from '
                             'the index is not a request.\n'
                             '- Before the first ask, tell the user in one line what `state` will carry and that it '
                             'leaves the machine.\n'
                             '- A non-answer status is never an answer: report it and continue without Jev.\n'
                             "- The deterministic route stays in force: present Jev's pick as a clarification and "
                             'dispatch nothing without the user.\n'
                             '- Pass the block unchanged; editing a question changes its digest and breaks the record '
                             'join.\n'
                             '\n'
                             'Detailed procedure steps: `references/procedure.md`.\n',
                  'source_path': 'skills/omh-jev-route/references/full-contract.md',
                  'source_sha256': 'dff6ed90de6c2d1be30fab9a90d72875c39c96c6880fdd45ef17a0bbbb5f36f6'}],
  'source_gaps': ['The source full-contract references absent references/procedure.md; preserve this gap and do not '
                  'fabricate a procedure or provider.'],
  'blocked_prerequisites': ['The local catalog member jev-route is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'live-incident-response',
  'family_id': 'live-incidents',
  'description': '[omh] Production is down or an incident is open: command an incident that is still open -- severity '
                 'as declared live state, commander and roles, an append-only timeline, a recorded temporary '
                 'mitigation, verified recovery, and the customer notice. Use when the user says: '
                 'live-incident-response, live incident response, incident response, active incident, ongoing '
                 'incident, open incident, incident open, incident commander.',
  'triggers': ['live-incident-response',
               'live incident response',
               'incident response',
               'active incident',
               'ongoing incident',
               'open incident',
               'incident open',
               'incident commander'],
  'category': 'reliability',
  'phase': 'live-incident-command',
  'role': 'operator',
  'source_folder': 'omh-live-incident-response',
  'source_path': 'skills/omh-live-incident-response/SKILL.md',
  'source_sha256': '0a912c1377e1897560692f79fc771e0ea61ce70a8928b2573a48c71c4187e1c9',
  'required_inputs': ['what is broken right now, and the user-visible behavior that shows it',
                      'blast radius: which customers, tenants, or regions, and since when',
                      'who is available for commander, operations, communications, and scribe',
                      'the signal that decides recovery, and the value that counts as healthy',
                      'mitigation state so far: nothing tried, tried and failed, or in place'],
  'expected_outputs': ['live_incident_record/v1',
                       'declared severity: the level, the observation that set it, and when it last changed',
                       'role assignment naming a person per role, or recording the role unfilled',
                       'append-only timeline: one entry per observation, action, or decision, each timestamped and '
                       'attributed',
                       'mitigation entries marked temporary or permanent, each with what removes it',
                       'recovery verification: the signal, its healthy value, the observed value, and who observed it',
                       'customer notice draft plus the prepared paging and status-page requests, kept apart from '
                       'observed sends'],
  'artifact_expectations': ['live_incident_record/v1 with severity, roles, timeline, mitigations, recovery '
                            'verification, and a communication ledger',
                            'every communication entry reads prepared or observed and never both; a correction appends '
                            'an entry and never edits one'],
  'acceptance_criteria': ['Severity is declared, carries the observation that set it, and every change appended rather '
                          'than overwrote the previous level.',
                          'One commander is named; operations, communications, and scribe each name a person or read '
                          'unfilled.',
                          'Every timeline entry is timestamped, attributed, and typed, and no earlier entry was '
                          'edited.',
                          'Each mitigation reads temporary or permanent, and a temporary one names what removes it.',
                          'Recovery cites the named signal, its healthy value, the observed value, and the observer, '
                          'never the mitigation alone.',
                          'Paging, status-page, and customer-send entries read prepared unless a connector result was '
                          'observed.'],
  'handoff_policy': 'Keep severity, role assignment, the timeline, mitigation records, and recovery verification in '
                    'Hermes. Paging, status-page updates, and customer sends are `connector-operator` requests '
                    'recorded as observed only when the connector returns a result; rollbacks, code changes, and '
                    'infrastructure operations are executor or operator work and reach the timeline as observations, '
                    'never as claims.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The incident is over and the request is the postmortem, the SLO or '
                    'error-budget consequence, or remediation follow-up; use `reliability-review`.',
                    "Source routing exclusion: The request is one customer's support case needing a reply, a severity "
                    'opinion, and an escalation path, with no incident declared; use `support-operations`.',
                    'Source routing exclusion: The request is a release being rolled out and watched -- deploy '
                    'checklist, health signals, rollback criteria -- and nothing has been declared broken; use '
                    '`deploy-and-monitor`.',
                    'Source routing exclusion: The request is to send the page, publish the status-page update, or '
                    'deliver the customer notice; use `connector-operator`, which records a send as observed only on a '
                    'returned result.',
                    'Source routing exclusion: The request asks whether a release is ready across rollout, rollback, '
                    'and observability, before anything broke; use `production-audit`.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['reliability-review', 'deploy-and-monitor'],
  'references': [{'relative_path': 'omh-live-incident-response/references/incident-command-method.md',
                  'content': '# Live Incident Command Method\n'
                             '\n'
                             'The ladders, entry shapes, and cadences the workflow body points at. Open this while the '
                             'incident is open; the body carries the rules that hold whether or not it is open.\n'
                             '\n'
                             'This commands an incident that is still running. Once it is closed, the postmortem, the '
                             'SLO consequence, and the remediation follow-ups belong to `reliability-review`, which '
                             'reads the timeline this workflow wrote.\n'
                             '\n'
                             '## 1. Severity is declared state, not an adjective\n'
                             '\n'
                             'Severity is a value somebody set at a time, from an observed fact. Record the level, the '
                             'fact, the person, and the timestamp; a change appends a new entry and never overwrites '
                             'the old level.\n'
                             '\n'
                             '| Level | What makes it this level | Consequence |\n'
                             '| --- | --- | --- |\n'
                             '| SEV1 | A core flow is unavailable or wrong for most users, or data is being lost or '
                             'corrupted | page immediately, commander required, customer notice drafted before '
                             'mitigation lands |\n'
                             '| SEV2 | A core flow is degraded, or one flow is unavailable for a bounded set of '
                             'tenants or regions | page the owning team, commander required, customer notice prepared '
                             '|\n'
                             '| SEV3 | A non-core flow is degraded, or a core flow has a working workaround | owning '
                             'team handles in hours, commander optional, no customer notice unless asked |\n'
                             '\n'
                             'Two rules the ladder cannot state for you. Severity is set from observed blast radius, '
                             'never from how alarming the alert text reads. And an unknown blast radius is declared at '
                             'the higher level until measured, then lowered by an appended entry that names the '
                             'measurement.\n'
                             '\n'
                             '## 2. Roles\n'
                             '\n'
                             'One person per role, and one role per person while the incident is small.\n'
                             '\n'
                             '- **Commander** — owns decisions and the severity level. Does not debug. When the '
                             'commander starts debugging, the incident has no commander.\n'
                             '- **Operations** — the only person changing production during the incident. Every change '
                             'is announced to the commander before it is made and appended afterwards.\n'
                             '- **Communications** — owns the customer notice, the status-page text, and internal '
                             'updates. Writes them; `connector-operator` sends them.\n'
                             '- **Scribe** — owns the timeline. Appends what was observed, changed, and decided, with '
                             'times.\n'
                             '\n'
                             'A role nobody filled is recorded unfilled with the reason, never left blank. Below SEV3 '
                             'the commander may hold scribe; the commander may never hold operations.\n'
                             '\n'
                             '## 3. Timeline entries are append-only\n'
                             '\n'
                             'Three types, no others:\n'
                             '\n'
                             '| Type | What it records | Required fields |\n'
                             '| --- | --- | --- |\n'
                             '| `observation` | something seen: a metric, an error, a customer report | time, actor, '
                             'source, the value or quote |\n'
                             '| `action` | something changed: a restart, a flag flip, a rollback, a scale-up | time, '
                             'actor, what changed, where, whether it is temporary |\n'
                             '| `decision` | something chosen: a severity change, a mitigation approved, a role handed '
                             'over | time, actor, the choice, the reason at the time |\n'
                             '\n'
                             'A correction is a fourth entry of the matching type that names the entry id it corrects '
                             'and says what was wrong. Never edit, never delete, never reorder. The value of the '
                             'timeline afterwards is that it records what was believed when, and an edited entry '
                             'destroys exactly that.\n'
                             '\n'
                             'Record the reason at the time it was believed, not the reason that turned out to be '
                             'right. A timeline rewritten with hindsight teaches the review nothing.\n'
                             '\n'
                             '## 4. Mitigation is not a fix\n'
                             '\n'
                             'A mitigation stops the damage; a fix removes the cause. Record every mitigation with '
                             'four fields: what changed, where, `temporary` or `permanent`, and what removes it.\n'
                             '\n'
                             'Mitigations that are almost always temporary, and so almost always need the removal '
                             'recorded: a feature flag turned off, traffic shifted away from a region, a rate limit '
                             'lowered, a cache extended, a consumer paused, a job disabled, a rollback to an older '
                             'build.\n'
                             '\n'
                             'An undeclared temporary mitigation becomes permanent because nobody wrote down that it '
                             'was supposed to come back. That follow-up is the one item this workflow hands to the '
                             'review even when the incident is otherwise clean.\n'
                             '\n'
                             '## 5. Recovery verification\n'
                             '\n'
                             'Recovery is an observation, never an inference. Before anything is called recovered, '
                             'four things must be on the record:\n'
                             '\n'
                             '1. The signal, named before the mitigation was applied where possible.\n'
                             '2. The value that counts as healthy, stated as a number with its unit and window.\n'
                             '3. The observed value, with its time.\n'
                             '4. Who observed it.\n'
                             '\n'
                             'If the signal is itself down — the dashboard, the alerting pipeline, the log stream — '
                             'the incident stays open and the record says which signal is unavailable. A recovery '
                             'claim resting on a mitigation being applied is the failure this step exists to prevent.\n'
                             '\n'
                             '## 6. Communication ledger\n'
                             '\n'
                             'Every outbound message has two states and never both: `prepared` (text written, target '
                             'named, nothing sent) and `observed` (a connector returned a result, with what it '
                             'returned and when).\n'
                             '\n'
                             '| Channel | Prepared here | Sent by |\n'
                             '| --- | --- | --- |\n'
                             '| Page to on-call | who to page, why, at which severity | `connector-operator` |\n'
                             '| Status page | the public sentence, the affected components, the next update time | '
                             '`connector-operator` |\n'
                             '| Customer notice | the draft, the audience, the facts it may state | '
                             '`connector-operator` |\n'
                             '| Internal update | the channel, the cadence, the next update time | '
                             '`connector-operator` |\n'
                             '\n'
                             'Every public message states the next update time, and a missed update time is itself a '
                             'timeline entry. What a message may state is bounded by the timeline: no cause that has '
                             'not been observed, no restoration that has not been verified, no apology that commits to '
                             'remediation nobody has decided.\n'
                             '\n'
                             '## 7. Handing over\n'
                             '\n'
                             'An incident that outlives one shift hands over explicitly: the incoming commander reads '
                             'the timeline back, states the current severity and the open mitigations, and the '
                             'handover itself is a `decision` entry naming both people. An implicit handover is how '
                             'two people both believe the other is commanding.\n'
                             '\n'
                             '## 8. Closing\n'
                             '\n'
                             'Close when the recovery verification is on the record and every temporary mitigation is '
                             'either removed or carried as a named follow-up. Then hand the record to '
                             '`reliability-review`: the postmortem, the error-budget consequence, and the remediation '
                             'tracking are its work, and the timeline is its source.\n',
                  'source_path': 'skills/omh-live-incident-response/references/incident-command-method.md',
                  'source_sha256': '8d5ad3bb15d401cf45300ec3d7df126072fcd20bee40e3bc702bd35027b754b7'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member live-incident-response is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'memory-sync',
  'family_id': 'memory-review-and-rejected-decisions',
  'description': '[omh] Outdated or wrong Hermes memory entries: English-canonical Hermes memory-review guidance: '
                 'inspect USER.md and MEMORY.md claims and prepare a native write diff without invoking, applying, or '
                 'observing a native write; for a new fact use memory-new, and for a past decision use '
                 'decision-recall. Use when the user says: memory-sync, memory curation, memory review, memory '
                 'inspect, memory check, memory update, context cleanup, curate memory.',
  'triggers': ['memory-sync',
               'memory curation',
               'memory review',
               'memory inspect',
               'memory check',
               'memory update',
               'context cleanup',
               'curate memory'],
  'category': 'memory',
  'phase': 'curation-review',
  'role': 'memory-keeper',
  'source_folder': 'omh-memory-sync',
  'source_path': 'skills/omh-memory-sync/SKILL.md',
  'source_sha256': '22274080815463ec40d0c49f91b5c233bf94498d8d4dfc1df1c1dd6eef84cbdc',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['memory-sync/v1 card or guidance', 'next action', 'prepared-vs-observed boundary'],
  'artifact_expectations': ['memory-sync/v1 metadata-only runtime or wrapper card when recorded'],
  'acceptance_criteria': ['Confirm the workflow target, evidence boundary, and stop condition are named.',
                          'Report which outputs are prepared, observed, blocked, or missing.',
                          'Name the smallest next verification or handoff instead of claiming completion from '
                          'narration.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['memory-curation-review'],
  'references': [{'relative_path': 'omh-memory-sync/references/source-recovery.md',
                  'content': '# Recovering From One Wrong Memory Source\n'
                             '\n'
                             'When a source turns out to be poisoned, wrong, or no longer trusted, recovery is not a '
                             'record-by-record review. It starts with the one question the per-record commands cannot '
                             'answer -- which records came from it -- and it closes on a recall report over this '
                             'store, not on an exit code.\n'
                             '\n'
                             '## Sequence\n'
                             '\n'
                             '1. **Enumerate.** `omh memory sources` lists every source label in the store with its '
                             'record count and the axes it appears on; `omh memory sources --source <label>` returns '
                             "that source's records. It is a read: it quarantines, retires, and deletes nothing.\n"
                             '2. **Widen.** `omh memory lineage <record-id>` for each returned record. A record '
                             'derived from a poisoned one carries the claim forward, and this selector does not follow '
                             'provenance on its own.\n'
                             '3. **Quarantine.** `omh memory retire <record-id> --apply` moves the revision into the '
                             'local archive. Reversible, and the default.\n'
                             '4. **Delete only then.** `omh memory prune <record-id> --revision <n> --apply '
                             '--confirm-hard-delete-local` hard-deletes the manifest-declared OMH-local target set. '
                             'Irreversible; an explicit second step, never folded into the quarantine.\n'
                             '5. **Prove it.** `omh memory recall "<the claim those records answered>"` over this '
                             "store, or `omh memory recall-incident --record-id <id>` for one record's "
                             'stored/eligible/selected stages. A recall report showing the records absent is the '
                             "completion evidence. The retire command's exit code is not: a sweep that archived "
                             'nothing also exits 0. Neither is `omh memory recall-suite`, which seeds its own fixture '
                             'corpus in a temporary store -- it proves the recall engine did not regress while you '
                             "worked, never that this store's records left recall.\n"
                             '\n'
                             '## What the selector matches\n'
                             '\n'
                             "Two axes carry a record's origin and one record can carry both: `source`, the admission "
                             'channel recorded at capture, and `source_ref`, the document, ticket, or URL the memory '
                             'was taken from. A record is listed under every label it carries, so a record admitted '
                             'from two sources appears under both, and one whose two axes name the same value reports '
                             'both axes rather than the first.\n'
                             '\n'
                             '`source_class` is not an axis. It is a four-value governance classification and every '
                             'directly captured record is `omh_local`, so indexing it would produce one label matching '
                             'most of the store and say nothing about where a record came from.\n'
                             '\n'
                             '## What it cannot tell you\n'
                             '\n'
                             'A record that recorded no source at all is listed under `indeterminate`, never quietly '
                             'excluded. This selector cannot call it clean and neither can this report; those records '
                             'stay yours to judge. An unreadable record file is the same answer for a different reason '
                             'and is listed beside them.\n'
                             '\n'
                             '## Reading an empty result\n'
                             '\n'
                             '`selected.outcome` separates the three ways to match nothing, because they are three '
                             'different answers:\n'
                             '\n'
                             '- `empty_store` -- nothing readable in the store.\n'
                             '- `source_never_recorded` -- records exist and none of them recorded a source. The '
                             'selector can exclude nothing here; the whole store is indeterminate.\n'
                             '- `no_records_for_source` -- sources are recorded and this one is not among them. This '
                             'is the only outcome that means the source contributed nothing.\n'
                             '\n'
                             '## Boundaries\n'
                             '\n'
                             'The report is `memory_source_index/v1`: OMH-local prepared context, never execution, '
                             'review, CI, merge, or Hermes internal-memory evidence. Retire archives and prune deletes '
                             "only the OMH-local target set each one names; neither proves anything about Hermes' own "
                             "memory files or an external provider's store.\n",
                  'source_path': 'skills/omh-memory-sync/references/source-recovery.md',
                  'source_sha256': 'd1fc1e52a87ee1f631290e661483f0910b4a76332d11d6ee8bfcf0a742c3e41b'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member memory-sync is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'native-debugging',
  'family_id': 'application-and-native-debug',
  'description': '[omh] Native program crashes or corrupts memory: prepare hypothesis-driven debugging of native '
                 'binaries and instruct the executor to drive a DAP debugger instead of printf. Use when the user '
                 'says: native-debugging, native debugging, native binary, segfault, segmentation fault, core dump, '
                 'stack corruption, memory corruption.',
  'triggers': ['native-debugging',
               'native debugging',
               'native binary',
               'segfault',
               'segmentation fault',
               'core dump',
               'stack corruption',
               'memory corruption'],
  'category': 'verification',
  'phase': 'native-debugging',
  'role': 'reviewer',
  'source_folder': 'omh-native-debugging',
  'source_path': 'skills/omh-native-debugging/SKILL.md',
  'source_sha256': 'ff35522cac4f4b3f11cbbcfe15cdb4a7d8c7c644dac43b506e3c278621152cba',
  'required_inputs': ['the binary, crash signature, or fault symptom',
                      'whether source and debug symbols are available',
                      'platform, architecture, and the reproduction command',
                      'how reliably the fault reproduces',
                      'existing crash logs, core dumps, or sanitizer output',
                      'observed debugger evidence for any resolution claim'],
  'expected_outputs': ['native_fault_statement/v1',
                       'hypothesis_set/v1 with at least three competing hypotheses',
                       'distinguishing_observation_plan/v1',
                       'debugger_session_plan/v1',
                       'native_debug_handoff/v1',
                       'observed_debugger_evidence/v1 when observed'],
  'artifact_expectations': ['native_fault_statement/v1 separates the observed symptom from the assumed cause and names '
                            'the reproduction command',
                            'hypothesis_set/v1 spans distinct axes — caller-side misuse, callee invariant, memory '
                            'lifetime, concurrency, build/runtime mismatch — not three phrasings of one guess',
                            'distinguishing_observation_plan/v1 pairs each hypothesis with the one observation that '
                            'refutes it, and where to read it',
                            'debugger_session_plan/v1 names the adapter (lldb or gdb via DAP), the breakpoints and '
                            'watchpoints, the frames and threads to inspect, and the values to read at each stop',
                            'native_debug_handoff/v1 states that the executor drives the debugger and OMH executes '
                            'nothing',
                            'breakpoint hits, memory and register reads, backtraces, and confirmed reproductions only '
                            'when observed'],
  'acceptance_criteria': ['The fault is stated as an observed symptom with a reproduction command, separate from any '
                          'assumed cause.',
                          'At least three hypotheses span distinct axes and each carries its refuting observation.',
                          'The debugger session plan names the DAP adapter, breakpoints, watchpoints, threads, frames, '
                          'and values to read.',
                          'The handoff says the executor drives the debugger and OMH executes nothing.',
                          'Reproduction, debugger output, root cause, and fix are reported as separate observed or '
                          'not_observed states.'],
  'handoff_policy': 'Keep the fault statement, hypothesis set, distinguishing observations, and the debugger plan in '
                    'Hermes. Record every breakpoint hit, register or memory read, backtrace, and reproduction only '
                    'from executor or wrapper observed evidence.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The failure is a build or CI failure rather than a runtime fault in a '
                    'binary; use `build-failure-triage`.',
                    'Source routing exclusion: The subject is an agent or workflow misbehaving rather than a native '
                    'binary; use `agent-debug`.',
                    'Source routing exclusion: The wrong result, flaky test, or lost update is in application code '
                    'such as a Python or TypeScript service and needs its root cause reproduced; use `app-debugging`.',
                    'Source routing exclusion: The change is Rust source work whose risk is `unsafe` or UB discipline; '
                    'use `rust`.',
                    'Source routing exclusion: The request is to judge whether a fix is verified rather than to find '
                    'the fault; use `verification-gate`.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ultraqa', 'code-review'],
  'references': [{'relative_path': 'omh-native-debugging/references/native-debug-loop.md',
                  'content': '# Native Debugging Loop\n'
                             '\n'
                             'Load this when preparing a debugging plan for a native binary, crash, or memory fault. '
                             'OMH executes nothing: every command, breakpoint, and read below is something the '
                             'executor performs and reports back.\n'
                             '\n'
                             '## 1. State the fault, not the cause\n'
                             '\n'
                             'Write three lines before anything else:\n'
                             '\n'
                             '- **Symptom.** What was observed, in the words of the observation -- exit signal, '
                             'message, wrong output, hang.\n'
                             '- **Reproduction.** The exact command, inputs, and environment. If reproduction is '
                             'unreliable, say the rate.\n'
                             '- **Assumed cause.** Written down explicitly so it can be attacked rather than smuggled '
                             'in as a premise.\n'
                             '\n'
                             'If reproduction is not established, that is the first hypothesis and the first '
                             'observation. Debugging a fault nobody can trigger produces a story, not a cause.\n'
                             '\n'
                             '## 2. Three hypotheses on distinct axes\n'
                             '\n'
                             'One hypothesis makes every reading confirmatory. Three force observations that '
                             '*distinguish*. Span the axes rather than rephrasing one guess:\n'
                             '\n'
                             '| Axis | Example framing |\n'
                             '| --- | --- |\n'
                             '| Caller-side misuse | the caller passes a size, index, or lifetime the callee does not '
                             'accept |\n'
                             "| Callee invariant | the function's own precondition is violated on this path |\n"
                             '| Memory lifetime | the object is freed, moved, or reallocated while a pointer to it is '
                             'live |\n'
                             '| Concurrency | two threads reach the state in an order the code does not handle |\n'
                             '| Build vs runtime | the running binary is not the source being read -- stale build, '
                             'wrong library, cached artifact |\n'
                             '| Environment | a limit, permission, or configuration differs from the assumed one |\n'
                             '\n'
                             'For each hypothesis write: the claim in one sentence; the single observation that would '
                             '**refute** it and where to read it; and, if it is true, the fix in two words. Two '
                             'hypotheses with the same distinguishing observation are one hypothesis -- collapse them '
                             'and find a real third.\n'
                             '\n'
                             '## 3. Plan the debugger session, do not print\n'
                             '\n'
                             'Prefer a DAP debug adapter -- `lldb-dap`, `codelldb`, or a gdb adapter -- driven by the '
                             "executor's own debugging surface. It reads state without rebuilding, and it reads state "
                             'the source never printed.\n'
                             '\n'
                             'Print-and-rebuild is the fallback, for when no adapter is available or the fault only '
                             'appears in an environment that cannot host one. It is slower per iteration, it perturbs '
                             'timing (which can hide a race), and it can only show values someone already guessed were '
                             'interesting.\n'
                             '\n'
                             'The plan names, concretely:\n'
                             '\n'
                             '| Element | What to specify |\n'
                             '| --- | --- |\n'
                             '| Adapter and target | which adapter, which binary, launch or attach |\n'
                             '| Breakpoints | file:line or symbol, plus any condition that skips uninteresting hits |\n'
                             '| Watchpoints | the address or expression whose change is the event, for corruption '
                             'faults |\n'
                             '| Threads and frames | which thread, how far up the stack, what to read in each frame |\n'
                             '| Values to read | named variables, registers, or memory ranges -- decided in advance, '
                             'per stop |\n'
                             '| Stop criterion | what result ends the session, for each hypothesis |\n'
                             '\n'
                             'A plan that says "set a breakpoint and look around" hands the thinking back to the '
                             'executor. Name the reads.\n'
                             '\n'
                             '## 4. When symbols are missing\n'
                             '\n'
                             'A stripped binary changes the evidence available, not the method. The hypotheses and the '
                             'distinguishing observations still come first. What changes:\n'
                             '\n'
                             '- Identify the file format, architecture, and linkage before anything else; the answer '
                             'decides which tools apply at all.\n'
                             '- Recover coarse structure from imported symbols and embedded strings, and treat both as '
                             'hints rather than as a map.\n'
                             '- Prefer syscall- and library-level tracing for a first pass -- it shows what the binary '
                             'actually does without needing to know where.\n'
                             '- Note when platform protections block a technique, and say the technique was blocked '
                             'rather than reporting an empty result as a finding.\n'
                             '- Only attach to, trace, or modify a binary the user owns or operates. If provenance is '
                             'unclear, that is a blocker, not a detail.\n'
                             '\n'
                             '## 5. Evidence boundary\n'
                             '\n'
                             '| Claim | Evidence |\n'
                             '| --- | --- |\n'
                             '| The fault reproduces | an observed run showing the symptom, with the rate if '
                             'intermittent |\n'
                             '| The hypothesis is refuted | the observed value that contradicts it, quoted |\n'
                             '| The root cause is known | an observation that explains every part of the symptom, '
                             'including its timing |\n'
                             '| The fix works | the reproduction no longer produces the symptom **and** the mechanism '
                             'explains why |\n'
                             '\n'
                             'The last row is the one that gets skipped. A symptom that stopped appearing after an '
                             'edit, with no mechanism, is an open fault with a changed schedule -- record it as '
                             'unresolved.\n'
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
                  'source_path': 'skills/omh-native-debugging/references/native-debug-loop.md',
                  'source_sha256': '3ce0f29395b8a1c71074ce2808d6d2497bef1ccbecbba179b74950055435430d'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member native-debugging is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'people-ops',
  'family_id': 'people',
  'description': '[omh] Company hiring or HR process to structure: turn hiring and people context into a fair, '
                 'structured recruiting or people-operations brief. Use when the user says: recruiting plan, hiring '
                 'scorecard, interview scorecard, candidate debrief, 채용 계획, 면접 평가표, 후보자 비교.',
  'triggers': ['recruiting plan',
               'hiring scorecard',
               'interview scorecard',
               'candidate debrief',
               '채용 계획',
               '면접 평가표',
               '후보자 비교'],
  'category': 'operations',
  'phase': 'people-operations',
  'role': 'operator',
  'source_folder': 'omh-people-ops',
  'source_path': 'skills/omh-people-ops/SKILL.md',
  'source_sha256': 'd0bfa06fcf9f9c4fa9c1ecbec0b1e45f5097cbbdeefcac96cffd94dfe5184e18',
  'required_inputs': ['role or people-process outcome', 'available evidence', 'decision owner', 'policy constraints'],
  'expected_outputs': ['role/outcome and must-have versus trainable-criteria brief',
                       'structured interview scorecard and evidence-based debrief template',
                       'hiring-process, interviewer, and decision-owner plan',
                       'inclusion, privacy, policy, and missing-evidence flags with a next route'],
  'artifact_expectations': ['prepared people-operations brief when a wrapper captures it'],
  'acceptance_criteria': ['Confirm the workflow target, evidence boundary, and stop condition are named.',
                          'Report which outputs are prepared, observed, blocked, or missing.',
                          'Name the smallest next verification or handoff instead of claiming completion from '
                          'narration.'],
  'handoff_policy': 'Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work '
                    'routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, '
                    'filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a '
                    'connector, file, coding, or human-review handoff only when the user explicitly accepts that next '
                    'step; report it only from observed evidence. Hermes can prepare fair process guidance and '
                    'interview artifacts; it cannot claim a candidate was contacted, evaluated, hired, rejected, or '
                    'recorded in an HR system.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The request asks for a jurisdiction-specific employment-law conclusion, '
                    'policy compliance ruling, or contract interpretation; use `legal-compliance-review`.',
                    'Source routing exclusion: The user only needs a one-off job-ad, rejection, or interview-email '
                    'rewrite; use `content-operator`.',
                    'Source routing exclusion: The user asks to create ATS records, send invitations, book interviews, '
                    'change employment status, or modify HRIS settings; use `connector-operator` with explicit '
                    'authorization and observed results.',
                    'Source routing exclusion: The prompt asks the workflow to make an unsupported candidate decision '
                    'from protected characteristics or missing interview evidence; retain the process and evidence gap '
                    'instead.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['meeting-brief', 'operating-rhythm'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member people-ops is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'physical-device-readiness',
  'family_id': 'external-and-provider-readiness',
  'description': '[omh] Agent control of a robot, 3D printer, or IoT relay: gate robots, 3D printers, IoT relays, '
                 'sensors, and lab hardware before trials; use external-connector-readiness for provider or connector '
                 'adoption and toolbelt-readiness for missing control tools. Use when the user says: '
                 'physical-device-readiness, physical device readiness, device safety readiness, physical device '
                 'safety, hardware safety gate, 3d printer readiness, 3D printer safety, snapmaker printer safety.',
  'triggers': ['physical-device-readiness',
               'physical device readiness',
               'device safety readiness',
               'physical device safety',
               'hardware safety gate',
               '3d printer readiness',
               '3D printer safety',
               'snapmaker printer safety'],
  'category': 'operations',
  'phase': 'device-readiness',
  'role': 'operator',
  'source_folder': 'omh-physical-device-readiness',
  'source_path': 'skills/omh-physical-device-readiness/SKILL.md',
  'source_sha256': '44c42487019fb1b0a86cd29e4dbad485d8e29af603780bf0a9f3622a8be99dc0',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['physical_device_readiness_card/v1',
                       'device_safety_envelope/v1',
                       'hazard_and_actuator_inventory/v1',
                       'sensor_camera_gate_policy/v1',
                       'operator_approval_policy/v1',
                       'dry_run_and_simulation_policy/v1',
                       'emergency_stop_and_rollback_plan/v1',
                       'device_trial_manifest/v1 when observed',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['physical_device_readiness_card/v1 metadata-only wrapper card when prepared',
                            'device_safety_envelope/v1 with device, workspace, hazards, actuator classes, '
                            'human/property risk, owner, authority, and stop condition',
                            'hazard_and_actuator_inventory/v1 separating motion, heat, pressure, electrical, relay, '
                            'network, credential, and environmental risks',
                            'sensor_camera_gate_policy/v1 for camera/OCR, sensor telemetry, stale readings, manual '
                            'inspection, and blocked/no-camera fallback',
                            'operator_approval_policy/v1 with explicit human authority, confirmation moment, '
                            'disallowed autonomous actions, and emergency contact or stop owner',
                            'dry_run_and_simulation_policy/v1 for slicer/G-code dry-runs, command previews, mock '
                            'relays, simulated robot paths, and no-hardware trial mode',
                            'emergency_stop_and_rollback_plan/v1 with stop command, power/network isolation, recovery '
                            'boundary, and abort condition',
                            'device_trial_manifest/v1 only when real telemetry, camera capture id, dry-run output, '
                            'command transcript, operator confirmation, or hardware observation is recorded'],
  'acceptance_criteria': ['Device scope, actuator and hazard classes, sensor/camera gates, operator approval, dry-run '
                          'policy, emergency stop, and stop condition are explicit.',
                          'Physical actions, heat commands, relay toggles, robot movement, print starts, camera '
                          'inspections, and telemetry readings are marked observed, missing, risky, or not_observed.',
                          'Route external APIs or provider setup to external-connector-readiness, terminal commands to '
                          'command-operator, safety concerns to security-safety-review, visual/camera checks to '
                          'visual-qa, and missing tools to toolbelt-readiness.',
                          'Do not claim device movement, heat, print, relay, robot, camera, sensor, or emergency-stop '
                          'success without observed device-trial evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member physical-device-readiness is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'product-discovery-validation',
  'family_id': 'product-discovery',
  'description': '[omh] Unvalidated early product idea: test whether a customer problem, segment, and business '
                 'hypothesis deserve product investment, ending in kill, pivot, persevere, or inconclusive before any '
                 'PRD. Use when the user says: product-discovery-validation, product discovery validation, product '
                 'discovery, customer discovery, customer discovery plan, zero to one validation, validate the problem '
                 'before building, problem solution interview.',
  'triggers': ['product-discovery-validation',
               'product discovery validation',
               'product discovery',
               'customer discovery',
               'customer discovery plan',
               'zero to one validation',
               'validate the problem before building',
               'problem solution interview'],
  'category': 'planning',
  'phase': 'product-discovery-validation',
  'role': 'planner',
  'source_folder': 'omh-product-discovery-validation',
  'source_path': 'skills/omh-product-discovery-validation/SKILL.md',
  'source_sha256': '1ab833ce4b011d8dbdb17941fe1fc0b4e7c56d39e5aac399142e0bc000cf8ab1',
  'required_inputs': ['problem hypothesis',
                      'target segment',
                      'known evidence and current alternatives',
                      'decision owner',
                      'learning budget and deadline',
                      'success, failure, and stop criteria'],
  'expected_outputs': ['discovery_decision_frame/v1',
                       'discovery_evidence_ledger/v1',
                       'customer_discovery_plan/v1',
                       'assumption_test_portfolio/v1',
                       'discovery_decision_receipt/v1',
                       'initial_gtm_hypothesis/v1'],
  'artifact_expectations': ['prepared discovery decision frame, evidence ledger, customer discovery plan, assumption '
                            'test portfolio, decision receipt, and GTM hypothesis when a wrapper captures them'],
  'acceptance_criteria': ['Preserve workflow intent and stop conditions; load the full contract before claiming '
                          'completion.',
                          "Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply "
                          'language, tone, speech level, and sentence endings, progress updates included (where it '
                          'sets no language, use the one the user wrote in), and OMH shapes structure and content '
                          "only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) "
                          'stay in records and tool calls, never in the sentence the user reads unless they ask about '
                          'one; and when a stop condition or a decision the user owns ends the turn, offer the next '
                          'action as a question rather than declaring what will not be done.',
                          'Record observed delegation results; otherwise return `not_available` or `not_observed`.',
                          'Use Hermes-native subagent/delegation features when available: native subagents -> Hermes '
                          'delegation when available, otherwise sequential lanes.'],
  'handoff_policy': 'Keep decision framing, evidence classification, assumption ranking, test precommitment, and the '
                    'discovery decision in Hermes. A prepared plan, ledger, portfolio, or receipt is not participant '
                    'recruitment, an interview, a survey, a payment, a prototype, a PRD, code, or a launch. Prepare a '
                    '`product-brief` handoff only from a `persevere` receipt the decision owner accepted; route a '
                    'single empirical prototype question to `decision-prototype`; reach `idea-to-deploy` only after '
                    'the resulting product brief and plan are accepted.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['deep-interview', 'strategy-brief', 'research-brief'],
  'references': [{'relative_path': 'omh-product-discovery-validation/references/full-contract.md',
                  'content': '# Product Discovery Validation\n'
                             '\n'
                             'Load this on-demand contract after the compact `product-discovery-validation` body '
                             'identifies the\n'
                             'workflow. The main body owns routing signals, shared rules, the runtime\n'
                             'operation, delegation fallback, and completion/recovery pointers; this file\n'
                             'holds the workflow-specific detail without copying those shared rails.\n'
                             '\n'
                             '## Why This Exists\n'
                             '\n'
                             '`product-discovery-validation` gives an early idea a bounded, evidence-typed path to a '
                             'kill, pivot, persevere, or inconclusive decision so `product-brief` consumes validated '
                             'inputs instead of judging raw discovery itself.\n'
                             '\n'
                             '## Do Not Use When\n'
                             '\n'
                             '- The user needs market, competitor, pricing, or customer research on named sources '
                             'without a discovery decision to make; use `research-brief`.\n'
                             '- The user is clarifying their own request, requirements, or preferences rather than '
                             'testing a customer problem with external people; use `deep-interview`.\n'
                             '- The user needs a company or product strategy decision across existing options with '
                             'evidence already in hand; use `strategy-brief`.\n'
                             '- The problem, segment, and evidence are already validated and accepted and the user '
                             'wants a PRD or prioritization; use `product-brief`.\n'
                             '- An accepted product brief and plan exist and the user wants implementation, QA, and '
                             'release gates; use `idea-to-deploy`.\n'
                             '- The user has one falsifiable technical or empirical question a disposable prototype '
                             'can answer; use `decision-prototype`.\n'
                             '\n'
                             '## Examples\n'
                             '\n'
                             'Good example:\n'
                             '\n'
                             '- Prompt: I think freelance designers struggle to chase late invoices. Before we write a '
                             'PRD, help me test whether this is worth building.\n'
                             '- Expected behavior: Frame the decision and kill criteria, classify the existing '
                             'evidence, plan past-behavior customer interviews, rank the riskiest assumptions with '
                             'precommitted tests, and stop at an explicit kill, pivot, persevere, or inconclusive '
                             'receipt.\n'
                             '- Why: The request is a pre-PRD discovery decision about a customer problem and segment, '
                             'not research on named sources, requester clarification, or a PRD.\n'
                             '\n'
                             'Bad example:\n'
                             '\n'
                             '- Prompt: Write the PRD for our invoice-chasing feature; the interviews already '
                             'confirmed the problem.\n'
                             '- Expected behavior: Route to `product-brief` and ask for the accepted discovery receipt '
                             'or evidence rather than rerunning discovery.\n'
                             '- Why: Validated, accepted evidence with a PRD request belongs to the PRD owner, not to '
                             'discovery.\n'
                             '\n'
                             '## Completion Checklist\n'
                             '\n'
                             '- The problem gate state is recorded as validated, refuted, or inconclusive with the '
                             'external-human or behavioral-data refs that decided it, all observed in the framed '
                             'target segment.\n'
                             '- The target segment is explicit enough to recruit or tied to observed behavioral data '
                             'before any solution, PRD, prototype, or coding output leaves this workflow.\n'
                             '- Every assumption test in the portfolio carries its precommitted success, failure, '
                             'inconclusive, segment, deadline, cost, owner, and evidence re-entry fields.\n'
                             '- The receipt names kill, pivot, persevere, or inconclusive, preserves rejected paths, '
                             'and routes to `product-brief` only from an accepted persevere.\n'
                             '- Every artifact is reported as prepared; interviews, tests, and prototypes stay '
                             'not_observed until re-entered evidence exists.\n'
                             '\n'
                             '## Recovery Notes\n'
                             '\n'
                             '- If external-human or behavioral-data evidence is absent, hold the problem gate at '
                             'inconclusive and hand the customer discovery plan to a human owner instead of filling '
                             'the gap with personas.\n'
                             '- If a test passes its deadline or budget without meeting a precommitted condition, '
                             'record inconclusive with the residual risk and let the decision owner choose a new '
                             'budget or a kill.\n'
                             '- If the target segment is unknown, synthetic-only, or non-recruitable, keep the '
                             'discovery frame and customer discovery plan and report defining a recruitable or '
                             'behaviorally observed audience as the next evidence task.\n'
                             '- If a pivot changes the problem or segment, open a new decision frame and carry the '
                             'falsified hypotheses forward as rejected paths.\n'
                             '\n'
                             '## Use When\n'
                             '\n'
                             'Use when a founder or product owner brings an early idea and needs the problem, segment, '
                             'value proposition, and business hypothesis framed, evidence-typed, and tested to an '
                             'explicit discovery decision before a PRD, prototype, or delivery plan exists.\n'
                             '\n'
                             'Routing signals: `product-discovery-validation`, `product discovery validation`, '
                             '`product discovery`, `customer discovery`, `customer discovery plan`, `zero to one '
                             'validation`, `validate the problem before building`, `problem solution interview`, '
                             '`customer interview guide`, `riskiest assumption test`, `assumption test portfolio`, '
                             '`kill pivot persevere`, `kill or pivot decision`, `willingness to pay test`, `business '
                             'hypothesis validation`, `is this idea worth building`, `고객 발견 검증`, `가정 검증 테스트`, `킬 피벗 지속 '
                             '결정`\n'
                             '\n'
                             '## Workflow Contract\n'
                             '\n'
                             'Category: `planning`\n'
                             'Phase: `product-discovery-validation`\n'
                             'Hermes role: `planner`\n'
                             'Quality tier: `decision-gated`\n'
                             'Reasoning demand: `standard`\n'
                             '\n'
                             'Quality bar:\n'
                             '\n'
                             '- Separate the decision frame, typed evidence, customer re-entry plan, ranked '
                             'assumptions, and the receipt so each can be reviewed alone.\n'
                             '- Keep every kill, pivot, persevere, or inconclusive claim tied to precommitted criteria '
                             'and observed evidence.\n'
                             '\n'
                             'Handoff policy:\n'
                             '\n'
                             'Keep decision framing, evidence classification, assumption ranking, test precommitment, '
                             'and the discovery decision in Hermes. A prepared plan, ledger, portfolio, or receipt is '
                             'not participant recruitment, an interview, a survey, a payment, a prototype, a PRD, '
                             'code, or a launch. Prepare a `product-brief` handoff only from a `persevere` receipt the '
                             'decision owner accepted; route a single empirical prototype question to '
                             '`decision-prototype`; reach `idea-to-deploy` only after the resulting product brief and '
                             'plan are accepted.\n'
                             '\n'
                             'Required inputs:\n'
                             '\n'
                             '- problem hypothesis\n'
                             '- target segment\n'
                             '- known evidence and current alternatives\n'
                             '- decision owner\n'
                             '- learning budget and deadline\n'
                             '- success, failure, and stop criteria\n'
                             '\n'
                             'Expected outputs:\n'
                             '\n'
                             '- discovery_decision_frame/v1\n'
                             '- discovery_evidence_ledger/v1\n'
                             '- customer_discovery_plan/v1\n'
                             '- assumption_test_portfolio/v1\n'
                             '- discovery_decision_receipt/v1\n'
                             '- initial_gtm_hypothesis/v1\n'
                             '\n'
                             'Artifact expectations:\n'
                             '\n'
                             '- prepared discovery decision frame, evidence ledger, customer discovery plan, '
                             'assumption test portfolio, decision receipt, and GTM hypothesis when a wrapper captures '
                             'them\n'
                             '\n'
                             'Safety rules:\n'
                             '\n'
                             '- Do not recruit or contact participants, record interviews, run surveys, scrape '
                             'communities, buy ads, launch fake doors, accept payments, build a prototype, write a '
                             'PRD, write code, or deploy anything from this workflow.\n'
                             '- Synthetic personas, model-generated interview answers, secondary summaries, prototypes '
                             'without representative-user observation, and unsupported market-size figures cannot '
                             'satisfy a customer-validation gate.\n'
                             '- Interview praise, stated purchase intent, a waitlist signup, a finished prototype, or '
                             'one passed experiment is not product-market fit; state what each signal can and cannot '
                             'establish.\n'
                             '- Founder-market fit and strategic preference may inform the decision but never '
                             'substitute for target-customer evidence.\n'
                             '- An unknown, synthetic-only, or non-recruitable target segment blocks a solution, PRD, '
                             'prototype-as-validation, or coding handoff; discovery framing, the customer discovery '
                             'plan, and evidence work continue while it does.\n'
                             '\n'
                             'Detailed procedure steps: `references/procedure.md`.\n',
                  'source_path': 'skills/omh-product-discovery-validation/references/full-contract.md',
                  'source_sha256': 'ca33812bb36762cb7c1c17eaa80495cb51cff09b25fd37aa4570dbdee70dc41b'},
                 {'relative_path': 'omh-product-discovery-validation/references/procedure.md',
                  'content': '# product-discovery-validation Specialist Procedure\n'
                             '\n'
                             'Expert clarification questions:\n'
                             '- `problem hypothesis`\n'
                             '  - English: Which customer problem or opportunity do you believe exists, for whom, and '
                             'what would you expect to observe if it were false?\n'
                             '  - Korean: 어떤 고객 문제 또는 기회가 존재한다고 보시며, 누구에게 해당하고, 그 가설이 틀렸다면 무엇이 관찰될 것으로 예상하시나요?\n'
                             '- `target segment`\n'
                             '  - English: Which target segment, buyer versus user roles, and recruitable participant '
                             'criteria define who must show the problem, or is that audience still unknown?\n'
                             '  - Korean: 어떤 목표 세그먼트, 구매자와 사용자 구분, 모집 가능한 참여자 기준이 이 문제를 보여야 하는 대상을 정의하나요, 아니면 그 대상이 아직 '
                             '미정인가요?\n'
                             '- `known evidence and current alternatives`\n'
                             '  - English: Which evidence already exists, from which source class and date, and which '
                             'current alternatives or workarounds do those people use today?\n'
                             '  - Korean: 이미 확보된 근거는 무엇이고 출처 유형과 날짜는 어떠하며, 그 사람들이 지금 사용하는 대안이나 우회 방법은 무엇인가요?\n'
                             '- `decision owner`\n'
                             '  - English: Who owns the kill, pivot, persevere, or inconclusive decision, and who must '
                             'accept a handoff to a product brief?\n'
                             '  - Korean: 킬, 피벗, 지속, 미결 결정의 책임자는 누구이며, 제품 브리프로의 인계는 누가 승인해야 하나요?\n'
                             '- `learning budget and deadline`\n'
                             '  - English: What learning budget in time, money, and participant count applies, and by '
                             'which date must the decision be made?\n'
                             '  - Korean: 시간, 비용, 참여자 수 기준의 학습 예산은 얼마이며, 어느 날짜까지 결정을 내려야 하나요?\n'
                             '- `success, failure, and stop criteria`\n'
                             '  - English: Which observed conditions would count as success, failure, or a stop before '
                             'evidence is gathered?\n'
                             '  - Korean: 근거를 수집하기 전에 어떤 관찰 조건을 성공, 실패, 중단으로 간주할지 정해 두셨나요?\n'
                             '\n'
                             '## Procedure\n'
                             '\n'
                             'Declared checks:\n'
                             '- `discovery_decision_frame_check`\n'
                             '  - Required result fields: `problem_hypothesis`, `segment`, '
                             '`target_segment_definition`, `current_alternatives`, `decision`, `constraints`, `owner`, '
                             '`learning_budget`, `kill_criteria`, `disposition`\n'
                             '  - Criterion: PASS only when every frame field is supplied by the user or marked '
                             'unknown; HOLD when the decision, owner, learning budget, or kill criteria are missing, '
                             'and never infer them. Record `target_segment_definition` as recruitable, behaviorally '
                             'observed, unknown, synthetic-only, or non-recruitable; an unknown, synthetic-only, or '
                             'non-recruitable audience keeps discovery framing and evidence planning open while it '
                             'blocks solution work, and never invent a persona to close it.\n'
                             '- `discovery_evidence_class_check`\n'
                             '  - Required result fields: `source_class`, `safe_reference`, `observation_date`, '
                             '`segment`, `observation`, `direction`, `confidence_limits`, `unresolved_inconsistency`, '
                             '`pointer_status`\n'
                             '  - Criterion: Label every item as external-human, behavioral-data, '
                             'internal-stakeholder, secondary-research, synthetic, or inferred; record direction as '
                             'supporting or contradicting; assign no confidence from source class alone; keep a source '
                             'pointer a pointer, not a fresh observation.\n'
                             '- `discovery_customer_reentry_check`\n'
                             '  - Required result fields: `participant_criteria`, `interview_guide_focus`, '
                             '`consent_privacy_constraints`, `bias_controls`, `human_task_handoff`, '
                             '`evidence_reentry_contract`, `transcript_exclusion`\n'
                             '  - Criterion: The guide must ask about past behavior, current workarounds, switching '
                             'costs, and observed commitments, not praise or future intent; refuse simulated personas '
                             'or model-generated answers as participants; raw recordings, transcripts, and contact '
                             'data stay outside durable artifacts.\n'
                             '- `discovery_problem_gate_check`\n'
                             '  - Required result fields: `problem_gate_state`, `supporting_refs`, '
                             '`contradicting_refs`, `gate_reason`, `audience_gate`, `missing_audience_evidence`, '
                             '`solution_work_permitted`\n'
                             '  - Criterion: Set `problem_gate_state` to validated, refuted, or inconclusive from '
                             'external-human or behavioral-data entries only; the supporting entries must come from '
                             'the same target segment the frame names. `solution_work_permitted` is true only when the '
                             'gate is validated and `audience_gate` is defined, so refuted, inconclusive, or an '
                             'unknown, synthetic-only, or non-recruitable audience never advances to a solution, PRD, '
                             'prototype-as-validation, or coding handoff; name the missing audience evidence as the '
                             'next task instead.\n'
                             '- `discovery_assumption_precommit_check`\n'
                             '  - Required result fields: `assumption_category`, `decision_impact`, `evidence_gap`, '
                             '`rank`, `smallest_disconfirming_test`, `success_condition`, `failure_condition`, '
                             '`inconclusive_condition`, `segment_sample`, `deadline`, `cost`, `owner`, '
                             '`evidence_reentry`\n'
                             '  - Criterion: Rank each value, usability, feasibility, viability, go-to-market, or '
                             'ethics assumption by decision impact multiplied by evidence gap; every test must carry '
                             'precommitted success, failure, and inconclusive conditions plus segment, deadline, cost, '
                             'owner, and evidence re-entry before any observation is accepted.\n'
                             '- `discovery_decision_receipt_check`\n'
                             '  - Required result fields: `decision`, `precommitted_criteria`, `observed_evidence`, '
                             '`confidence_limits`, `rejected_paths`, `residual_risks`, `next_route`, '
                             '`promotion_guard`\n'
                             '  - Criterion: Decision must be kill, pivot, persevere, or inconclusive; missing '
                             'external evidence, a refuted problem, unresolved contradiction, an expired test, an '
                             'inconclusive result, or an audience that is unknown, synthetic-only, or non-recruitable '
                             'must not produce persevere or a `product-brief`, `decision-prototype`, or coding route; '
                             'rejected and falsified hypotheses are preserved, and no raw transcript is replayed.\n'
                             '- `discovery_gtm_hypothesis_check`\n'
                             '  - Required result fields: `beachhead_segment`, `buyer_user_distinction`, '
                             '`current_alternative`, `value_proposition`, `pricing_wtp_hypothesis`, `initial_channel`, '
                             '`first_cohort`, `learning_metrics`, `evidence_basis`\n'
                             '  - Criterion: Every field is a labeled hypothesis with its evidence basis; pricing, '
                             'willingness-to-pay, and market-size figures require an observed source or behavioral '
                             'evidence with explicit assumptions, and an unsupported field stays unknown instead of a '
                             'generic ratio.\n'
                             '\n'
                             '### `discovery_frame_decision` (analysis)\n'
                             '\n'
                             'Write the decision the discovery must inform, the problem hypothesis, segment, known '
                             'current alternatives, constraints, owner, learning budget, and kill criteria before '
                             'touching any evidence.\n'
                             '\n'
                             '- Input refs: `problem hypothesis`, `target segment`, `decision owner`, `learning budget '
                             'and deadline`, `success, failure, and stop criteria`\n'
                             '- Output refs: `discovery_decision_frame/v1`\n'
                             '- Check IDs: `discovery_decision_frame_check`\n'
                             '\n'
                             '### `discovery_classify_evidence` (analysis)\n'
                             '\n'
                             'Enter each supplied item with its source class, safe reference, date, segment, '
                             'observation, direction, and confidence limits; flag contradictions as unresolved '
                             'inconsistency rather than resolving them by preference.\n'
                             '\n'
                             '- Input refs: `known evidence and current alternatives`, `target segment`\n'
                             '- Output refs: `discovery_evidence_ledger/v1`\n'
                             '- Check IDs: `discovery_evidence_class_check`\n'
                             '\n'
                             '### `discovery_plan_customer_reentry` (production)\n'
                             '\n'
                             'Prepare participant criteria, a past-behavior interview guide, consent and privacy '
                             'constraints, bias controls, the human task that recruits and interviews, and the '
                             'contract for how bounded summaries re-enter the ledger; OMH contacts nobody.\n'
                             '\n'
                             '- Input refs: `target segment`, `known evidence and current alternatives`, `learning '
                             'budget and deadline`\n'
                             '- Output refs: `customer_discovery_plan/v1`\n'
                             '- Check IDs: `discovery_customer_reentry_check`\n'
                             '\n'
                             '### `discovery_gate_problem` (validation)\n'
                             '\n'
                             'Compare ledger entries against the precommitted criteria and record the problem gate as '
                             'validated, refuted, or inconclusive, admitting only entries observed in the framed '
                             'target segment; when it is not validated, or when the audience is unknown, '
                             'synthetic-only, or non-recruitable, stop solution and MVP work and name the customer or '
                             'audience evidence still missing.\n'
                             '\n'
                             '- Input refs: `problem hypothesis`, `known evidence and current alternatives`, `success, '
                             'failure, and stop criteria`\n'
                             '- Output refs: `discovery_decision_frame/v1`\n'
                             '- Check IDs: `discovery_evidence_class_check`, `discovery_problem_gate_check`\n'
                             '\n'
                             '### `discovery_rank_assumptions` (production)\n'
                             '\n'
                             'List the assumptions by category, score decision impact and evidence gap, and select for '
                             'each top-ranked assumption the cheapest disconfirming test that could change the '
                             'decision, with its precommitted conditions and bounded budget; a prototype is one '
                             'optional instrument routed to `decision-prototype`, never validation by itself.\n'
                             '\n'
                             '- Input refs: `problem hypothesis`, `target segment`, `known evidence and current '
                             'alternatives`, `decision owner`, `learning budget and deadline`, `success, failure, and '
                             'stop criteria`\n'
                             '- Output refs: `assumption_test_portfolio/v1`\n'
                             '- Check IDs: `discovery_assumption_precommit_check`\n'
                             '\n'
                             '### `discovery_draft_gtm_hypothesis` (production)\n'
                             '\n'
                             'Draft the beachhead segment, buyer versus user, current alternative, value proposition, '
                             'pricing or willingness-to-pay hypothesis, one initial channel, first cohort, and '
                             'learning metrics, each tied to its evidence basis or marked unknown.\n'
                             '\n'
                             '- Input refs: `problem hypothesis`, `target segment`, `known evidence and current '
                             'alternatives`\n'
                             '- Output refs: `initial_gtm_hypothesis/v1`\n'
                             '- Check IDs: `discovery_gtm_hypothesis_check`\n'
                             '\n'
                             '### `discovery_validate_decision_receipt` (validation)\n'
                             '\n'
                             'Record the decision against the precommitted criteria and observed evidence, with '
                             'confidence limits, rejected paths, residual risks, and the next route; a `persevere` '
                             'receipt hands `product-brief` the validated problem, segment, MVP learning boundary, '
                             'residual risks, and GTM hypotheses without transcript replay.\n'
                             '\n'
                             '- Input refs: `problem hypothesis`, `target segment`, `known evidence and current '
                             'alternatives`, `decision owner`, `learning budget and deadline`, `success, failure, and '
                             'stop criteria`\n'
                             '- Output refs: `discovery_decision_receipt/v1`\n'
                             '- Check IDs: `discovery_decision_frame_check`, `discovery_evidence_class_check`, '
                             '`discovery_customer_reentry_check`, `discovery_problem_gate_check`, '
                             '`discovery_assumption_precommit_check`, `discovery_decision_receipt_check`, '
                             '`discovery_gtm_hypothesis_check`\n',
                  'source_path': 'skills/omh-product-discovery-validation/references/procedure.md',
                  'source_sha256': 'c4b545ab2472299450aa8279f3d15a64afbfada6e14314f083d3f905aa52a19a'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member product-discovery-validation is absent; nearest local contracts '
                            'are explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'prompt-import-readiness',
  'family_id': 'external-and-provider-readiness',
  'description': '[omh] Importing prompt files for Hermes: prompt import readiness - review and normalize external '
                 'CLI-agent prompt files before offering slash-command candidates; use external-connector-readiness '
                 'for plugin or API adoption and toolbelt-readiness for missing runtime capabilities. Use when the '
                 'user says: prompt-import-readiness, prompt import readiness, slash prompt import, slash prompts '
                 'import, slash command prompt import, prompt library import, prompt folder import, prompt directory '
                 'import.',
  'triggers': ['prompt-import-readiness',
               'prompt import readiness',
               'slash prompt import',
               'slash prompts import',
               'slash command prompt import',
               'prompt library import',
               'prompt folder import',
               'prompt directory import'],
  'category': 'prompt',
  'phase': 'prompt-import-readiness',
  'role': 'guide',
  'source_folder': 'omh-prompt-import-readiness',
  'source_path': 'skills/omh-prompt-import-readiness/SKILL.md',
  'source_sha256': 'bf93aea9e50cfd8abc0b24809f00540786039e375935b404c1f0070b8253229d',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['prompt_import_readiness_card/v1',
                       'prompt_compatibility_audit/v1 for explicitly named local files',
                       'prompt_source_inventory/v1',
                       'prompt_format_matrix/v1',
                       'argument_interpolation_policy/v1',
                       'slash_command_collision_report/v1',
                       'prompt_trust_review/v1',
                       'prompt_import_manifest/v1 when observed',
                       'next action',
                       'prepared-vs-observed boundary'],
  'artifact_expectations': ['prompt_import_readiness_card/v1 metadata-only wrapper card when prepared',
                            'prompt_compatibility_audit/v1 with bounded source metadata, format classification, '
                            'argument syntax, collisions, and review reasons for explicitly named local files',
                            'prompt_source_inventory/v1 with source directory, agent family, file count, format claim, '
                            'and review state',
                            'prompt_format_matrix/v1 separating YAML frontmatter, TOML frontmatter, raw markdown/text, '
                            'and unsupported formats',
                            'argument_interpolation_policy/v1 for $ARGUMENTS, $1-$9, {{args}}, named placeholders, '
                            'escaping, and missing argument handling',
                            'slash_command_collision_report/v1 with command names, aliases, existing Hermes commands, '
                            'and conflict resolution policy',
                            'prompt_trust_review/v1 with source trust, prompt-injection risk, secret leakage risk, '
                            'license/source notes, and review owner',
                            'prompt_import_manifest/v1 only when file reads, parsed prompts, generated slash-command '
                            'candidates, or dry-run output are observed'],
  'acceptance_criteria': ['Prompt sources, agent family, expected file formats, argument syntax, slash-command names, '
                          'trust level, and stop condition are explicit.',
                          'Explicit-path audit reads and compatibility results are observed only in their audit '
                          'output; source discovery, command registration, prompt mutation, slash-command activation, '
                          'and dry-run execution remain marked not_observed.',
                          'Route broad candidate discovery to skill-scout, prompt/tool safety to '
                          'security-safety-review, missing CLIs or directories to toolbelt-readiness, and approved '
                          'implementation to a selected executor handoff.',
                          'Imported prompts, generated command files, registry updates, and dry-run results are '
                          'reported only from observed prompt-import evidence.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member prompt-import-readiness is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'provider-profile-posture',
  'family_id': 'external-and-provider-readiness',
  'description': '[omh] Provider credentials without exposure: prepare provider-profile metadata without reading '
                 'secrets or calling providers. Use when the user says: provider-profile-posture, provider profile '
                 'posture, provider profile readiness, secret presence confirmation, connector profile posture, 공급자 '
                 '프로필 상태, 시크릿 존재 확인, 커넥터 준비 상태.',
  'triggers': ['provider-profile-posture',
               'provider profile posture',
               'provider profile readiness',
               'secret presence confirmation',
               'connector profile posture',
               '공급자 프로필 상태',
               '시크릿 존재 확인',
               '커넥터 준비 상태'],
  'category': 'operations',
  'phase': 'provider-profile-posture',
  'role': 'operator',
  'source_folder': 'omh-provider-profile-posture',
  'source_path': 'skills/omh-provider-profile-posture/SKILL.md',
  'source_sha256': '155e9a6d64c0fb80d10c373c73d30428455de83ede5896c34b20fd13a240ef01',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['provider_profile_posture/v1',
                       'metadata-only secret requirements',
                       'allowed and prohibited actions'],
  'artifact_expectations': ['provider_profile_posture/v1 metadata-only preparation record'],
  'acceptance_criteria': ['Provider ID, profile ID, requested capabilities, and secret-presence metadata are explicit.',
                          'No secret value, credential validation, provider call, model route, wallet, or payment '
                          'action is claimed.',
                          'Any host observation reference remains supplied metadata, not a live connector check.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['toolbelt-readiness'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member provider-profile-posture is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'refactor-plan',
  'family_id': 'behavior-preserving-refactor',
  'description': '[omh] Decided cross-module refactor to phase: refactor planning - turn a decided boundary-changing '
                 'refactor into a phased plan - reconnaissance, contracts-first phase order, per-phase verification '
                 'and rollback, a files table, and an explicit approval gate before any edit. Use when the user says: '
                 'refactor-plan, refactor plan, plan this refactor, plan the refactor, refactor planning, refactor '
                 'phases, phased refactor, refactor in phases.',
  'triggers': ['refactor-plan',
               'refactor plan',
               'plan this refactor',
               'plan the refactor',
               'refactor planning',
               'refactor phases',
               'phased refactor',
               'refactor in phases'],
  'category': 'planning',
  'phase': 'refactor-plan',
  'role': 'planner',
  'source_folder': 'omh-refactor-plan',
  'source_path': 'skills/omh-refactor-plan/SKILL.md',
  'source_sha256': '205d3ecac0b4101b105d69ba0b33e80c2ee5fa120de7982ba98b6f58686014b7',
  'required_inputs': ['the decided target shape (what moves where), or a pointer to the accepted plan that decided it',
                      'the affected-file evidence: import graph, codegraph handoff, or an observed file inventory',
                      'the regression gates that exist today (test suite, typecheck, generated-artifact checks)'],
  'expected_outputs': ['reconnaissance: affected files, ownership boundaries, hidden coupling, blast radius — and for '
                       'an upgrade, the advisory, licence, migration-guide, and lockfile intake',
                       'phase plan in the fixed order - types/interfaces, implementations, callers, tests, cleanup - '
                       'each with verification and rollback',
                       'files table: path, action, phase, blocks/blocked-by',
                       'for an upgrade, the call-site readiness gate: every breaking change between the two versions '
                       "against this repository's call sites or an observed empty search, and every stage's rollback",
                       "the approval gate: the plan stops and waits for the user's go"],
  'artifact_expectations': ['metadata-only runtime record when a wrapper or shell is available'],
  'acceptance_criteria': ['Reconnaissance names affected files, boundaries, coupling, and blast radius from observed '
                          'evidence.',
                          'Every phase carries its verification command and its rollback point, and ends at a '
                          'shippable commit.',
                          'The files table covers every touched file with action, phase, and dependencies.',
                          'For an upgrade, every breaking change row names its call sites or an observed empty search, '
                          'and every stage names its rollback.',
                          "The plan stopped at the approval gate; no implementation began without the user's go."],
  'handoff_policy': 'Hermes owns reconnaissance and the phased plan; implementation of any approved phase is coding '
                    'work for the selected executor lane under its own evidence rules. An approved plan is approval of '
                    'the order, not evidence any phase ran.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    "Source routing exclusion: The refactor's direction is still contested or the goal itself needs "
                    'consensus planning; use `ralplan`.',
                    'Source routing exclusion: The work is deletion-first cleanup with no boundary changes; use '
                    '`ai-slop-cleaner`.',
                    'Source routing exclusion: The plan is done and the claim is that work is complete; use '
                    '`verification-gate` for the evidence close.',
                    'Source routing exclusion: The version bump carries a security advisory, a CVE, or a leaked '
                    'secret; use `security-event-response`, which owns containment and closure.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ai-slop-cleaner', 'code-review', 'ralplan'],
  'references': [{'relative_path': 'omh-refactor-plan/references/dependency-upgrade.md',
                  'content': '# Dependency and Framework Upgrades\n'
                             '\n'
                             'A major upgrade is a boundary-changing refactor whose direction was decided by\n'
                             'somebody else. The phase contract in `references/refactor-phases.md` carries\n'
                             'the execution shape unchanged - reconnaissance, contracts-first order,\n'
                             'per-phase verification and rollback, the files table, the approval gate. Four\n'
                             'things are specific to an upgrade, and all four are read before the first\n'
                             'phase is ordered.\n'
                             '\n'
                             '## 1. Advisory intake\n'
                             '\n'
                             'Establish why the upgrade is happening, because it sets the deadline and the\n'
                             'acceptable risk:\n'
                             '\n'
                             '- Which advisories or CVEs the current version carries, with their identifiers\n'
                             '  and severity, and whether a patch release fixes them without the major jump.\n'
                             '- Whether the current version is still supported upstream, and the end-of-life\n'
                             '  date if one is published.\n'
                             '- Whether any advisory is reachable from this codebase. An advisory in a code\n'
                             '  path nothing calls is a different deadline from one in the request handler,\n'
                             '  and saying which is a finding, not a detail.\n'
                             '\n'
                             'A security-driven upgrade and a housekeeping upgrade produce different phase\n'
                             'plans: the first may ship the version bump alone and defer the API migration,\n'
                             'which is a legitimate split; the second has no reason to.\n'
                             '\n'
                             '## 2. License delta\n'
                             '\n'
                             'The new version may not carry the old licence. Read the licence file at the\n'
                             'target version rather than the package metadata, which lags. Record the\n'
                             'before and after, and flag a change from permissive to copyleft, a change to a\n'
                             'source-available or dual licence, and any new attribution requirement, as a\n'
                             "blocker for the user's decision rather than a note in the plan. The same\n"
                             'applies to transitive dependencies the upgrade adds - a new direct dependency\n'
                             'is visible in the diff, a new transitive one is visible only in the lockfile.\n'
                             '\n'
                             '## 3. The upstream migration guide is an input, not a summary\n'
                             '\n'
                             'Read the upstream migration guide and the changelog between the two versions,\n'
                             'and record for each breaking change: the upstream item, whether this codebase\n'
                             'is affected, and which phase handles it. A breaking change nobody checked is\n'
                             'not "probably fine", and a guide that does not mention something this codebase\n'
                             'does is a gap to record, not silence to interpret.\n'
                             '\n'
                             'Two things the guide will not tell you and the reconnaissance must: deprecated\n'
                             'APIs this codebase uses that still work in the target version - they are the\n'
                             "next upgrade's breaking changes - and behaviour changes that are not API\n"
                             'changes, such as a different default, a changed error type, or a changed\n'
                             'ordering guarantee. Those pass the typechecker and fail in production.\n'
                             '\n'
                             '## 4. Lockfile discipline\n'
                             '\n'
                             'The lockfile is the artifact the upgrade actually produces.\n'
                             '\n'
                             '- The lockfile changes in the same commit as the manifest. A manifest bump\n'
                             '  without its lockfile is a change nobody can reproduce.\n'
                             "- Regenerate it with the project's own tooling and version; a lockfile written\n"
                             '  by a different package-manager version reorders or reshapes entries and\n'
                             '  buries the real delta.\n'
                             '- Review the transitive delta, not only the direct one: read what was added,\n'
                             '  removed, and moved, and pair each unexpected addition with the direct\n'
                             '  dependency that pulled it in.\n'
                             '- Never hand-edit a lockfile to force a version. Constrain it in the manifest\n'
                             '  and regenerate, or the next regeneration silently undoes it.\n'
                             '- A monorepo with several lockfiles upgrades them together or states which are\n'
                             '  deliberately pinned behind and why.\n'
                             '\n'
                             '## 5. Call-site readiness gate\n'
                             '\n'
                             '"Safe to merge" for a bump - including one a bot opened - is a verdict over\n'
                             'this table, not a reading of the changelog. One row per breaking change\n'
                             'between the two versions:\n'
                             '\n'
                             '| Breaking change | Call sites in this repo | Stage | Rollback |\n'
                             '| --- | --- | --- | --- |\n'
                             '| upstream item, quoted | `path:line` per site, or the search run and its observed empty '
                             'result | which stage handles it | how that stage is undone |\n'
                             '\n'
                             'The plan is not ready, and the bump is not safe to merge, while any row has\n'
                             'an empty call-site cell or an empty rollback cell. A search that was prepared\n'
                             'but not run is an empty cell. An empty call-site list is a finding only when\n'
                             'the search that produced it is named, because an unrun search and a clean one\n'
                             'look the same in a summary.\n'
                             '\n'
                             '## Phase order for an upgrade\n'
                             '\n'
                             'The contracts-first order still holds, read for this shape. Each stage states\n'
                             'its own rollback:\n'
                             '\n'
                             '| Stage | What it does | Rollback |\n'
                             '| --- | --- | --- |\n'
                             '| Prepare | compatibility shims and adapters that work on both versions | revert the '
                             'shim commits; the old version still runs |\n'
                             '| Bump | manifest and lockfile together, ending green on their own | revert two files |\n'
                             '| Adapt | call sites move off the removed APIs, in reviewable groups | revert the group; '
                             'the shims still cover it |\n'
                             '| Remove shims | cleanup, from a tagged rollback point | return to the tag |\n'
                             '\n'
                             'Shims that run on both versions go first, so the bump stays a two-file revert\n'
                             'and every call site is covered while the adapt stage lands.\n'
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'Advisory identifiers, licence text, and changelog entries are read from what\n'
                             'the user or the repository supplies; OMH fetches nothing. An upgrade plan is\n'
                             'not an applied upgrade, a passing suite, or evidence that the advisory is\n'
                             'resolved - the regenerated lockfile and a green run are separate observed\n'
                             'evidence.\n',
                  'source_path': 'skills/omh-refactor-plan/references/dependency-upgrade.md',
                  'source_sha256': '97e9b74b117a66171386a0015a0ad60954def8dcf59b1d6c180037919c61bfbf'},
                 {'relative_path': 'omh-refactor-plan/references/refactor-phases.md',
                  'content': '# Refactor Phases\n'
                             '\n'
                             'The phase contract for a boundary-changing refactor whose direction is already\n'
                             'decided. The plan is the deliverable; implementation starts only after the\n'
                             'user approves it, phase by phase if they choose.\n'
                             '\n'
                             '## Reconnaissance before phases\n'
                             '\n'
                             'Map the territory before ordering the work:\n'
                             '\n'
                             '- **Affected files** - every file the change touches, from the actual import\n'
                             '  graph (a codegraph handoff is the prepared input when available), not from\n'
                             "  memory. Each file enters the plan's table as modify, create, or delete.\n"
                             '- **Ownership boundaries** - which modules own the symbols that move, and who\n'
                             '  else imports them. A consumer outside the mapped set found later is a plan\n'
                             '  defect, not a surprise.\n'
                             '- **Hidden coupling** - shared mutable state, import cycles, reflection or\n'
                             '  string-keyed lookups, test fixtures that reach into internals. Each one is\n'
                             '  named in the plan with the phase that unwinds it.\n'
                             '- **Blast radius** - the observable surfaces that could change if a phase goes\n'
                             '  wrong: public APIs, CLI output, generated artifacts, persisted schemas.\n'
                             '  The radius decides the verification depth, not optimism.\n'
                             '\n'
                             '## The phase order\n'
                             '\n'
                             'Contracts precede implementations, implementations precede callers, callers\n'
                             'precede tests, tests precede cleanup:\n'
                             '\n'
                             '1. **Types and interfaces** - introduce the target contracts beside the old\n'
                             '   ones; nothing calls them yet. Verification: the build and typecheck gate.\n'
                             '   Rollback: delete the additions.\n'
                             '2. **Implementations** - fill the new contracts, old paths still live.\n'
                             '   Verification: new-path unit tests plus the untouched existing suite.\n'
                             '   Rollback: revert this phase alone; callers never moved.\n'
                             '3. **Callers** - move call sites in reviewable groups; both paths stay green\n'
                             '   until the last group lands. Verification: the full suite per group.\n'
                             '   Rollback: revert the group, not the phase.\n'
                             '4. **Tests** - retarget tests that asserted the old shape; add the boundary\n'
                             '   locks the new shape needs. Verification: the full suite, plus a check that\n'
                             '   coverage did not silently narrow.\n'
                             '5. **Cleanup** - delete the old contracts and their shims; this is the first\n'
                             '   phase that removes anything. Verification: the full suite plus a dead-code\n'
                             '   sweep. Rollback: restore from the tag cut before cleanup.\n'
                             '\n'
                             'Every phase ends at a commit that could ship. A phase that cannot end green\n'
                             'is split further or its plan is wrong.\n'
                             '\n'
                             "## The plan's table\n"
                             '\n'
                             'One row per file: path, action (modify/create/delete), phase, blocks /\n'
                             'blocked-by. A row without a phase is unplanned work; a phase without rollback\n'
                             'is a bet, not a plan.\n'
                             '\n'
                             '## The approval gate\n'
                             '\n'
                             'The plan stops here. State the phases, the table, the blast radius, and the\n'
                             "per-phase verification, then wait for the user's go - whole plan or first\n"
                             'phase. Implementation, however approved, is executor work under the coding\n'
                             "lane's own evidence rules.\n"
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'A refactor plan is prepared context: it is not implementation, migration,\n'
                             'verification, review, CI, or merge evidence, and an approved plan does not\n'
                             "make its phases' verification claims true in advance.\n",
                  'source_path': 'skills/omh-refactor-plan/references/refactor-phases.md',
                  'source_sha256': '492cfcd81b1b44ffb54bcb16b6dc319549a7ee868d95b21176fa9cc0fa06f035'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member refactor-plan is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'rules-distill',
  'family_id': 'rule-candidates',
  'description': '[omh] Turn repeated lessons into written rules: extract repeated principles from skills, prompts, '
                 'traces, reviews, and failures into reviewed rule candidates without auto-mutating guidance. Use when '
                 'the user says: rules-distill, rules distill, distill rules, rule distillation, principle distill, '
                 'skill principles, extract agent rules, turn traces into rules.',
  'triggers': ['rules-distill',
               'rules distill',
               'distill rules',
               'rule distillation',
               'principle distill',
               'skill principles',
               'extract agent rules',
               'turn traces into rules'],
  'category': 'knowledge',
  'phase': 'rules-distillation',
  'role': 'memory-keeper',
  'source_folder': 'omh-rules-distill',
  'source_path': 'skills/omh-rules-distill/SKILL.md',
  'source_sha256': '71e259d34ecffd67e10898e07e65921e4ef8caec8ca1983463dcdbdd54db37d8',
  'required_inputs': ['source corpus: skills, prompts, traces, reviews, failures, or docs',
                      'destination boundary: AGENTS, skill catalog, prompt, docs, memory, or no-write review',
                      'rule granularity and acceptance criteria',
                      'reviewer or approval requirement'],
  'expected_outputs': ['rules_distillation_plan/v1',
                       'principle_candidate_set/v1',
                       'duplication_conflict_report/v1',
                       'review_queue/v1',
                       'approved_patch_handoff/v1 when approved',
                       'not-evidence boundary'],
  'artifact_expectations': ['principle_candidate_set/v1 with source references, repeated pattern, candidate wording, '
                            'scope, non-goals, and risk',
                            'duplication_conflict_report/v1 with already-covered rules, conflicts, and stale guidance',
                            'review_queue/v1 separating proposed, approved, rejected, deferred, and needs-evidence '
                            'candidates'],
  'acceptance_criteria': ['The durable fact, source evidence, retrieval hint, and staleness risk are recorded.',
                          'Uncertain or conflicting knowledge is marked as review-needed rather than permanent truth.',
                          'Separate coding or docs tasks are extracted instead of buried in notes.'],
  'handoff_policy': 'Keep principle extraction and candidate review in Hermes. Editing AGENTS.md, catalog data, '
                    'prompts, skills, or docs requires explicit approved implementation work and verification.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The user wants a single workflow route regression; use '
                    '`workflow-learning`.',
                    'Source routing exclusion: The user wants durable factual project memory; use `wiki` or memory '
                    'curation.',
                    'Source routing exclusion: The user already approved a concrete code/doc change; use the '
                    'implementation workflow.',
                    'Source routing exclusion: The ask is writing or keeping current the file an agent reads at '
                    'startup -- AGENTS.md, CLAUDE.md, a Cursor rule; use `agent-instructions`, which updates only its '
                    'marked region.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['workflow-learning'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member rules-distill is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'run-efficiency',
  'family_id': 'context-and-efficiency',
  'description': '[omh] Run efficiency and context usage report: report supplied local run efficiency while provider '
                 'and host data stay unobserved. Use when the user says: run-efficiency, run efficiency report, local '
                 'run efficiency, context utilization, tool duration report, 실행 효율 리포트, 컨텍스트 사용량, 도구 지연 시간.',
  'triggers': ['run-efficiency',
               'run efficiency report',
               'local run efficiency',
               'context utilization',
               'tool duration report',
               '실행 효율 리포트',
               '컨텍스트 사용량',
               '도구 지연 시간'],
  'category': 'observability',
  'phase': 'run-efficiency',
  'role': 'tracker',
  'source_folder': 'omh-run-efficiency',
  'source_path': 'skills/omh-run-efficiency/SKILL.md',
  'source_sha256': '55d3f2ea146cfc156cf89841d0bc092bb6818ebaa388bdae32ec2fcb5003851d',
  'required_inputs': ['user request', 'target context', 'delivery or status expectation', 'known missing evidence'],
  'expected_outputs': ['run_efficiency_report/v1', 'context utilization', 'not_observed provider and host gaps'],
  'artifact_expectations': ['run_efficiency_report/v1 metadata-only report',
                            'supplied `session_activity_receipt/v1` when available; unavailable metrics stay '
                            'unavailable, never zero'],
  'acceptance_criteria': ['The run ID, context budget, surfaces, and supplied observations are explicit.',
                          'Provider billing, cron, and host claims remain not_observed unless separately recorded.',
                          'The report does not intercept, route, or execute provider or host work.'],
  'handoff_policy': 'Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or '
                    'host-runtime handoff only when the user accepts that next step and observed evidence can be '
                    'recorded.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Source routing exclusion: The request is already handled by a narrower explicit skill with '
                    'stronger evidence.',
                    'Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, '
                    'schedulers, file exports, or runtime agents.',
                    'Source routing exclusion: The only safe answer is to ask for missing authority, credentials, '
                    'target, or observed evidence first.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ops-observability-card', 'agent-ops-review'],
  'references': [],
  'source_gaps': ['The pinned upstream member declares no physical method reference; its SKILL.md source contract '
                  'remains authoritative.'],
  'blocked_prerequisites': ['The local catalog member run-efficiency is absent; nearest local contracts are explicitly '
                            'non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'sales-pipeline-review',
  'family_id': 'sales-pipeline',
  'description': '[omh] CRM pipeline or sales forecast to review: turn a supplied CRM export or pipeline snapshot into '
                 'an evidence-bound pipeline health, forecast, and follow-up review. Aliases: pipeline-review, '
                 'forecast-review, deal-review. Use when the user says: sales-pipeline-review, sales pipeline review, '
                 'pipeline review, pipeline health, pipeline coverage, deal review, deal health, sales forecast '
                 'review.',
  'triggers': ['sales-pipeline-review',
               'sales pipeline review',
               'pipeline review',
               'pipeline health',
               'pipeline coverage',
               'deal review',
               'deal health',
               'sales forecast review'],
  'category': 'operations',
  'phase': 'sales-pipeline-review',
  'role': 'operator',
  'source_folder': 'omh-sales-pipeline-review',
  'source_path': 'skills/omh-sales-pipeline-review/SKILL.md',
  'source_sha256': '772914984077a1ec970a012400622515dd303488a5a4c280a53b18f59c33afff',
  'required_inputs': ['pipeline snapshot',
                      'as-of time and review horizon',
                      'currency, amount, stage, and forecast definitions',
                      'prior forecast and actuals',
                      'decision owner'],
  'expected_outputs': ['sales_pipeline_scope/v1',
                       'sales_pipeline_health/v1',
                       'sales_forecast_assessment/v1',
                       'sales_outcome_learning_annex/v1',
                       'sales_renewal_risk_annex/v1',
                       'sales_pipeline_handoff/v1'],
  'artifact_expectations': ['prepared sales pipeline review brief when a wrapper captures it',
                            'durable artifacts hold bounded aggregates, opaque source references, and only the account '
                            'identifiers an approved handoff needs; raw export rows and message content are not '
                            'persisted by default'],
  'acceptance_criteria': ['Preserve workflow intent and stop conditions; load the full contract before claiming '
                          'completion.',
                          "Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply "
                          'language, tone, speech level, and sentence endings, progress updates included (where it '
                          'sets no language, use the one the user wrote in), and OMH shapes structure and content '
                          "only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) "
                          'stay in records and tool calls, never in the sentence the user reads unless they ask about '
                          'one; and when a stop condition or a decision the user owns ends the turn, offer the next '
                          'action as a question rather than declaring what will not be done.',
                          'Record observed delegation results; otherwise return `not_available` or `not_observed`.',
                          'Use Hermes-native subagent/delegation features when available: native subagents -> Hermes '
                          'delegation when available, otherwise sequential lanes.'],
  'handoff_policy': 'Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work '
                    'routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, '
                    'filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a '
                    'connector, file, coding, or human-review handoff only when the user explicitly accepts that next '
                    'step; report it only from observed evidence. Hermes reviews supplied records; it does not replace '
                    'a CRM, store or sync CRM data, mutate opportunities, create dashboards or alerts, send outreach, '
                    'book revenue, or claim seller or buyer commitments that were not observed.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ops-review', 'report-package'],
  'references': [{'relative_path': 'omh-sales-pipeline-review/references/full-contract.md',
                  'content': '# Sales Pipeline Review\n'
                             '\n'
                             'Load this on-demand contract after the compact `sales-pipeline-review` body identifies '
                             'the\n'
                             'workflow. The main body owns routing signals, shared rules, the runtime\n'
                             'operation, delegation fallback, and completion/recovery pointers; this file\n'
                             'holds the workflow-specific detail without copying those shared rails.\n'
                             '\n'
                             '## Why This Exists\n'
                             '\n'
                             '`sales-pipeline-review` prepares evidence-bounded portfolio pipeline, forecast, and '
                             'follow-up reviews from supplied CRM snapshots without replacing a CRM, mutating records, '
                             'or claiming revenue.\n'
                             '\n'
                             '## Do Not Use When\n'
                             '\n'
                             '- The request is single-account discovery, qualification, buyer hypotheses, outreach '
                             "drafting, or one opportunity's next step; use `sales-development`.\n"
                             '- The user wants a weekly status, release-risk, or operating review with no sales '
                             'stages, forecast categories, or deal records; use `ops-review`.\n'
                             '- The user needs authoritative revenue, bookings, budget-variance, or close reporting '
                             'rather than a pipeline scenario; use `finance-analysis`.\n'
                             '- The user wants generic exploration or calculation on a supplied table with no stage, '
                             'forecast, or deal-health semantics; use `data-analysis`.\n'
                             '- The supplied material is qualitative customer feedback, call notes, or survey text '
                             'rather than opportunity records; use `feedback-triage`.\n'
                             '- The user asks to update Salesforce or HubSpot, store or sync CRM data, send alerts or '
                             'outreach, or change an opportunity; use `connector-operator` with explicit object, '
                             'field, and authority.\n'
                             '\n'
                             '## Examples\n'
                             '\n'
                             'Good example:\n'
                             '\n'
                             "- Prompt: Here is this week's pipeline export as of Monday 09:00; review deal health, "
                             "slipped close dates, and whether the commit forecast holds up against last quarter's "
                             'calls.\n'
                             '- Expected behavior: Validate as-of time, currency, amount and stage semantics first, '
                             'then prepare health, forecast-state, and calibration findings with owned follow-ups and '
                             'proposed CRM corrections.\n'
                             '- Why: The request is portfolio-level pipeline and forecast review over a supplied '
                             'snapshot with a stated as-of time.\n'
                             '\n'
                             'Bad example:\n'
                             '\n'
                             '- Prompt: Write discovery questions for the Northwind opportunity and draft the '
                             'follow-up email.\n'
                             '- Expected behavior: Route to `sales-development`, not `sales-pipeline-review`.\n'
                             "- Why: A single account's discovery, qualification, and outreach draft has no portfolio, "
                             'aging, or forecast-calibration objective.\n'
                             '\n'
                             '## Completion Checklist\n'
                             '\n'
                             '- The scope disposition is recorded before any figure: `HOLD` names the blocking gap, '
                             'otherwise freshness, currency basis, amount and stage semantics, duplicates, and owners '
                             'are confirmed from supplied data.\n'
                             '- Health, forecast, and annex outputs cite supplied record references, keep stage, '
                             'seller forecast, scenario, and observed commitment separate, and mark calibration or an '
                             'annex `unavailable` or `unsupported` instead of filling it.\n'
                             '- The handoff lists owner, due date, exit criterion, and evidence per follow-up, keeps '
                             'every CRM correction proposed with an approval state, and reports mutation, storage, '
                             'sync, alerts, and outreach as `not_observed` unless a connector result was observed.\n'
                             '\n'
                             '## Recovery Notes\n'
                             '\n'
                             '- If the snapshot fails scope validation, return `HOLD` naming the exact missing '
                             'definition, conversion basis, owner, or duplicate set and ask for it; do not rank or '
                             'total partial data.\n'
                             '- If prior forecasts or outcomes are absent, keep calibration `unavailable`; if an annex '
                             'has no supporting evidence, emit it as `unsupported` with the gap named rather than '
                             'omitting it.\n'
                             '- If a connector is unavailable, keep every CRM correction proposed and every alert or '
                             'message unsent, and name the connector boundary as the next observable step.\n'
                             '\n'
                             '## Use When\n'
                             '\n'
                             'Use when a sales leader or business owner supplies a bounded CRM export or pipeline '
                             'snapshot and needs recurring portfolio review: evidence scope and freshness, stage and '
                             'forecast definitions, movement and aging, stale or slipped deals, exit-criteria gaps, '
                             'next-step quality, concentration, forecast scenarios and prior-forecast calibration, '
                             'optional won/lost or renewal-risk learning, and an owned follow-up handoff.\n'
                             '\n'
                             'Routing signals: `sales-pipeline-review`, `sales pipeline review`, `pipeline review`, '
                             '`pipeline health`, `pipeline coverage`, `deal review`, `deal health`, `sales forecast '
                             'review`, `forecast call`, `forecast calibration`, `seller forecast`, `stale deals`, '
                             '`slipped deals`, `renewal risk review`, `win loss review`, `파이프라인 리뷰`, `영업 예측 보정`, `딜 '
                             '리뷰`\n'
                             '\n'
                             '## Workflow Contract\n'
                             '\n'
                             'Category: `operations`\n'
                             'Phase: `sales-pipeline-review`\n'
                             'Hermes role: `operator`\n'
                             'Quality tier: `decision-gated`\n'
                             'Reasoning demand: `standard`\n'
                             '\n'
                             'Quality bar:\n'
                             '\n'
                             '- Separate stage, seller forecast, model-derived scenario, and observed buyer commitment '
                             'in every forecast statement.\n'
                             '- Cite the supplied record reference behind every exception, slip, stall, concentration, '
                             'and proposed correction.\n'
                             '- Emit calibration only from matched prior snapshots and observed outcomes; otherwise '
                             'state that it is unavailable.\n'
                             '\n'
                             'Handoff policy:\n'
                             '\n'
                             'Keep domain framing, clarification, source/evidence synthesis, draft outputs, and '
                             'next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external '
                             'action, approval, filing, send, publish, data mutation, implementation, review, CI, or '
                             'merge claim. Prepare a connector, file, coding, or human-review handoff only when the '
                             'user explicitly accepts that next step; report it only from observed evidence. Hermes '
                             'reviews supplied records; it does not replace a CRM, store or sync CRM data, mutate '
                             'opportunities, create dashboards or alerts, send outreach, book revenue, or claim seller '
                             'or buyer commitments that were not observed.\n'
                             '\n'
                             'Required inputs:\n'
                             '\n'
                             '- pipeline snapshot\n'
                             '- as-of time and review horizon\n'
                             '- currency, amount, stage, and forecast definitions\n'
                             '- prior forecast and actuals\n'
                             '- decision owner\n'
                             '\n'
                             'Expected outputs:\n'
                             '\n'
                             '- sales_pipeline_scope/v1\n'
                             '- sales_pipeline_health/v1\n'
                             '- sales_forecast_assessment/v1\n'
                             '- sales_outcome_learning_annex/v1\n'
                             '- sales_renewal_risk_annex/v1\n'
                             '- sales_pipeline_handoff/v1\n'
                             '\n'
                             'Artifact expectations:\n'
                             '\n'
                             '- prepared sales pipeline review brief when a wrapper captures it\n'
                             '- durable artifacts hold bounded aggregates, opaque source references, and only the '
                             'account identifiers an approved handoff needs; raw export rows and message content are '
                             'not persisted by default\n'
                             '\n'
                             'Safety rules:\n'
                             '\n'
                             '- Treat a missing or stale as-of time, undefined stage or forecast semantics, mixed '
                             'currencies without an observed conversion basis, unknown amount meaning, duplicate '
                             'opportunities, or missing owners as `HOLD`, never as an input to a calculation.\n'
                             '- Do not claim CRM storage, sync, mutation, dashboards, alerts, outreach, booked '
                             'revenue, or seller or buyer commitments; a proposed correction is not a change and a '
                             'scenario is not a promise.\n'
                             "- Consume the organization's supplied stage, category, probability, amount, and "
                             'close-date definitions; never impose a vendor schema or a default probability table.\n'
                             '- Persist bounded aggregates and opaque source references only; raw CRM exports and '
                             'message content stay out of durable artifacts unless the user explicitly approves a '
                             'scoped exception.\n'
                             '\n'
                             'Detailed procedure steps: `references/procedure.md`.\n',
                  'source_path': 'skills/omh-sales-pipeline-review/references/full-contract.md',
                  'source_sha256': 'ca5c932554aaa27326c6eab7b07a34e53d853251528efab343340d88457f2d91'},
                 {'relative_path': 'omh-sales-pipeline-review/references/procedure.md',
                  'content': '# sales-pipeline-review Specialist Procedure\n'
                             '\n'
                             'Expert clarification questions:\n'
                             '- `pipeline snapshot`\n'
                             '  - English: Which CRM export or pipeline snapshot is supplied, with its opaque source '
                             'reference, included motions, owners, cohort, record count, and known data-quality gaps '
                             'such as duplicates or missing owners?\n'
                             '  - Korean: 어떤 CRM 내보내기 파일 또는 파이프라인 스냅샷이 제공되며, 출처 참조, 포함된 영업 방식, 담당자, 코호트, 레코드 수, 중복이나 '
                             '담당자 누락 같은 알려진 데이터 품질 결함은 무엇인가요?\n'
                             '- `as-of time and review horizon`\n'
                             '  - English: What as-of timestamp does the snapshot carry, what review horizon and '
                             'cadence apply, and how stale may the data be before the review must HOLD?\n'
                             '  - Korean: 스냅샷의 기준 시각은 언제이고, 검토 기간과 주기는 무엇이며, 데이터가 얼마나 오래되면 검토를 보류해야 하나요?\n'
                             '- `currency, amount, stage, and forecast definitions`\n'
                             '  - English: Which currency and conversion basis, amount meaning, close-date meaning, '
                             'stage definitions with exit criteria, and forecast-category or probability definitions '
                             'does your organization use for these records?\n'
                             '  - Korean: 이 레코드에 적용되는 통화와 환산 기준, 금액의 의미, 마감일의 의미, 종료 기준을 포함한 단계 정의, 예측 카테고리 또는 확률 정의는 '
                             '무엇인가요?\n'
                             '- `prior forecast and actuals`\n'
                             '  - English: Which prior forecast snapshots and observed won, lost, slipped, or renewal '
                             'outcomes are supplied for calibration or learning, or is calibration not requested this '
                             'cycle?\n'
                             '  - Korean: 보정이나 학습을 위해 어떤 이전 예측 스냅샷과 관찰된 수주, 실주, 지연, 갱신 결과가 제공되나요, 아니면 이번 주기에는 보정을 요청하지 '
                             '않나요?\n'
                             '- `decision owner`\n'
                             '  - English: Who owns the review decision, who may approve proposed CRM corrections, and '
                             'which follow-up owners and due-date conventions apply?\n'
                             '  - Korean: 검토 결정의 책임자는 누구이고, 제안된 CRM 수정을 승인할 수 있는 사람은 누구이며, 후속 조치 담당자와 기한 규칙은 무엇인가요?\n'
                             '\n'
                             '## Procedure\n'
                             '\n'
                             'Declared checks:\n'
                             '- `sales_pipeline_scope_check`\n'
                             '  - Required result fields: `source_reference`, `as_of_time`, `review_horizon_cohort`, '
                             '`included_motions_owners`, `currency_conversion_basis`, `amount_semantics`, '
                             '`stage_definitions`, `forecast_category_definitions`, `freshness_status`, '
                             '`duplicate_status`, `missing_owner_status`, `data_quality_gaps`, `disposition`\n'
                             '  - Criterion: HOLD before any calculation or ranking when the as-of time is missing or '
                             'stale for the horizon, stage or forecast-category semantics are undefined, currencies '
                             'are mixed without an observed conversion basis, amount meaning is unknown, or duplicate '
                             'records and missing owners are unresolved; every field is supplied or observed, never '
                             'assumed.\n'
                             '- `sales_pipeline_health_check`\n'
                             '  - Required result fields: `stage_movement`, `aging_stalls`, `slipped_close_dates`, '
                             '`exit_criteria_evidence`, `next_step_quality`, `concentration`, `duplicates`, '
                             '`missing_ownership`, `deal_exceptions`, `record_evidence_refs`\n'
                             '  - Criterion: Derive movement, aging, stalls, slips, exit-criteria gaps, next-step '
                             'quality, and concentration from supplied records only, citing the record reference '
                             'behind every exception; never infer buyer activity or stage progress from silence, and '
                             'never rank deals a HOLD scope excluded.\n'
                             '- `sales_forecast_state_check`\n'
                             '  - Required result fields: `supplied_seller_category`, `supplied_probability`, '
                             '`scenario_range`, `observed_buyer_commitment`, `evidence_limits`, '
                             '`prior_forecast_actual_comparison`, `calibration_status`, `confidence`\n'
                             '  - Criterion: Keep stage, supplied seller category or probability, model-derived '
                             'scenario range, and observed buyer commitment as separate states: stage alone never '
                             'creates a probability or commitment, a probability-weighted total is a scenario and not '
                             'a promise, and calibration_status is `unavailable` unless matching prior snapshots and '
                             'observed outcomes were supplied.\n'
                             '- `sales_outcome_learning_check`\n'
                             '  - Required result fields: `cohort_bounds`, `observed_won_reasons`, '
                             '`observed_lost_reasons`, `unqualified_reasons`, `contradictions`, `missing_evidence`, '
                             '`research_followups`, `annex_status`\n'
                             '  - Criterion: Emit the learning annex only when supplied won, lost, or unqualified '
                             'evidence covers a bounded cohort; keep reasons observed rather than causal, record '
                             'contradictions and missing evidence, and set annex_status to `unsupported` when the '
                             'cohort is empty.\n'
                             '- `sales_renewal_risk_check`\n'
                             '  - Required result fields: `renewal_horizon`, `health_signal`, `utilization_signal`, '
                             '`support_signal`, `budget_signal`, `staffing_signal`, `open_risks`, '
                             '`expansion_hypotheses`, `owner`, `annex_status`\n'
                             '  - Criterion: Emit the renewal annex only when supplied renewal evidence exists; each '
                             'signal is observed, missing, or unknown, expansion items stay hypotheses, and an unowned '
                             'risk is recorded as a gap rather than assigned.\n'
                             '- `sales_pipeline_handoff_check`\n'
                             '  - Required result fields: `selected_account_followups`, `owner`, `due_date`, '
                             '`exit_criterion`, `evidence_ref`, `crm_object_field_value_proposals`, `approval_state`, '
                             '`sibling_routes`, `mutation_status`, `disposition`\n'
                             '  - Criterion: Every follow-up carries owner, due date, exit criterion, and evidence '
                             'reference; every CRM correction carries object, field, value, evidence, owner, and '
                             'approval state and stays proposed; mutation_status stays `not_observed` unless an '
                             'observed connector result exists, and account discovery, qualitative customer material, '
                             'generic calculation, and authoritative finance reporting are routed to their owning '
                             'workflows.\n'
                             '\n'
                             '### `sales_pipeline_validate_scope` (validation)\n'
                             '\n'
                             'Record the opaque source reference, as-of time, horizon and cohort, included motions and '
                             'owners, currency and conversion basis, amount semantics, stage and forecast-category '
                             'definitions, freshness, duplicates, missing owners, and data-quality gaps; return `HOLD` '
                             'with the exact blocking gap before calculating or ranking anything.\n'
                             '\n'
                             '- Input refs: `pipeline snapshot`, `as-of time and review horizon`, `currency, amount, '
                             'stage, and forecast definitions`, `decision owner`\n'
                             '- Output refs: `sales_pipeline_scope/v1`\n'
                             '- Check IDs: `sales_pipeline_scope_check`\n'
                             '\n'
                             '### `sales_pipeline_assess_health` (analysis)\n'
                             '\n'
                             'From the validated records identify stage movement, aging and stalls against the '
                             'supplied definitions, slipped close dates, exit-criteria evidence per stage, next-step '
                             'quality, concentration by account, owner, or segment, duplicates, missing ownership, and '
                             'deal exceptions, each tied to its record reference.\n'
                             '\n'
                             '- Input refs: `pipeline snapshot`, `as-of time and review horizon`, `currency, amount, '
                             'stage, and forecast definitions`\n'
                             '- Output refs: `sales_pipeline_health/v1`\n'
                             '- Check IDs: `sales_pipeline_health_check`\n'
                             '\n'
                             '### `sales_pipeline_assess_forecast` (analysis)\n'
                             '\n'
                             'Report supplied seller categories and probabilities as supplied, build scenario ranges '
                             'with their evidence limits, list observed buyer commitments separately, compare prior '
                             'forecasts with observed outcomes only when matching snapshots and actuals exist, and '
                             'state confidence; otherwise mark calibration `unavailable`.\n'
                             '\n'
                             '- Input refs: `pipeline snapshot`, `currency, amount, stage, and forecast definitions`, '
                             '`prior forecast and actuals`\n'
                             '- Output refs: `sales_forecast_assessment/v1`\n'
                             '- Check IDs: `sales_forecast_state_check`\n'
                             '\n'
                             '### `sales_pipeline_prepare_annexes` (production)\n'
                             '\n'
                             'When supplied evidence supports it, prepare the won/lost/unqualified learning annex by '
                             'bounded cohort with contradictions and research follow-ups, and the renewal-risk annex '
                             'with horizon, health, utilization, support, budget, and staffing signals, open risks, '
                             'expansion hypotheses, and owner; otherwise emit each annex as `unsupported` with the '
                             'missing evidence named.\n'
                             '\n'
                             '- Input refs: `pipeline snapshot`, `as-of time and review horizon`, `prior forecast and '
                             'actuals`\n'
                             '- Output refs: `sales_outcome_learning_annex/v1`, `sales_renewal_risk_annex/v1`\n'
                             '- Check IDs: `sales_outcome_learning_check`, `sales_renewal_risk_check`\n'
                             '\n'
                             '### `sales_pipeline_validate_handoff` (validation)\n'
                             '\n'
                             'Select account follow-ups with owner, due date, exit criterion, and evidence reference, '
                             'list proposed CRM object/field/value corrections with evidence, owner, and approval '
                             'state, name the sibling route for discovery, feedback, calculation, or finance work, and '
                             'return the review disposition with mutation, storage, sync, alert, and communication '
                             'left to the connector boundary.\n'
                             '\n'
                             '- Input refs: `pipeline snapshot`, `as-of time and review horizon`, `currency, amount, '
                             'stage, and forecast definitions`, `prior forecast and actuals`, `decision owner`\n'
                             '- Output refs: `sales_pipeline_handoff/v1`\n'
                             '- Check IDs: `sales_pipeline_scope_check`, `sales_pipeline_health_check`, '
                             '`sales_forecast_state_check`, `sales_pipeline_handoff_check`\n',
                  'source_path': 'skills/omh-sales-pipeline-review/references/procedure.md',
                  'source_sha256': 'ae092ea4d9363da82d23620f33a2f83e8a3dd42f4a8d69fd08b92cb2989fa138'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member sales-pipeline-review is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'},
 {'canonical_id': 'tech-debt-audit',
  'family_id': 'behavior-preserving-refactor',
  'description': '[omh] Accumulated tech debt to rank: build the severity-by-effort debt ledger from observed repo '
                 'evidence - orient, audit the named dimensions with file:line citations, rank fixes and quick wins - '
                 'and reconcile RESOLVED/NEW/CARRIED against the previous ledger on rerun. Use when the user says: '
                 'tech-debt-audit, tech debt, tech debt audit, technical debt, technical debt audit, tech debt ledger, '
                 'debt ledger, audit our tech debt.',
  'triggers': ['tech-debt-audit',
               'tech debt',
               'tech debt audit',
               'technical debt',
               'technical debt audit',
               'tech debt ledger',
               'debt ledger',
               'audit our tech debt'],
  'category': 'maintenance',
  'phase': 'tech-debt-audit',
  'role': 'reviewer',
  'source_folder': 'omh-tech-debt-audit',
  'source_path': 'skills/omh-tech-debt-audit/SKILL.md',
  'source_sha256': 'e8c5ce7eda593b4a824f67e3391e09dfc81ef52ab963c5e5d74c3574d9f47469',
  'required_inputs': ['the repo root or the scoped path list the audit is confined to',
                      'the stack truth from manifests (package/build files), not from memory of the tree',
                      'the previous ledger when one exists, so the rerun can reconcile instead of restart'],
  'expected_outputs': ['orientation summary: manifests read, churn ranking, largest files, test and CI entry points',
                       'findings table per `tech_debt_ledger/v1`: id, category, file:line, severity, effort, '
                       'recommendation',
                       'top fixes ranked by severity and the quick wins ranked by payoff-per-effort',
                       'the looks-bad-but-is-actually-fine list, and the RESOLVED/NEW/CARRIED reconciliation on rerun'],
  'artifact_expectations': ['debt ledger per `omh-tech-debt-audit/references/debt-dimensions.md`',
                            'prepared detection commands named per stack, marked observed only after their output is '
                            'seen'],
  'acceptance_criteria': ['Orientation evidence is observed: manifests, churn ranking, and largest files are named, '
                          'not assumed.',
                          'Every finding has id, dimension, file:line, severity, effort, and a bounded recommendation.',
                          'Quick wins and top fixes are ranked, and the looks-bad-but-is-actually-fine section is '
                          'present.',
                          'On rerun, every prior finding is reconciled RESOLVED, CARRIED, or superseded - none '
                          'silently dropped.'],
  'handoff_policy': 'Hermes owns the orientation, the dimension audit, and the ledger; detection commands run through '
                    "the operator's terminal and stay prepared_not_observed until their output is seen, and every fix "
                    'the ledger recommends is coding work for the selected executor lane, never part of the audit.',
  'catalog_rules': ['Route only on the source-defined description and triggers; do not treat nearest local contracts '
                    'as aliases.',
                    "Source routing exclusion: The target is one diff, PR, or claim rather than the codebase's "
                    'accumulated state; use `code-review`.',
                    'Source routing exclusion: The user wants the debt removed now, behavior preserved; use '
                    '`ai-slop-cleaner` for deletion-first cleanup.',
                    'Source routing exclusion: A boundary-changing fix from the ledger needs its execution shaped into '
                    'phases; use `refactor-plan`.',
                    'Source routing exclusion: The question is release risk for a specific deploy rather than source '
                    'quality; use `production-audit`.',
                    'Keep this canonical ID as prepared guidance because the local catalog marks it '
                    'preparedGuidanceMissing.',
                    'Do not claim provider, executor, runtime, mutation, or observed-result capability from this '
                    'metadata alone.'],
  'local_contract_ids': ['ai-slop-cleaner', 'code-review', 'ralplan'],
  'references': [{'relative_path': 'omh-tech-debt-audit/references/debt-dimensions.md',
                  'content': '# Debt Dimensions and the Ledger Contract\n'
                             '\n'
                             "The audit's full contract: what each dimension looks for, how findings are\n"
                             'graded, and how a rerun reconciles. Detection commands here are prepared\n'
                             'context - they count only when their output is observed.\n'
                             '\n'
                             '## Orientation first\n'
                             '\n'
                             'Before any dimension, establish the observed baseline:\n'
                             '\n'
                             '- **Stack truth** - read the manifests (package/build/dependency files), never\n'
                             '  memory of the tree.\n'
                             '- **Churn ranking** - `git log --format= --name-only | sort | uniq -c |\n'
                             '  sort -rn | head -30`: the most-changed files are where debt costs the most.\n'
                             '- **Size ranking** - the largest source files by line count.\n'
                             '- **Gate inventory** - the test suites, typecheckers, linters, and CI entry\n'
                             '  points that already exist; debt findings that a gate already catches are\n'
                             '  gate-configuration findings, not new debt.\n'
                             '\n'
                             "High-churn plus high-size plus low-test is the audit's priority corner.\n"
                             '\n'
                             '## The nine dimensions\n'
                             '\n'
                             '| Dimension | What to look for |\n'
                             '| --- | --- |\n'
                             '| Architectural decay | cyclic imports, god modules, layers bypassed, boundary leaks '
                             'between packages |\n'
                             '| Consistency rot | competing patterns for the same job - two HTTP clients, three error '
                             'styles, mixed naming |\n'
                             '| Type and contract gaps | untyped public surfaces, `any`-equivalents, implicit schemas '
                             'parsed in many places |\n'
                             '| Test debt | untested high-churn paths, skipped or stub tests, assertions that cannot '
                             'fail |\n'
                             '| Dependency and configuration debt | unpinned or abandoned dependencies, drifted config '
                             'copies, secrets handling by convention |\n'
                             '| Performance and resource debt | unbounded caches and queues, N+1 access patterns, sync '
                             'work on hot paths |\n'
                             '| Error-handling and observability debt | swallowed exceptions, bare retries, failures '
                             'invisible to logs or metrics |\n'
                             '| Security hygiene | credentials in the tree, injectable string building, permissive '
                             'defaults |\n'
                             '| Documentation drift | READMEs and comments contradicting the code, dead runbooks, '
                             'stale generated artifacts |\n'
                             '\n'
                             'Per-stack detection commands (linters, dead-code finders, dependency and\n'
                             'coverage audits) are named at audit time from the manifests read in\n'
                             'orientation; they stay prepared_not_observed until run through the operator.\n'
                             '\n'
                             '## Grading\n'
                             '\n'
                             '- **Severity**: `critical` (active correctness or security risk), `high`\n'
                             '  (costs every change in the area), `medium` (costs some changes), `low`\n'
                             '  (cosmetic or contained).\n'
                             '- **Effort**: `S` (one bounded change), `M` (a few files, one review),\n'
                             '  `L` (needs `refactor-plan` phases).\n'
                             '- **Top fixes** rank by severity first; **quick wins** are the\n'
                             '  severity-at-least-medium, effort-S rows - payoff per unit of effort.\n'
                             '- A `critical`/`L` finding routes to `refactor-plan`; the ledger never\n'
                             '  recommends a rewrite.\n'
                             '\n'
                             '## The ledger (`tech_debt_ledger/v1`)\n'
                             '\n'
                             'One row per finding: `id`, `dimension`, `file:line`, `severity`, `effort`,\n'
                             '`recommendation` (bounded, actionable). Stable `id` = dimension prefix plus\n'
                             'path plus a short slug (`test.src-routing-chat.untested-fallback`), so reruns\n'
                             'can match rows without archaeology. After the table: top fixes, quick wins,\n'
                             'and the mandatory **looks bad but is actually fine** section - deliberate\n'
                             'patterns that pattern-match to debt (a generated file, an intentional\n'
                             'duplication, a documented workaround) stay off the ledger with their reason\n'
                             'recorded, so the next audit does not rediscover them.\n'
                             '\n'
                             '## Rerun reconciliation\n'
                             '\n'
                             'With a previous ledger present, reconcile before writing:\n'
                             '\n'
                             '- **RESOLVED** - the cited evidence is gone at the cited location; name the\n'
                             '  commit or the observed absence.\n'
                             '- **CARRIED** - still present; keep the id, increment its age. A finding\n'
                             '  carried three audits is a prioritization finding about the ledger itself.\n'
                             '- **NEW** - not matched by any prior id.\n'
                             '\n'
                             'Prior ids that no longer match the tree are mapped by dimension plus path\n'
                             'before anything is declared RESOLVED. A rerun that restarts from zero loses\n'
                             "the ledger's point.\n"
                             '\n'
                             '## Boundary\n'
                             '\n'
                             'A ledger is prepared analysis: it is not a completed cleanup, a measured\n'
                             'quality improvement, observed command evidence, review, CI, or merge\n'
                             'evidence, and every fix it recommends is separate coding work.\n',
                  'source_path': 'skills/omh-tech-debt-audit/references/debt-dimensions.md',
                  'source_sha256': '7d0d601c1fc8897f0ce433dfa2ae44c2a5c9dd69ded28d7775cb6adbdd2afb75'}],
  'source_gaps': [],
  'blocked_prerequisites': ['The local catalog member tech-debt-audit is absent; nearest local contracts are '
                            'explicitly non-equivalent.',
                            'An explicit accepted handoff and matching observed provider, executor, or host evidence '
                            'are required before execution claims.',
                            'Native, provider, connector, or command surfaces remain upstream-only/not_observed until '
                            'a selected executor or wrapper supplies observed evidence; this record does not provide '
                            'OMJ execution.'],
  'evidence_boundary': 'prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, '
                       'routing, and preparation in Hermes; selected executor/runtime or provider actions require an '
                       'explicit accepted handoff and observed evidence. No executor/provider/runtime execution, '
                       'observed result, review, CI, deploy, or merge evidence is implied.'})
