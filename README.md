# The Day in One Image — 25 November 2026

Entry for the make.fun bounty
["Sum up 25 November's world news in one image"](https://make.fun/bounty/news-image-20261125)
($100, top 50 entries share the prize).

## What it is

`main.py` (Python 3, standard library only) draws a newspaper-style
front page — "THE DAY IN ONE IMAGE" — summing up the world's news of
Wednesday 25 November 2026, and writes it to `/output/entry.png`.

No network, no clock, no randomness: every run writes the same bytes.

## The stories

- **Ukraine – Russia:** Zelenskiy confirms Kyiv struck a cargo ship
  in the Gulf of Finland; Moscow calls the drone strikes on Russian
  ships (also off Libya) "terrorism" and warns of consequences.
- **Climate – Antalya:** the COP31 summit collapses with no deal, as
  oil and gas producers block a fossil-fuel phaseout.
- **Energy – Hormuz:** three oil tankers hit by naval mines in the
  Strait of Hormuz, Iran's Revolutionary Guard Navy says.
- **Security – Poland:** NATO to send early-warning aircraft to Poland
  after missiles landed during an attack on Ukraine.
- **India – Punjab:** BJP and Shiromani Akali Dal reunite for the 2027
  Punjab election, after a six-year split.
- **Also today:** 266 million people face acute food insecurity (WFP);
  Gaza's death toll reaches 74,746.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image is a 1024x1024 PNG, well under the 1 MiB limit. Two runs
produce byte-identical output (verified by SHA-256).

## License

MIT — see `LICENSE`.
