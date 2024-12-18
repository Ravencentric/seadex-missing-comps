# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyanilist==0.6.1",
#     "seadex==0.4.0",
# ]
# ///


from seadex import SeaDexEntry
from pyanilist import AniList, Media
from time import sleep


def sorter(entry: tuple[Media, str]) -> int:
    """
    Key function for sorting entries
    """
    return entry[0].popularity if entry[0].popularity is not None else -1


def main() -> None:
    with (
        SeaDexEntry() as seadex_entry,
        AniList() as anilist,
    ):
        entries: list[tuple[Media, str]] = []

        for entry in seadex_entry.iterator():
            if not any(
                comp.startswith("https://slow.pics") for comp in entry.comparisons
            ):
                media = anilist.get_media(id=entry.anilist_id)
                entries.append((media, entry.url))
                print(f"Found: {media.title} - {entry.url}")
                sleep(2)  # Avoid AniList rate limit

        entries.sort(reverse=True, key=sorter)

        with open("README.md", "w", encoding="utf-8") as file:
            file.write("## SeaDex entries with no comparisons\n")
            file.write("0. Title / Year / Score / SeaDex / AniList\n")
            for idx, (media, url) in enumerate(entries, start=1):
                line = f"{idx}. {media.title}"

                if year := media.start_date.year:
                    line += f" / {year}"
                if score := media.average_score:
                    line += f" / {score}"

                line += f" / [SeaDex]({url}) / [AniList]({media.site_url})\n"

                file.write(line)


if __name__ == "__main__":
    main()
