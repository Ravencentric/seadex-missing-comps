# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyanilist==0.6.1",
#     "seadex==0.4.0",
#     "prettytable==3.12.0",
# ]
# ///


import argparse
from dataclasses import dataclass
from time import sleep

from prettytable import PrettyTable, TableStyle
from pyanilist import AniList, Media
from seadex import SeaDexEntry


@dataclass
class Entry:
    title: str
    year: int | None
    score: int | None
    seadex: str
    anilist: str


def get_entries() -> tuple[Entry, ...]:
    """Get SeaDex entries with missing comparisons sorted by popularity."""
    results: list[Entry] = []

    with (
        SeaDexEntry() as seadex_entry,
        AniList() as anilist,
    ):
        entries: list[tuple[Media, str]] = []
        count = 0

        for entry in seadex_entry.iterator():
            if not any(
                comp.startswith("https://slow.pics") for comp in entry.comparisons
            ):
                media = anilist.get_media(id=entry.anilist_id)
                entries.append((media, entry.url))
                print(f"Found: {media.title} - {entry.url}")
                sleep(2)  # Avoid AniList rate limit
                if count ==5:
                    break
                else:
                    count += 1

        entries.sort(
            reverse=True,
            key=lambda x: x[0].popularity if x[0].popularity is not None else -1,
        )

        for media, url in entries:
            results.append(
                Entry(
                    title=str(media.title),
                    year=media.start_date.year,
                    score=media.average_score,
                    seadex=url,
                    anilist=str(media.site_url),
                )
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
    data = get_entries()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("## SeaDex entries with missing comparisons\n")
        f.write(stringify(data))
