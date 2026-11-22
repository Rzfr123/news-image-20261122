# Sunday 22 November 2026 — The World's News in One Image

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Rzfr123/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Rzfr123/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A newspaper front page summing up Sunday 22 November 2026 in 35 dated stories: COP31 close to a final deal in Antalya, Russia's 400-drone barrage on Ukraine, Iran striking US bases in Bahrain, the burning Russian cargo ship in the Gulf of Finland, 'El Chapo Isidro' caught, Bolsonaro in intensive care, and 29 more — with a DATE CHECK box naming the earlier news deliberately left out.

Bounty: https://make.fun/bounty/news-image-20261122

## How it was made

`render.py` draws the whole page programmatically with Pillow on cream paper: flat vector illustrations, original drawings, no photographs, so every headline is exact text. `main.ts` copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`) and validates it first: PNG magic, 1024x1024, 8-bit RGB, ≤1 MiB, every chunk CRC, IEND last, byte-identical copy.

## Stories

Leads: COP31 deal close (Antalya) · Russia's 400-drone barrage (Kyiv) · Iran strikes US bases (Bahrain). Features 4–13: Gulf of Finland ship fire, Kryvyi Rih strike, Bayelsa boat capsize, Eisenkot–Likud talks, Gaza aid vehicle, 'El Chapo Isidro' caught, Iran electricity rationing, Nvidia probe, Bolsonaro in intensive care, Marles on AUKUS. Briefs 14–35: FBI hack probe, teen gamer rescue, Vance 2028, Saudi missile downed, Lebanon, Iran 'silent economic war', Hormuz swim, Moldova, Belgium strike, IG Metall, Lisbon march, Denmark expulsion, Bangladesh fires, Fred Nile, Melbourne 1956, EU–Indonesia deal, rugby, football, tennis.

## Sources

Reporting of Sunday 22 November 2026 by Reuters, BBC, Al Jazeera, DW, The Straits Times, Sky News, CNA, ABC Australia, Times of India, The Guardian and Kyiv Independent, as recorded in `run-notes.md`.

## License

MIT — see LICENSE.
