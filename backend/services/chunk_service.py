import re
import uuid
from typing import List, Dict, Any

def extract_hierarchy_and_chunk(json_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Step 1 & 2: Extract Hierarchy and Chunk Smartly
    """
    hierarchy = []
    chunks = []
    
    current_chapter = "Unknown Chapter"
    current_section = "Unknown Section"
    
    # Regex patterns (Updated for Markdown & Traditional)
    # Chapter: "# Title" or "1. Title"
    chapter_pattern = re.compile(r'^(#\s+.+|\d+\.\s+[A-Z][A-Za-z\s]+)')
    # Section: "## Title" or "1.1 Title"
    section_pattern = re.compile(r'^(#{2,6}\s+.+|\d+\.\d+\s+[A-Za-z\s]+)')
    
    # We will accumulate text and process it
    # However, because hierarchy depends on specific lines, we handle line by line or block by block from pages
    
    print(f"DEBUG: Processing {len(json_pages)} pages/chapters for chunking...")

    for page_data in json_pages:
        # Use chapter_index if available, otherwise fall back to page or default
        page_num = page_data.get('chapter_index', page_data.get('page', 1))
        content = page_data.get('content', '')
        if not content and 'markdown' in page_data:
            content = page_data['markdown']
            
        if not content:
            print(f"DEBUG: Page {page_num} has empty content.")
            continue
            
        # Normalize double newlines for paragraph splitting
        # Split by lines to detect headers
        lines = content.split('\n')
        
        buffer_text = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for Chapter
            chapter_match = chapter_pattern.match(line)
            if chapter_match:
                # If we have buffer, flush it as a chunk with PREVIOUS context
                if buffer_text:
                    create_chunks(chunks, buffer_text, page_num, current_chapter, current_section)
                    buffer_text = ""
                
                current_chapter = line.replace('#', '').strip()
                # Reset section when new chapter starts
                current_section = "" 
                hierarchy.append({"page": page_num, "chapter": current_chapter})
                # Add header to buffer or treat as metadata only? 
                # Better to include header in text for context
                # Add header to buffer for context
                buffer_text = line 
                continue 
            
            # Check for Section
            section_match = section_pattern.match(line)
            if section_match:
                if buffer_text:
                    create_chunks(chunks, buffer_text, page_num, current_chapter, current_section)
                    buffer_text = ""
                
                current_section = line.replace('#', '').strip()
                hierarchy.append({"page": page_num, "chapter": current_chapter, "section": current_section})
                continue
            
            # Add line to buffer
            if buffer_text:
                buffer_text += "\n" + line
            else:
                buffer_text = line
        
        # End of page, flush buffer? 
        # Or keep buffer across pages? 
        # Usually chunking is better if we respect page boundaries if hierarchy might change, 
        # but text flows across pages. 
        # Let's flush at end of page to keep "page" metadata accurate for the chunk.
        if buffer_text:
            create_chunks(chunks, buffer_text, page_num, current_chapter, current_section)

    return {
        "hierarchy": hierarchy,
        "chunks": chunks,
        "ready_for_embedding": True
    }

def create_chunks(chunks_list, text, page, chapter, section):
    """
    Step 2: Chunk Smartly (Max 800 chars, natural breaks)
    Step 3: Generate Embeddings Metadata
    """
    max_chars = 800
    
    # Split by double newlines to respects paragraphs
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    
    for para in paragraphs:
        # If adding this paragraph exceeds max_chars, save current chunk and start new
        if len(current_chunk) + len(para) > max_chars:
            if current_chunk:
                add_chunk_node(chunks_list, current_chunk, page, chapter, section)
                current_chunk = ""
            
            # If paragraph itself is huge, we must split it hard or by single lines
            if len(para) > max_chars:
                # simplistic splitting for very long text
                while len(para) > max_chars:
                    split_idx = para[:max_chars].rfind(' ')
                    if split_idx == -1: split_idx = max_chars
                    
                    sub = para[:split_idx]
                    add_chunk_node(chunks_list, sub, page, chapter, section)
                    para = para[split_idx:].strip()
                current_chunk = para
            else:
                current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
                
    if current_chunk:
        add_chunk_node(chunks_list, current_chunk, page, chapter, section)

def add_chunk_node(chunks_list, text, page, chapter, section):
    text = text.strip()
    if not text: return
    
    chunk_id = f"chunk_{uuid.uuid4().hex[:8]}"
    full_keywords = extract_keywords(text)
    
    node = {
        "id": chunk_id,
        "content": text,
        "metadata": {
            "page": page,
            "chapter_index": page, # Explicitly store as chapter_index as well
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

# For backward compatibility if needed, or update pdf_pipeline to use the new function
def chunk_text(text):
    # This was the old signature. 
    # If the pipeline calls this with a string, we might fail or need to wrap it.
    # But we will update the pipeline.
    pass



