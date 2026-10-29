import streamlit as st
from markitdown import MarkItDown
import tempfile
import os
import zipfile
import io

st.set_page_config(page_title="ConvertInAjaBro", page_icon="📝")

file_formats = [
    "PDF",
    "PowerPoint",
    "Word",
    "Excel",
    "Images (EXIF metadata and OCR)",
    "Audio (EXIF metadata and speech transcription)",
    "HTML",
    "Text-based formats (CSV, JSON, XML)",
    "ZIP files (iterates over contents)",
    "YouTube URLs",
    "EPubs"
]

st.title("ConvertInAjaBro Web App by Fz")
st.write("Convert multiple files with `markitdown` by Microsoft on Python.")
st.write("Support these formats:")
st.write(file_formats)

st.markdown("### 1. Upload Files")
uploaded_files = st.file_uploader(
    "Support multiple files upload!", 
    type=[
        "pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls", 
        "jpg", "jpeg", "png", "webp", "bmp", 
        "mp3", "wav", "m4a", "flac", 
        "html", "htm", "csv", "json", "xml", "txt", "md", 
        "zip", "epub"
    ],
    accept_multiple_files=True
)

st.markdown("---")
st.markdown("### 2. Or Convert URL (YouTube / Web)")
url_input = st.text_input("Paste YouTube or Web URL (opsional):", placeholder="https://www.youtube.com/watch?v=...")

if st.button("🔄 Converting", type="primary"):
    if not uploaded_files and not url_input.strip():
        st.warning("Upload at least 1 file or enter a URL!")
    else:
        zip_buffer = io.BytesIO()
        success_count = 0
        failed_count = 0
        
        with st.spinner("Processing... Please be patient (audio transcription or image OCR might take a bit longer)."):
            md = MarkItDown()
            
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        tmp_path = None
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_path = tmp_file.name

                            result = md.convert(tmp_path)
                            markdown_text = result.text_content
                            
                            base_name = os.path.splitext(uploaded_file.name)[0]
                            output_filename = f"{base_name}.md"
                            
                            zip_file.writestr(output_filename, markdown_text)
                            success_count += 1
                        except Exception as e:
                            failed_count += 1
                            st.warning(f"Failed to process file `{uploaded_file.name}`: {e}")
                        finally:
                            if tmp_path and os.path.exists(tmp_path):
                                os.unlink(tmp_path)
                
                if url_input.strip():
                    try:
                        result = md.convert(url_input.strip())
                        markdown_text = result.text_content
                        
                        output_filename = "youtube_or_web_content.md"
                        zip_file.writestr(output_filename, markdown_text)
                        success_count += 1
                    except Exception as e:
                        failed_count += 1
                        st.warning(f"Failed to process URL `{url_input}`: {e}")

        if success_count > 0:
            st.success(f"Successfully converted **{success_count} items**! {f'({failed_count} items failed)' if failed_count > 0 else ''}")
            
            zip_buffer.seek(0)
            st.download_button(
                label="📥 Download All Results (.zip)",
                data=zip_buffer,
                file_name="markdown_results.zip",
                mime="application/zip",
                type="primary"
            )
        else:
            st.error("No items were successfully converted.")
            