import re
import uuid
from typing import List, Dict, Any

def extract_hierarchy_and_chunk(json_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Step 1 & 2: Extract Hierarchy and Chunk Smartly
    Docs: https://github.com/pymupdf/pymupdf
    """
    hierarchy = []
    chunks = []
    
    current_chapter = "Unknown Chapter"
    current_section = "Unknown Section"
    
    # REQ 1: REGEX IMPROVEMENTS
    # Relaxed & Case-insensitive. 
    # Supports: Markdown (#), Numbered (1.), Mixed case text.
    # Chapter examples: "# Title", "1. Introduction", "Chapter 1"
    chapter_pattern = re.compile(r'^(#\s|chapter\s+\d|\d+\.\s).*', re.IGNORECASE)
    
    # Section examples: "## Title", "### Title", "1.1 Subsection", "1.2.3 Detail"
    section_pattern = re.compile(r'^(#{2,6}\s|\d+(\.\d+)+\s).*', re.IGNORECASE)
    
    # REQ 3: DO NOT FLUSH BUFFER AT PAGE BOUNDARIES
    # We maintain a persistent buffer across pages to merge content.
    buffer_text = ""
    # Track the page number where the current buffer started
    buffer_start_page = 1
    
    print(f"DEBUG: Processing {len(json_pages)} pages/chapters for chunking...")

    for page_data in json_pages:
        # Use simple 'page' key or fallback
        page_num = page_data.get('chapter_index', page_data.get('page', 1))
        content = page_data.get('content', '')
        
        # Fallback to markdown if content empty
        if not content and 'markdown' in page_data:
            content = page_data['markdown']
            
        if not content:
            # Only print debug if it's truly empty (sometimes happens with Images-only pages)
            # print(f"DEBUG: Page {page_num} has empty content.")
            continue

        # If buffer is empty, mark start page as current page
        if not buffer_text:
            buffer_start_page = page_num
            
        # Normalize double newlines for paragraph splitting if needed, 
        # but here we process line by line for headers
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for Chapter (Priority over Section)
            if chapter_pattern.match(line):
                # Flush previous buffer before starting new chapter
                if buffer_text:
                    create_chunks(chunks, buffer_text, buffer_start_page, current_chapter, current_section)
                    buffer_text = ""
                
                # Update Context
                current_chapter = line.replace('#', '').strip()
                current_section = "" # Reset section on new chapter
                hierarchy.append({"page": page_num, "chapter": current_chapter})
                
                # REQ 2: INCLUDE HEADERS IN CHUNKS
                # Start new buffer with the header line
                buffer_text = line
                buffer_start_page = page_num
                continue 
            
            # Check for Section
            if section_pattern.match(line):
                # Flush previous buffer before starting new section
                if buffer_text:
                    create_chunks(chunks, buffer_text, buffer_start_page, current_chapter, current_section)
                    buffer_text = ""
                
                # Update Context
                current_section = line.replace('#', '').strip()
                # If we consider sections as sub-nodes, add to hierarchy
                hierarchy.append({"page": page_num, "chapter": current_chapter, "section": current_section})
                
                # REQ 2: INCLUDE HEADERS IN CHUNKS
                # Start new buffer with the header line
                buffer_text = line
                buffer_start_page = page_num
                continue
            
            # Standard Text Line
            if buffer_text:
                buffer_text += "\n" + line
            else:
                buffer_text = line
                buffer_start_page = page_num
        
        # REQ 3: Removed logic that flushes buffer here. 
        # We loop to next page accumulating text.

    # Flush any remaining text at the End of Document
    if buffer_text:
        create_chunks(chunks, buffer_text, buffer_start_page, current_chapter, current_section)

    return {
        "hierarchy": hierarchy,
        "chunks": chunks,
        "ready_for_embedding": True
    }

def create_chunks(chunks_list, text, page, chapter, section):
    """
    Step 2: Chunk Smartly (Token-Aware)
    Target ~500 tokens. 
    1 token ≈ 4 chars. So ~2000 chars.
    """
    # REQ 5: TOKEN-AWARE CHUNK SIZE
    TARGET_TOKENS = 500
    CHARS_PER_TOKEN = 4
    MAX_CHARS = TARGET_TOKENS * CHARS_PER_TOKEN  # ~2000 chars
    
    # Split by double newlines to respect paragraphs
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    
    for para in paragraphs:
        # Check size if we add this paragraph
        # (Len current + Len para + 1 whitespace)
        if len(current_chunk) + len(para) > MAX_CHARS:
            # If current_chunk has content, save it before starting new
            if current_chunk:
                add_chunk_node(chunks_list, current_chunk, page, chapter, section)
                current_chunk = ""
            
            # If the paragraph itself is larger than the limit, we must split it
            if len(para) > MAX_CHARS:
                # Naive split by spaces to keep it simple and library-free
                words = para.split(' ')
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk) + len(word) + 1 > MAX_CHARS:
                        add_chunk_node(chunks_list, temp_chunk, page, chapter, section)
                        temp_chunk = word
                    else:
                        temp_chunk += (" " + word) if temp_chunk else word
                
                # Assign remainder to current_chunk (might be empty or start of next)
                current_chunk = temp_chunk
            else:
                current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
                
    # Add trailing content
    if current_chunk:
        add_chunk_node(chunks_list, current_chunk, page, chapter, section)

def add_chunk_node(chunks_list, text, page, chapter, section):
    text = text.strip()
    if not text: return
    
    chunk_id = f"chunk_{uuid.uuid4().hex[:8]}"
    
    # REQ 6: KEEP KEYWORD EXTRACTION LIGHT (Existing function)
    full_keywords = extract_keywords(text)
    
    # REQ 4: FIX METADATA & REQ 7: PRESERVE OUTPUT FORMAT
    # Removed 'chapter_index'. Added 'chapter', 'section', 'keywords'.
    node = {
        "id": chunk_id,
        "content": text,
        "metadata": {
            "page": page,
            "chapter": chapter,
            "section": section,
            "keywords": full_keywords
        }
    }
    chunks_list.append(node)

def extract_keywords(text):
    """
    Step 3: Keywords (Top 5 nouns)
    Simple heuristic without heavy NLP lib
    """
    # Remove special chars
    clean = re.sub(r'[^a-zA-Z\s]', '', text)
    words = clean.split()
    
    # Filter common stop words (short list)
    stop_words = {"the", "and", "is", "of", "to", "in", "a", "for", "that", "this", "on", "with", "as", "are", "it", "be", "by", "or", "from", "at", "an", "was", "not"}
    nouns = [w for w in words if w.lower() not in stop_words and len(w) > 2]
    
    # Count frequency
    counts = {}
    for n in nouns:
        n = n.capitalize() # Normalize
        counts[n] = counts.get(n, 0) + 1
        
    # Sort by freq
    sorted_nouns = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [n[0] for n in sorted_nouns[:5]]

# Backwards compatibility mock if other files import it (though should be updated)
def chunk_text(text):
    pass




