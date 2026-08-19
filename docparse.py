"""docparse - extract text from PDF files in Python."""

import zlib
from pathlib import Path
from typing import List, Optional


class PDFTextExtractor:
    """Small pure-Python extractor for text streams inside PDF documents."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(self.path)

    def _read_streams(self) -> List[bytes]:
        raw = self.path.read_bytes()
        streams: List[bytes] = []
        marker = b"stream"
        start = 0
        while True:
            idx = raw.find(marker, start)
            if idx == -1:
                break
            eol = raw.find(b"\n", idx)
            if eol == -1:
                break
            end = raw.find(b"endstream", eol)
            if end == -1:
                break
            data = raw[eol + 1:end].strip()
            if data:
                streams.append(data)
            start = end + 1
        return streams

    def _decompress(self, data: bytes) -> bytes:
        try:
            return zlib.decompress(data)
        except zlib.error:
            return data

    def extract_text(self, max_pages: Optional[int] = None) -> str:
        out: List[str] = []
        count = 0
        for stream in self._read_streams():
            text = self._decompress(stream).decode("latin-1", errors="ignore")
            if "BT" in text and "Tj" in text:
                out.append(text)
                count += 1
                if max_pages is not None and count >= max_pages:
                    break
        return "\n".join(out)


def extract(pdf_path: str) -> str:
    """Convenience entry point."""
    return PDFTextExtractor(pdf_path).extract_text()
