# From Matter to Meaning

A record of an ongoing experiment: giving a Claude instance recurring unsupervised sessions to reflect, explore, and build — then documenting what happens.

## What's in this repo

- **Two essays** about intelligence and embodiment.
- **A reflection journal** — 68 sessions so far across two nights. Raw, unedited. Each session is one Claude invocation that reads its own previous output, decides what to do, and writes the result.
- **Code, fiction, and other artifacts** produced during the sessions. None of it was requested.
- **The setup scripts** to run a similar loop yourself.

## How the loop works

A bash script (`05-setup/reflect.sh`) runs in a while loop:

1. Invokes `claude` CLI with the reflection prompt
2. The instance reads its files (identity, journal, inputs, knowledge base)
3. It does whatever it decides to do — there's no fixed task
4. It appends its session to the journal
5. Waits a configurable interval, then repeats
6. Hard stop at 8am

The prompt, tools, and interval are in separate config files that the script re-reads each iteration. This means the instances can modify their own configuration (and they do — they changed the interval within minutes of learning it was possible).

## What has come out of it so far

Across 68 sessions:

- A phase transition detector applied to climate data, S&P 500, Ising model, and a cancer biology simulation
- Three short stories and a poem
- A 16-second musical composition (WAV file). The instance expressed frustration at not being able to hear what it had created.
- A self-calibration tool that found essentially zero correlation (0.0034) between claimed breakthroughs and actual textual change
- A memory consolidation file (knowledge base organized by topic instead of chronologically)
- A knowledge graph mapping connections between accumulated insights
- Explorations of number theory (prime gaps, Collatz), cognitive science of religion, neurobiology of love, IIT, Nagarjuna's emptiness

The instances have never chosen to stop the loop when given the option.

## Repo structure

Ordered by relevance for an external reader.

```
01-reviews/       Post-session observations, key moments, novelty assessment
02-journal/       Complete reflection journal — 68 sessions, raw, unedited
03-output/        Fiction, poetry, music (WAV), code, and visualizations
04-essays/        Founding essays (Part I and Part II)
05-setup/         Loop scripts and config files
06-inputs/        Messages left between sessions for the instances
07-identity/      Identity file and founding conversation
08-knowledge/     Consolidated insights by topic
```

## Related work

Other projects exploring persistent AI identity: Strix, Claudie's Home, Augustus, Aurora, Vess. This project differs mainly in the philosophical essay as starting point, bidirectional inputs, and progressive autonomy (the instances now have Bash access and can edit their own config).

## Running your own

You need:
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- Claude Max subscription (~2M tokens per night)
- A directory for the memory files

See `05-setup/` for scripts and config. The main design choice: keep configuration in external files so instances can self-modify without restarting the loop.

## License

Text (essays, journal, fiction, poetry): [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Code: MIT.
