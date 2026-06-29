# Discord Bot Wrapper Flow

This example shows the recommended shape for a Discord bot or hosted chat
wrapper. Hermes Agent remains the user-facing runtime. OMJ supplies local,
deterministic contracts that the wrapper can render, persist, and update with
observed evidence.

The user should not need to know OMJ command names. The wrapper translates a
plain Discord message into a chat response, plan decision, coding handoff, and
status update.

## Primary Flow

1. The bot receives a Discord message and writes the raw platform event to a
   temporary local file such as `event.json`.

2. The bot asks OMJ for the wrapper-native interaction envelope:

   ```sh
   interaction_json="$(omj chat interact --source discord --event-json event.json)"
   ```

3. The bot renders the safe chat response in the same Discord thread:

   ```sh
   printf '%s' "$interaction_json" |
     python -c 'import json,sys; data=json.load(sys.stdin)["chat_response"]; body=data.get("messenger_rendering", {}).get("body_text"); isinstance(body, str) or sys.exit("missing messenger_rendering.body_text"); print(data["headline"]); print(body)'
   ```

   `chat_response.headline` already starts with a visible marker such as
   `[omj] web-research`. Discord uses the `limited_markdown` render profile, so
   `chat_response.messenger_rendering.body_text` is the body to post; it keeps
   prose intact while converting supported Markdown tables into bullets. Rich
   Hermes TUI or web surfaces can render their own profile's `body_text` with
   tables preserved. Keep the prefix on the first line only; repeat it only
   when posting separate split messages.
   Typical action ids include `accept_plan`, `revise_plan`, `choose_executor`,
   `show_prompt_handoff`, `copy_prompt_handoff`, `send_to_executor`,
   `show_status`, and `cancel`. `send_to_codex` is only a compatibility alias
   when the selected executor profile is `codex`.

4. If the wrapper needs restart recovery, start or resume a metadata-only chat
   session keyed to the Discord message/thread:

   ```sh
   session_json="$(
     omj chat session start \
       --source discord \
       --source-event-id "$DISCORD_MESSAGE_ID" \
       --channel-ref "$DISCORD_CHANNEL_ID" \
       "risky refactor"
   )"
   session_id="$(printf '%s' "$session_json" | python -c 'import json,sys; print(json.load(sys.stdin)["session"]["session_id"])')"
   ```

5. If OMJ returns a plan, wait for the user to accept or revise it before
   preparing a coding handoff:

   ```sh
   omj chat session accept-plan "$session_id"
   ```

6. For accepted implementation-shaped work, choose who owns the coding work.
   Codex can create a run-backed lifecycle; non-Codex profiles prepare
   prompt-only handoffs without creating a runtime run:

   ```sh
   omj chat session select-executor "$session_id" codex
   ```

7. Prepare the selected handoff and link it to the wrapper session:

   ```sh
   handoff_json="$(omj chat session prepare-handoff "$session_id" "risky refactor")"
   run_id="$(printf '%s' "$handoff_json" | python -c 'import json,sys; print(json.load(sys.stdin)["session"]["current_run_id"])')"
   ```

8. If the selected executor is Codex, dispatch the
   `coding_executor_handoff/v1` payload to the external coding executor outside
   OMJ, then record only transitions the wrapper actually observed:

   ```sh
   omj coding lifecycle dispatch --run "$run_id"
   omj coding lifecycle result --run "$run_id" --result completed --evidence-ref codex-log
   omj coding lifecycle verify --run "$run_id" --completion-status completed
   ```

   If the selected executor is prompt-only, render the `prompt_handoff` for the
   user to copy or for the wrapper to pass to its own executor integration. Do
   not mark dispatch, execution, review, CI, or merge evidence as observed from
   the prompt alone.

9. Render status updates from the local lifecycle report:

   ```sh
   omj coding lifecycle report --run "$run_id"
   omj chat session status "$session_id"
   ```

## Status Boundaries

- A prepared handoff is not execution evidence.
- Hermes should not claim it implemented code from an OMJ record.
- Review, verification, CI, and merge status require separately observed
  wrapper or runtime evidence.
- Use `not_observed` or `not_available` when the bot cannot prove a transition.

## Lower-Level Diagnostics

The lower-level runtime commands are still useful for debugging custom wrappers
or inspecting local artifacts directly:

```sh
run_json="$(omj runtime record --skill oh-my-jeo --harness coding-handling --status started)"
run_id="$(printf '%s' "$run_json" | python -c 'import json,sys; print(json.load(sys.stdin)["run"]["run_id"])')"

omj runtime delegate --run "$run_id" --requested --not-observed --result not_observed
omj runtime show "$run_id"
omj runtime validate --run "$run_id"
```

Use these diagnostic commands when you need explicit artifact inspection. For
normal Discord or Slack UX, prefer `omj chat interact`, `omj chat session`, and
`omj coding lifecycle`.
