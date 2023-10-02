import re

LOCATION_ABBREVIATIONS = {
    # Countries and regions
    "USA", "UK", "UAE", "EU", "NZ", "SA", "RSA", "USSR", "PRC",

    # US states
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",

    # Canadian provinces
    "AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT",

    # Major cities and their common abbreviations
    "NYC", "LA", "SF", "CHI", "DC", "LDN",  # New York City, Los Angeles, San Francisco, Chicago, D.C., London

    # International organizations and bodies
    "UN", "NATO", "ASEAN", "OPEC",

    # Continents and major regions
    "NA", "SA", "EU", "AS", "AF", "OC", "AN",  # North America, South America, Europe, Asia, Africa, Oceania, Antarctica

    # Some major cities around the world
    "HK", "TPE", "TOK", "SYD",  # Hong Kong, Taipei, Tokyo, Sydney
}


def is_location_abbreviation(segment: str) -> bool:
    """
    Check if the segment contains a location abbreviation.
    """
    matches = re.findall(r"\{(\w+)\}", segment)
    for match in matches:
        if match in LOCATION_ABBREVIATIONS:
            return True
    return False


def simplify_booktitle(booktitle: str, year: str = None) -> str:
    """
    Simplifies the booktitle by:
    1. Keeping only the first segment (before the comma).
    2. If any later segment contains '{}', it is retained unless it's a location abbreviation.
    3. If a year is provided, removing that year substring from any segment.
    """
    segments = booktitle.split(',')

    # Keeping the first segment
    simplified_title = [segments[0].strip()]

    # Checking the remaining segments
    for segment in segments[1:]:
        if '{' in segment and '}' in segment and not is_location_abbreviation(segment):
            simplified_title.append(segment.strip())

    # If year is provided, remove it from any segment
    if year:
        simplified_title = [segment.replace(year, '').strip() for segment in simplified_title]

    return ', '.join(simplified_title)


def simplify_bibtex(bib_database, replace_name=False):
    for entry in bib_database.entries:
        if entry['ENTRYTYPE'] not in ['book', 'inproceedings', 'article', 'misc', 'incollection']:
            continue
        if replace_name:
            abbreviation_match = re.search(r"/(\w+)/", entry['ID'])
            abbreviation = abbreviation_match.group(1) if abbreviation_match else "yr"

            # Modify the BibTeX entry ID
            first_author = entry['author'].split('and')[0].strip().split(' ')[-1]

            title_abbreviation = entry['title'].split(' ')[0]
            if title_abbreviation.lower() in ['a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by',
                                              'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above',
                                              'below', 'under', 'up', 'down', 'off', 'over', 'under', 'again',
                                              'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                                              'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
                                              'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                                              'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']:
                title_abbreviation = entry['title'].split(' ')[1]

            entry_id = f"{first_author}:{abbreviation}{entry['year'][-2:]}:{title_abbreviation}"
            entry['ID'] = entry_id
            entry['ID'] = re.sub(r"[^a-zA-Z0-9:]+", "", entry['ID'])

        if 'booktitle' in entry:
            year_value = entry.get('year', None)
            entry['booktitle'] = simplify_booktitle(entry['booktitle'], year_value)
        desired_fields = ['author', 'title', 'journal', 'booktitle', 'volume', 'pages', 'year', 'ENTRYTYPE', 'ID']
        keys_to_remove = [key for key in entry if key not in desired_fields]
        for key in keys_to_remove:
            del entry[key]
    return bib_database
