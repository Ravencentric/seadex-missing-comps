# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "seadex==0.4.0",
#     "prettytable==3.12.0",
#     "httpx>=0.28.1",
#     "pydantic>=2.10.5",
# ]
# ///


import argparse
from itertools import batched

import httpx
from prettytable import PrettyTable, TableStyle
from pydantic import BaseModel
from seadex import EntryRecord, SeaDexEntry

URL = "https://graphql.anilist.co"

QUERY = """\
query Media($idIn: [Int]) {
  Page {
    media(id_in: $idIn) {
      id
      title {
        romaji
        english
      }
      startDate {
        year
      }
      averageScore
      popularity
    }
  }
}
"""


class Entry(BaseModel):
    title: str
    year: int | None
    score: int | None
    popularity: int | None
    seadex: str
    anilist: str


def get_entries_with_no_comps() -> tuple[Entry, ...]:
    """Get SeaDex entries with missing comparisons"""
    results: list[Entry] = []

    with SeaDexEntry() as seadex_entry:
        entries: list[EntryRecord] = []

        for entry in seadex_entry.iterator():
            if not any(
                comp.startswith("https://slow.pics") for comp in entry.comparisons
            ):
                entries.append(entry)

    with httpx.Client() as client:
        for batch in batched(entries, 50):
            resp = client.post(
                URL,
                json={
                    "query": QUERY,
                    "variables": {"idIn": [entry.anilist_id for entry in batch]},
                },
            ).raise_for_status().json()["data"]["Page"]["media"]

            for media in resp:
                results.append(
                    Entry(
                        title=media["title"]["english"] or media["title"]["romaji"],
                        year=media["startDate"]["year"],
                        score=media["averageScore"],
                        popularity=media["popularity"],
                        seadex=f"https://releases.moe/{media['id']}/",
                        anilist=f"https://anilist.co/anime/{media['id']}",
                    ),
                )

    results.sort(
        reverse=True,
        key=lambda x: x.popularity if x.popularity is not None else -1,
    )

    return tuple(results)


def stringify(entries: tuple[Entry, ...]) -> str:
    """Convert the entries into a markdown string."""
    table = PrettyTable()
    table.set_style(TableStyle.MARKDOWN)
    table.align = "l"
    table.field_names = ["Idx", "Title", "Year", "Score", "Links"]
    for idx, entry in enumerate(entries, start=1):
        table.add_row(
            [
                idx,
                entry.title,
                entry.year,
                entry.score,
                f"[SeaDex]({entry.seadex}), [AniList]({entry.anilist})",
            ],
        )

    return table.get_formatted_string()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dump SeaDex entries with missing comparisons.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file name (default: nocomps.md)",
        default="nocomps.md",
    )

    args = parser.parse_args()
    data = get_entries_with_no_comps()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("## SeaDex entries with missing comparisons\n")
        f.write(stringify(data))
