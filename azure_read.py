from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from base64 import b64encode
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

from vars import AZURE_KEY

endpoint = 'https://devaa-po.cognitiveservices.azure.com/'

def analyze_read(doc_name: str) -> tuple[str, int]:
    reader = PdfReader(doc_name)
    total_pages = len(reader.pages)

    client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(AZURE_KEY)
    )

    texts = []
    for start in range(0, total_pages, 2):
        # build a 2‑page PDF
        writer = PdfWriter()
        for p in range(start, min(start + 2, total_pages)):
            writer.add_page(reader.pages[p])

        buf = BytesIO()
        writer.write(buf)
        chunk_bytes = buf.getvalue()

        # enforce 5 MB limit
        if len(chunk_bytes) > 5 * 1024 * 1024:
            raise ValueError(
                f"Pages {start+1}-{min(start+2, total_pages)} "
                f"exceed 5 MB ({len(chunk_bytes)} bytes)"
            )

        # base64‑encode and analyze
        chunk_b64 = b64encode(chunk_bytes).decode('utf-8')
        poller = client.begin_analyze_document(
            "prebuilt-read",
            AnalyzeDocumentRequest(bytes_source=chunk_b64)
        )
        result = poller.result()
        texts.append(result.content)

    full_text = "\n\n".join(texts)
    return full_text, total_pages

