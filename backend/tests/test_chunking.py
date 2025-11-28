from services.document_processor import DocumentProcessor

def test_chunking_basic():
    dp = DocumentProcessor()
    text = "Sentence one. Sentence two. Sentence three. " * 50
    chunks, metadata = dp.chunk_text(text, "test.txt")
    assert len(chunks) > 0
    assert len(chunks) == len(metadata)
    # Ensure overlap logic produces sequential chunks
    assert metadata[0]["chunk_index"] == 0

