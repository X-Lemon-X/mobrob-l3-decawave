# Knowledge base

Everything we know and decide about lab 3 (beacon-based global localization
with the Decawave/Qorvo UWB system), in plain Markdown.
Code lives in [`code/`](../code/); the report in [`report/`](../report/).

## Layout

| Path | What goes there |
|---|---|
| [knowledge/](knowledge/) | Facts: how the code, tools and hardware work. Should stay true until the code changes. |
| [proposals/](proposals/) | Plans and design options that are not built yet. Each has a status. |
| [log.md](log.md) | Project log: meetings and work sessions, newest first. |
| [decisions.md](decisions.md) | Short log of decisions taken, newest first, with the reason. |
| [open-questions.md](open-questions.md) | Things we still have to decide or find out. |
| [sources.md](sources.md) | Where external information came from (documents processed from `inbox/`, links). |

## Pages

Knowledge
- [Decawave lab setup and data](knowledge/decawave-setup.md)
- [Message formats](knowledge/messages.md)
- [Beacon localization algorithm](knowledge/beacon-localization.md)
- [Encoder odometry](knowledge/encoder-odometry.md)
- [Evaluation method and results](knowledge/evaluation.md)
- [Running the code](knowledge/running.md)

Proposals
- none yet

## Conventions

- English only (the assignment is in English).
- One topic per file. Link between pages with relative links.
- Write facts in `knowledge/`, opinions and plans in `proposals/`.
- When a proposal is accepted, set its status to `accepted`, add a line to
  `decisions.md`, and move the facts it establishes into `knowledge/` once
  the code exists.
- Units are metres, seconds, radians; coordinate frame as in
  [decawave-setup.md](knowledge/decawave-setup.md#coordinate-frame).
- External material goes through [`inbox/`](../inbox/README.md).
