"""
ComicInfo.xml generator following the ComicRack/Kavita/Komga standard schema.
Reference: https://github.com/anansi-project/comicinfo
"""
from typing import Optional
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from app.models.models import Comic


def _add_if_present(parent: Element, tag: str, value) -> None:
    """Add XML child element only if value is not None."""
    if value is not None:
        el = SubElement(parent, tag)
        el.text = str(value)


def generate_comicinfo_xml(comic: Comic) -> str:
    """
    Generate a ComicInfo.xml string for a given comic.

    Returns a pretty-printed XML string conforming to ComicInfo v2.1 schema.
    """
    root = Element("ComicInfo")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")

    # ── Identification ────────────────────────────────────────────────────────
    _add_if_present(root, "Title", comic.title)
    _add_if_present(root, "Series", comic.series)
    _add_if_present(root, "Number", comic.number)
    _add_if_present(root, "Count", comic.count)
    _add_if_present(root, "Volume", comic.volume)
    _add_if_present(root, "AlternateSeries", comic.alternate_series)
    _add_if_present(root, "AlternateNumber", comic.alternate_number)
    _add_if_present(root, "AlternateCount", comic.alternate_count)
    _add_if_present(root, "SeriesGroup", comic.series_group)

    # ── Summary & Notes ───────────────────────────────────────────────────────
    _add_if_present(root, "Summary", comic.summary)
    _add_if_present(root, "Notes", comic.notes)

    # ── Publication Date ──────────────────────────────────────────────────────
    _add_if_present(root, "Year", comic.year)
    _add_if_present(root, "Month", comic.month)
    _add_if_present(root, "Day", comic.day)

    # ── Publisher ─────────────────────────────────────────────────────────────
    _add_if_present(root, "Publisher", comic.publisher)
    _add_if_present(root, "Imprint", comic.imprint)

    # ── Creators ──────────────────────────────────────────────────────────────
    _add_if_present(root, "Writer", comic.writer)
    _add_if_present(root, "Penciller", comic.penciller)
    _add_if_present(root, "Inker", comic.inker)
    _add_if_present(root, "Colorist", comic.colorist)
    _add_if_present(root, "Letterer", comic.letterer)
    _add_if_present(root, "CoverArtist", comic.cover_artist)
    _add_if_present(root, "Editor", comic.editor)
    _add_if_present(root, "Translator", comic.translator)

    # ── Classification ────────────────────────────────────────────────────────
    _add_if_present(root, "Genre", comic.genre)
    _add_if_present(root, "Tags", comic.tags)
    _add_if_present(root, "Web", comic.web)
    _add_if_present(root, "Format", comic.format)
    _add_if_present(root, "AgeRating", comic.age_rating)
    _add_if_present(root, "LanguageISO", comic.language_iso)
    _add_if_present(root, "Manga", comic.manga)

    if comic.is_bw is not None:
        _add_if_present(root, "BlackAndWhite", "Yes" if comic.is_bw else "No")

    # ── Ratings & Review ──────────────────────────────────────────────────────
    _add_if_present(root, "CommunityRating", comic.community_rating)
    _add_if_present(root, "Review", comic.review)

    # ── Page Info ─────────────────────────────────────────────────────────────
    _add_if_present(root, "PageCount", comic.page_count)

    # ── Identifiers ───────────────────────────────────────────────────────────
    if comic.isbn:
        _add_if_present(root, "ISBN", comic.isbn)
    if comic.barcode:
        _add_if_present(root, "Barcode", comic.barcode)

    # Pretty-print
    raw = tostring(root, encoding="unicode")
    parsed = minidom.parseString(raw)
    return parsed.toprettyxml(indent="  ", encoding=None)
