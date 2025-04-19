from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from typing import List

llm = init_chat_model(model='claude-3-5-haiku-20241022', model_provider='anthropic')

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', 'You are a helpful assistant that extracts data from the output of OCR perfromed of PDF Files. Please Reply in the format: `FieldName: ExtractedData` with each field in a new line. DO NOT ADD ANY PLEASANTRIES OR GREETINGS OR ANSWER IN SENTENCES. ONLY PROVIDE THE RESPONSE IN THE PARTICULAR FORMAT. PLEASE WRITE DATES IN DD/MM/YYYY. If a field is not found, write \'NOT FOUND\'', ),
        ('human', 'Please extract the following fields:\n{fields}\n\nFrom the PDF OCR Output text:\n{ocr_output}'),
    ]
)

chain = prompt | llm

def extract_fields(ocr_output: str, fields: List[str]):
    """Extracts the fields from the OCR output."""
    extracted = chain.invoke({ 'ocr_output': ocr_output, 'fields': ','.join(fields) })
    return extracted.content