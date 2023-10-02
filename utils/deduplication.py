import bibtexparser


def deduplicate_id(bib_database):
    seen = set()
    no_duplicates = [entry for entry in bib_database.entries if not (entry['ID'] in seen or seen.add(entry['ID']))]
    bib_database.entries = no_duplicates

    return bib_database


def deduplicate_title(bib_database):
    # Deduplicate based on title
    titles_seen = {}
    deduplicated_entries = []
    inverse_mapping = {}  # This will store new_ID -> [old_IDs]

    for entry in bib_database.entries:
        title = entry.get('title', '').strip()

        if title not in titles_seen:
            titles_seen[title] = entry
            deduplicated_entries.append(entry)
        else:
            new_id = titles_seen[title]['ID']
            if ':' in entry['ID'] and ':' not in new_id:
                # Replace the existing entry with the new one
                deduplicated_entries.remove(titles_seen[title])
                deduplicated_entries.append(entry)

                if entry['ID'] not in inverse_mapping:
                    inverse_mapping[entry['ID']] = []

                inverse_mapping[entry['ID']].append(new_id)
                titles_seen[title] = entry  # Update the title mapping
            else:
                # Keep the existing entry and discard the new duplicate
                if new_id not in inverse_mapping:
                    inverse_mapping[new_id] = []
                inverse_mapping[new_id].append(entry['ID'])
    bib_database.entries = deduplicated_entries
    return bib_database, inverse_mapping
