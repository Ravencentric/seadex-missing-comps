# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyanilist==0.6.1",
#     "seadex==0.4.0",
# ]
# ///


from seadex import SeaDexEntry
from pyanilist import AniList
from time import sleep


def main() -> None:
    with (
        SeaDexEntry() as seadex_entry,
        AniList() as anilist,
    ):
        entries: list[tuple[int, str, str]] = []

        for entry in seadex_entry.iterator():
            if not any(comp.startswith("https://slow.pics") for comp in entry.comparisons):
                media = anilist.get_media(id=entry.anilist_id)
                popularity = media.popularity if media.popularity is not None else -1
                entries.append((popularity, str(media.title), entry.url))
                print(f"Found: {media.title} - {entry.url}")
                sleep(2) # Avoid AniList rate limit

        entries.sort(reverse=True, key=lambda x: x[0])

        with open("README.md", "w", encoding="utf-8") as file:
            file.write("## SeaDex entries with no comparisons\n")
            for idx, (_, title, url) in enumerate(entries, start=1):
                file.write(f"{idx}. {title} - {url}\n")

if __name__ == "__main__":
    main()
