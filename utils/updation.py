import bibtexparser
from reffix import utils as ut
import os
import re
import logging
import pprint
from bibtexparser.bparser import BibTexParser


def update_bibtex_with_dblp(input_data, replace_name=False):
    bib_database = process(
        bib_database=input_data,
        replace_arxiv=True,  # or True, based on preference
        force_titlecase=True,
        interact=False,
        no_publisher=True,
        process_conf_loc=True,
        replace_name=replace_name,
    )

    return bib_database


def process(
        bib_database,
        replace_arxiv,
        force_titlecase,
        interact,
        no_publisher,
        process_conf_loc,
        replace_name=False,
):
    if process_conf_loc:
        import spacy

        # download spacy model if not existing
        if not spacy.util.is_package("en_core_web_sm"):
            ut.log_message("Downloading spacy model...", "info")
            os.system("python -m spacy download en_core_web_sm")
            ut.log_message("Spacy model downloaded successfully.", "info")

        nlp = spacy.load("en_core_web_sm")

    bp = BibTexParser(interpolate_strings=False, common_strings=True)
    bp.ignore_nonstandard_types = False
    ut.log_message("Bibliography file loaded successfully.", "info")
    orig_entries_cnt = len(bib_database.entries)

    for i in range(len(bib_database.entries)):
        try:
            orig_entry = bib_database.entries[i]
            title = orig_entry["title"]
            try:
                first_author = ut.get_authors_canonical(orig_entry)[0]
            except IndexError:
                # don't try to match if there is no first author
                continue

            query = title + " " + first_author

            entries = ut.get_dblp_results(query)
            entry = select_entry(entries, orig_entry=orig_entry, replace_arxiv=replace_arxiv)

            if entry is not None:
                # replace the new BibTeX reference label with the original one
                if not replace_name:
                    entry["ID"] = orig_entry["ID"]
                if process_conf_loc and entry.get("ENTRYTYPE") == "inproceedings":
                    entry = ut.process_conf_location(entry, nlp)

                # if the title is titlecased in the original entry, do not modify it
                if force_titlecase and not ut.is_titlecased(entry["title"]):
                    entry["title"] = ut.to_titlecase(entry["title"])

                entry["title"] = ut.protect_titlecase(entry["title"])
                orig_str = pprint.pformat(orig_entry, indent=4)
                new_str = pprint.pformat(entry, indent=4)
                conf = "y"

                if interact:
                    logging.info(f"\n---------------- Original ----------------\n {orig_str}\n")
                    logging.info(f"\n---------------- Retrieved ---------------\n {new_str}\n")
                    while True:
                        conf = input("==> Replace the entry (y/n)?: ").lower()
                        if conf == "y" or conf == "n":
                            break
                        print("Please accept (y) or reject (n) the change.")
                if conf == "y":
                    bib_database.entries[i] = entry

                    if ut.is_equivalent(entry, orig_entry):
                        # the entry is equivalent, using the DBLP bib entry
                        ut.log_message(ut.entry_to_str(entry), info="update")
                    elif replace_arxiv and ut.is_arxiv(orig_entry) and not ut.is_arxiv(entry):
                        # non-arxiv version was found on DBLP
                        ut.log_message(ut.entry_to_str(entry), info="update_arxiv")
                    else:
                        # a different version was found on DBLP
                        ut.log_message(ut.entry_to_str(entry), info="update")

            else:
                entry = orig_entry

                # no result found, keeping the original entry
                if force_titlecase and not ut.is_titlecased(title):
                    title = ut.to_titlecase(title)

                title = ut.protect_titlecase(title)
                entry["title"] = title
                ut.log_message(ut.entry_to_str(entry), info="keep")

            if no_publisher and entry.get("ENTRYTYPE") in ["article", "inproceedings"] and "publisher" in entry:
                del entry["publisher"]

            # attempt to fix potential errors
            entry = ut.clean_entry(entry)
        except Exception as e:
            ut.log_message(f"Error processing entry {orig_entry['ID']}", info="error")
            ut.log_message(f"Error: {e}", info="error")

    new_entries_cnt = len(bib_database.entries)
    assert orig_entries_cnt == new_entries_cnt
    return bib_database


def select_entry(entries, orig_entry, replace_arxiv):
    if not entries:
        return None

    matching_entries = []
    # keep only entries with matching title, ignoring casing and non-alpha numeric characters
    # (some titles are returned with trailing dot, dashes may be inconsistent, etc.)
    orig_title = re.sub(r"[^0-9a-zA-Z]+", "", orig_entry["title"]).lower()
    orig_authors = ut.get_authors_canonical(orig_entry)

    # try to find if any entry is better than the original one
    for entry in entries:
        title = re.sub(r"[^0-9a-zA-Z]+", "", entry["title"]).lower()

        # skip entries with no authors
        if "author" not in entry:
            continue

        authors = ut.get_authors_canonical(entry)

        # keep only entries where at least one of the authors is also present in the original entry
        if title == orig_title and len(set(orig_authors).intersection(set(authors))) > 0:
            matching_entries.append(entry)

    # split into arxiv and non-arxiv publications
    entries_other = [entry for entry in matching_entries if not ut.is_arxiv(entry)]
    entries_arxiv = [entry for entry in matching_entries if ut.is_arxiv(entry)]

    best_all = ut.get_best_entry(matching_entries, orig_entry)
    best_other = ut.get_best_entry(entries_other, orig_entry)
    best_arxiv = ut.get_best_entry(entries_arxiv, orig_entry)

    # we found a non-arxiv entry for an arxiv entry but not returning it because the flag was not set -> notify the user
    if not replace_arxiv and ut.is_arxiv(orig_entry) and best_other is not None:
        ut.log_message(ut.entry_to_str(orig_entry), "non_arxiv_found")

    # best entries can be None (if None is returned, no new entry was selected)
    if replace_arxiv:
        return best_other or best_all
    else:
        return best_arxiv or best_all


if __name__ == "__main__":
    update_bibtex_with_dblp("../bib/test.bib", replace_name=True)
