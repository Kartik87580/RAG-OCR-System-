from pathlib import Path
import shutil
import time
import zipfile
from typing import Dict, Any



# Global job storage (production: use Redis)
JOBS: Dict[str, Dict[str, Any]] = {}

# Global OCR model (load once!)
OCR_MODEL = None

def init_ocr():
    global OCR_MODEL
    if OCR_MODEL is None:
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import PdfFormatOption
        print("🔄 Loading Docling (takes a moment)...")
        
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        
        OCR_MODEL = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        print("✅ Docling ready!")
    return OCR_MODEL

def write_job(job_id: str, data: Dict):
    JOBS[job_id] = {**JOBS.get(job_id, {}), **data}

def export_chapters_final(result, output_dir: Path) -> tuple[str, list]:
    from docling_core.types.doc import DocItemLabel, TableItem
    doc = result.document
    current_chapter_name = "Introduction"
    current_content = []
    chapter_count = 0
    
    full_markdown_content = []
    generated_chapters_data = []

    def save_chapter(index, name, content):
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{index:02d}_{clean_name[:50]}.md"
        path = output_dir / filename
        text_content = "".join(content)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text_content)
        print(f"Created: {filename}")
        return filename, text_content

    for item, level in doc.iterate_items():
        # Check for heading labels
        label_str = str(item.label)
        is_heading = "heading" in label_str.lower()

        # Split at the top-most level (Level 0)
        if is_heading and level == 0:
            if current_content:
                fname, text = save_chapter(chapter_count, current_chapter_name, current_content)
                chapter_count += 1
                full_markdown_content.append(text)
                generated_chapters_data.append({"filename": fname, "content": text, "name": current_chapter_name})

            current_chapter_name = getattr(item, 'text', f"Chapter_{chapter_count}").strip()
            current_content = [f"# {current_chapter_name}\n\n"]

        else:
            # Handle different item types manually for maximum stability
            if isinstance(item, TableItem):
                # For tables, we use the item's built-in export to markdown
                table_md = item.export_to_markdown()
                current_content.append(f"\n{table_md}\n\n")
            elif is_heading:
                # Format sub-headings with appropriate # depth
                prefix = "#" * (level + 1)
                text = getattr(item, 'text', '')
                current_content.append(f"{prefix} {text}\n\n")
            else:
                # Standard paragraphs or other text items
                text = getattr(item, 'text', '')
                if text:
                    current_content.append(f"{text}\n\n")

    # Save final chapter
    if current_content:
        fname, text = save_chapter(chapter_count, current_chapter_name, current_content)
        full_markdown_content.append(text)
        generated_chapters_data.append({"filename": fname, "content": text, "name": current_chapter_name})
            
    return "\n\n".join(full_markdown_content), generated_chapters_data

def fast_extract_pdf(pdf_path: str, job_id: str) -> tuple[str, list]:
    """Extract PDF using Docling and split into chapters"""
    converter = init_ocr()
    start_time = time.time()
    
    print(f"📄 Processing {pdf_path} with Docling...")
    write_job(job_id, {"status": "running", "progress": 10})

    # Run conversion
    result = converter.convert(pdf_path)
    write_job(job_id, {"status": "running", "progress": 50})
    
    # Prepare output directory
    output_dir = Path(f"extracted_chapters_{job_id}")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export chapters
    full_markdown, files_data = export_chapters_final(result, output_dir)
    
    elapsed = time.time() - start_time
    print(f"⚡ Processed in {elapsed:.1f}s")
    
    write_job(job_id, {"status": "running", "progress": 100})
    
    # Return full markdown and list of generated chapter files with content
    json_pages = [
        {
            "type": "chapter", 
            "chapter_index": i+1, 
            "filename": d['filename'], 
            "content": d['content']
        } 
        for i, d in enumerate(files_data)
    ]
    
    return full_markdown, json_pages

def zip_output(output_dir: Path, zip_path: Path):
    """Zip results"""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for file in output_dir.rglob("*"):
            if file.is_file():
                z.write(file, file.relative_to(output_dir))

