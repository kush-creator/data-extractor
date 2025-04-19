import gradio as gr
from gradio_pdf import PDF
from os import system
from json import load
import pandas as pd

from vars import PASSWORDS, LIMITS, PREFILLED, GLOBAL_UPLOAD_COUNTER, preconfig

from tesseract import tesseract_ocr
from azure_read import analyze_read
from extract import extract_fields

from difflib import SequenceMatcher
from typing import List, Dict, Any

from atexit import register

@register
def save_state():
    """Save the state of the app to a file."""
    with open('state.json', 'w') as f:
        f.write('{"counter":' + str(GLOBAL_UPLOAD_COUNTER) + ',')
        f.write('"soham":' + str(LIMITS['soham']) + ',')
        f.write('"maifounder":' + str(LIMITS['maifounder']) + '}')


choices=list(PREFILLED.keys())
choices.append('Custom')


def export_as_excel(fields, prefilled, mode, request: gr.Request):
    if prefilled != 'Custom':
        curr = 'files_outputs/' + PREFILLED[prefilled].split('/')[1].split('.')[0] + '_' + mode
        with open(curr + '.json', 'r') as f:
            data = load(f)

    elif prefilled == 'Custom' and len(fields) != 0:
        data = fields

    else:
        return gr.Warning("⚠️ Please extract data before exporting.", duration=5)

    df = (
        pd.DataFrame(data)
            .rename(columns={'text': 'Field', 'out': 'Extracted Data'})
            .drop(columns=['id'])
    )
    df.to_excel(f'excel/{prefilled} {mode} {request.username}.xlsx', index=False)
    return f'excel/{prefilled} {mode} {request.username}.xlsx'


def get_page_counts(request: gr.Request):
    return gr.Markdown(f'# MAI\'s Data Extraction Tool | Pages Left: {LIMITS[request.username]}')


def parse_response_to_fields(response: str, fields: List[Dict[str, Any]], threshold: float):
    parsed = [dict(f) for f in fields]

    for line in response.splitlines():
        if ':' not in line:
            continue

        key_part, value_part = line.split(':', 1)
        key = key_part.strip()
        value = value_part.strip()
        if not key or not value:
            continue

        best_idx = None
        best_score = threshold
        key_lower = key.lower()
        for idx, field in enumerate(parsed):
            candidate = field['text'].lower()
            score = SequenceMatcher(None, key_lower, candidate).ratio()
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx is not None:
            parsed[best_idx]['out'] = value

    return parsed


def add_box(boxes, next_id):
    """Add an empty box with a brand‑new, permanent id."""
    return boxes + [{'id': next_id, 'text': '', 'out': ''}], next_id + 1


def drop_box(boxes, box_id):
    """Remove the box whose id == box_id (never fewer than 1)."""
    if len(boxes) > 1:
        boxes = [b for b in boxes if b['id'] != box_id]
    return boxes


def save_text(boxes, box_id, new_val):
    """Persist whatever the user typed so the value survives re‑renders."""
    for b in boxes:
        if b['id'] == box_id:
            b['text'] = new_val
            break
    return boxes


def save_file(name):
    global GLOBAL_UPLOAD_COUNTER
    system('cp ' + name + f' files/upload_{GLOBAL_UPLOAD_COUNTER}.pdf')
    GLOBAL_UPLOAD_COUNTER += 1


def get_output_data(pdf, mode, fields, request: gr.Request):
    """Get the output data from the PDF file."""

    if not pdf:
        return fields, get_page_counts(request), gr.Warning("⚠️ Please upload a PDF file before continuing.", duration=5)

    fields_list = []
    for field in fields:
        fields_list.append(field['text'])

    if mode == 'Cheap':
        text, number = tesseract_ocr(pdf)
    else:
        text, number = analyze_read(pdf)

    LIMITS[request.username] -= number
    extracted_response = extract_fields(text, fields_list)

    outputs = parse_response_to_fields(extracted_response, fields, threshold=0.7)
    
    return outputs, get_page_counts(request)


custom_css = """
#pdf-box { height: 90vh }
#pdf-box canvas { height: 82vh }

#field-data { height: 70vh; overflow: auto}

footer {visibility: hidden}'
"""

with gr.Blocks(title='MAI Extraction Tool Demo', theme='default', css=custom_css, fill_height=True) as page:
    
    title = gr.Markdown('# MAI\'s Data Extraction Tool | Pages Left: ')
    fields = gr.State([])
    next_id = gr.State(187)

    with gr.Row():
        with gr.Column(scale=4):
            pdf = PDF(label='Document', elem_id='pdf-box', interactive=True)

        with gr.Column(scale=5):
            with gr.Row(equal_height=True):
                prefilled = gr.Dropdown(choices=choices, value='Custom', scale=3, label='Sample Tests', interactive=True)
                mode = gr.Radio(choices=['Cheap', 'Accurate'], scale=2, label='Mode', value='Accurate', interactive=True)
                extract = gr.Button('Extract Data', variant='primary')

            with gr.Row():
                add_btn = gr.Button('➕ Add Field', interactive=True)
                get_base = gr.Button('Populate Fields', interactive=True)
                download = gr.DownloadButton(elem_id='download_btn_hidden', visible=False)
                export = gr.Button('Export as Excel', interactive=True)

            export.click(export_as_excel, inputs=[fields, prefilled, mode], outputs=download).then(fn=None, inputs=None, outputs=None, js="() => document.querySelector('#download_btn_hidden').click()")

            def get_base_fields():
                return preconfig

            add_btn.click(add_box, [fields, next_id], [fields, next_id])
            get_base.click(get_base_fields, inputs=None, outputs=fields)

            def change_pdf_related(pdf):
                if not pdf:
                    return gr.Dropdown(value='Custom', interactive=True)
                else:
                    if 'files/' + str(pdf).split('/')[-1] not in PREFILLED.values():
                        save_file(pdf)
                    return gr.Dropdown(interactive=True)
            
            def change_prefilled_related(prefilled):
                if prefilled != 'Custom':
                    return [gr.Button('➕ Add Field', interactive=False), PDF(value=PREFILLED[prefilled]), gr.Button(interactive=False), gr.Button(interactive=False)]
                else:
                    return [gr.Button('➕ Add Field', interactive=True), PDF(value=''), gr.Button(interactive=True), gr.Button(interactive=True)]

            pdf.change(change_pdf_related, inputs=pdf, outputs=prefilled)
            prefilled.change(change_prefilled_related, inputs=[prefilled], outputs=[add_btn, pdf, extract, get_base])

            with gr.Column(elem_id='field-data'):
                @gr.render(inputs=[fields, prefilled, mode], triggers=[prefilled.change, mode.change, fields.change])
                def draw(current_fields, prefilled, mode):
                    if prefilled == 'Custom':
                        for b in current_fields:
                            bid = b['id']
                            with gr.Row(equal_height=True):
                                tb=gr.Textbox(value=b['text'], show_label=False, placeholder='Field', key=f'tb-{bid}', scale=5)
                                tb.blur(lambda bl, v, _id=bid: save_text(bl, _id, v), inputs=[fields, tb], outputs=fields)
                                gr.TextArea(value=b['out'], show_label=False, placeholder='Extracted Data', key=f'out-{bid}', interactive=False, scale=5, lines=1)
                                gr.Button('❌', key=f'rm-{bid}', min_width=10).click(lambda bl, _id=bid: drop_box(bl, _id), inputs=fields, outputs=fields)
                    else:
                        current_file = 'files_outputs/' + PREFILLED[prefilled].split('/')[1].split('.')[0] + '_' + mode
                        with open(current_file + '.json', 'r') as f:
                            data = load(f)
                        for b in data:
                            bid = b['id']
                            with gr.Row(equal_height=True):
                                tb=gr.Textbox(value=b['text'], show_label=False, placeholder='Field', key=f'tb-{bid}', scale=5, interactive=False)
                                gr.TextArea(value=b['out'], show_label=False, placeholder='Extracted Data', key=f'out-{bid}', interactive=False, scale=5, lines=1)
                                gr.Button('❌', key=f'rm-{bid}', min_width=10, interactive=False)

        extract.click(fn=get_output_data, inputs=[pdf, mode, fields], outputs=[fields, title], show_api=False)
    
    page.load(get_page_counts, inputs=[], outputs=title)
                

if __name__ == '__main__':
    page.launch(favicon_path='OnlyBlue.png', show_api=False, auth=PASSWORDS)