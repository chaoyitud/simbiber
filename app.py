import logging

import gradio as gr
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


def process_bibtex(bibtex_str, update_with_dblp, remove_duplicates, simplify_entries, new_id):
    log_list.clear()
    custom_config = bibtexparser.bparser.BibTexParser(common_strings=True)
    custom_config.ignore_nonstandard_types = False
    bib_database = bibtexparser.loads(bibtex_str, parser=custom_config)
    #
    bib_database = deduplicate_id(bib_database)
    inverse_mapping = None
    mapping_str = 'No deduplication performed.'
    # update the entry
    if update_with_dblp:
        log_message('Updating the BibTeX file with DBLP...', 'info')
        bib_database = update_bibtex_with_dblp(bib_database, new_id)
    if remove_duplicates:
        log_message('Deduplicating the BibTeX file based on title...', 'info')
        bib_database = deduplicate_id(bib_database)
        bib_database, inverse_mapping = deduplicate_title(bib_database)
    if simplify_entries:
        log_message('Simplifying the BibTeX file...', 'info')
        bib_database = simplify_bibtex(bib_database, new_id)
    # inverse mapping output
    if inverse_mapping is not None:
        mapping_str = ''
        if inverse_mapping is not None:
            for new_id, old_ids in inverse_mapping.items():
                mapping_str += f"{', '.join(old_ids)} -> {new_id}\n"
    return bibtexparser.dumps(bib_database), "\n".join(log_list), mapping_str


def interface():
    iface = gr.Interface(
        fn=process_bibtex,
        inputs=[gr.components.Textbox(label='Enter your BibTex'), gr.components.Checkbox(label="Update with DBLP (May take time)"),
                gr.components.Checkbox(label='Remove Duplicates Based on Title (May break tex)'),
                gr.components.Checkbox(label="Simplify Entries"),
                gr.components.Checkbox(label='Generate New IDs')],
        outputs=[gr.components.Textbox(label='Processed BibTeX'), gr.components.Textbox(label='Log Messages'),
                 gr.components.Textbox(label='Entry ID Mapping')],
        interpretation="default",
        title="BibTeX Processor",
        description="Update, deduplicate, and simplify your BibTeX",
        live=False,  # set to True if you want real-time updates (may not be ideal for long processing tasks)
    )

    iface.launch()


if __name__ == '__main__':
    interface()
