import argparse
import logging
import bibtexparser
from utils.updation import update_bibtex_with_dblp
from utils.simplification import simplify_bibtex
from utils.deduplication import deduplicate_id, deduplicate_title
from reffix.utils import log_message


class ListHandler(logging.Handler):  # Custom handler to store logs in a list
    def __init__(self, log_list):
        super().__init__()
        self.log_list = log_list

    def emit(self, record):
        self.log_list.append(self.format(record))


log_list = []

handler = ListHandler(log_list)
logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

# Attach the handler to the root logger
root_logger = logging.getLogger()
root_logger.addHandler(handler)

logger = logging.getLogger(__name__)


def get_args_parser():
    parser = argparse.ArgumentParser(description='BibTeX Processing Tool')

    parser.add_argument('--input',
                        type=str,
                        default='references.bib',
                        help='Path to the input BibTeX file. Default is "references.bib".')

    parser.add_argument('--output',
                        type=str,
                        default='simplified.bib',
                        help='Path to the output BibTeX file. Default is "simplified.bib".')

    parser.add_argument('--update', '-u',
                        action='store_true',
                        help='Update the input BibTeX file with changes.')

    parser.add_argument('--de_title', '-d',
                        action='store_true',
                        help='Deduplicate entries based on title.')

    parser.add_argument('--simplify', '-s',
                        action='store_true',
                        help='Simplify the BibTeX entries (e.g., remove unnecessary fields).')

    parser.add_argument('--new_id', '-i',
                        action='store_true',
                        help='Generate new IDs for BibTeX entries.')

    return parser


def main(args):
    # read the input file
    with open(args.input, 'r') as bibtex_file:
        custom_config = bibtexparser.bparser.BibTexParser(common_strings=True)
        custom_config.ignore_nonstandard_types = False
        bib_database = bibtexparser.load(bibtex_file, parser=custom_config)
    #
    bib_database = deduplicate_id(bib_database)
    inverse_mapping = None
    # update the entry
    if args.update:
        log_message('Updating the BibTeX file with DBLP...', 'info')
        bib_database = update_bibtex_with_dblp(bib_database, args.new_id)
    if args.de_title:
        log_message('Deduplicating the BibTeX file based on title...', 'info')
        bib_database = deduplicate_id(bib_database)
        bib_database, inverse_mapping = deduplicate_title(bib_database)
    if args.simplify:
        log_message('Simplifying the BibTeX file...', 'info')
        bib_database = simplify_bibtex(bib_database, args.new_id)
    # write the output file
    with open(args.output, 'w') as bibtex_file:
        bibtexparser.dump(bib_database, bibtex_file)
    if inverse_mapping is not None:
        with open('id_mapping.txt', 'w') as f:
            for new_id, old_ids in inverse_mapping.items():
                f.write(f"{', '.join(old_ids)} -> {new_id}\n")


if __name__ == '__main__':
    args = get_args_parser().parse_args()
    main(args)
