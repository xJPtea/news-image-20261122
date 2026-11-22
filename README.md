# The World Today — 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/xJPtea/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/xJPtea/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A program that draws one newspaper front page summing up Sunday
22 November 2026 in a single 1024×1024 image. The page names the day
up front and covers seven verified stories from that day, across
regions and fields.

## The seven stories

1. **Gaza (lead)** — Australia, Canada, Italy and Britain jointly
   demand Israel open Gaza to aid as floods swamp shelters.
2. **The Gulf** — Saudi defences down a Houthi missile near Mecca
   in the early hours of Sunday.
3. **Climate** — COP31 talks resume in Antalya, still deadlocked
   over fossil fuels and finance.
4. **Israel** — Eisenkot opens unity talks with Netanyahu's Likud.
5. **Myanmar** — A magnitude 4.1 earthquake strikes before dawn.
6. **Sport** — Zverev and Alcaraz meet for the ATP Finals crown
   in Turin tonight.
7. **Hong Kong** — Voting begins for the powerful Election Committee.

Every story and its source is recorded in [NEWS.md](NEWS.md), including
the stories that were deliberately left out because they belong to
earlier days.

## How it works

`main.py` is pure Python 3.13 standard library — no Pillow, no network.
It draws the page pixel by pixel with a hand-written 5×7 bitmap font
and a hand-written PNG encoder, so the output is byte-for-byte
deterministic: run it twice and the two files are identical.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
python3 test_entry.py                    # determinism + format checks
```

`test_entry.py` runs the program twice into two fresh directories and
asserts byte-identical output, a valid PNG header, 1024×1024 pixels,
and a file size of at most 1 MiB.

## License

MIT — see [LICENSE](LICENSE).
