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
st.write("Upload **banyak file sekaligus** untuk diubah menjadi format Markdown menggunakan `markitdown` by Microsoft.")
st.write("Support untuk file-file:")
st.write(file_formats)

# Widget untuk upload banyak file sekaligus
uploaded_files = st.file_uploader(
    "Pilih file-file Anda", 
    type=["pdf", "docx", "pptx", "xlsx", "jpg", "png", "mp3", "wav", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Total file dipilih: **{len(uploaded_files)} file**")
    
    if st.button("🔄 Konversi Semua ke Markdown", type="primary"):
        # Buat buffer ZIP di memori untuk menampung semua hasil konversi
        zip_buffer = io.BytesIO()
        
        with st.spinner("Sedang memproses file... Mohon tunggu sebentar."):
            md = MarkItDown()
            success_count = 0
            failed_count = 0
            
            # Membuka ZIP file builder di memori
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for uploaded_file in uploaded_files:
                    tmp_path = None
                    try:
                        # Simpan file sementara agar bisa dibaca MarkItDown
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name

                        # Proses konversi
                        result = md.convert(tmp_path)
                        markdown_text = result.text_content
                        
                        # Buat nama file output dengan ekstensi .md
                        base_name = os.path.splitext(uploaded_file.name)[0]
                        output_filename = f"{base_name}.md"
                        
                        # Masukkan isi markdown ke dalam ZIP file
                        zip_file.writestr(output_filename, markdown_text)
                        success_count += 1
                        
                    except Exception as e:
                        failed_count += 1
                        st.warning(f"Gagal memproses `{uploaded_file.name}`: {e}")
                    finally:
                        # Bersihkan file temporary individual
                        if tmp_path and os.path.exists(tmp_path):
                            os.unlink(tmp_path)
            
            if success_count > 0:
                st.success(f"Berhasil mengkonversi **{success_count} file**! {f'({failed_count} file gagal)' if failed_count > 0 else ''}")
                
                # Kembalikan posisi pointer buffer ke awal sebelum didownload
                zip_buffer.seek(0)
                
                # Tombol download untuk file ZIP hasil konversi
                st.download_button(
                    label="📥 Download Semua Hasil (.zip)",
                    data=zip_buffer,
                    file_name="markdown_results.zip",
                    mime="application/zip",
                    type="primary"
                )
            else:
                st.error("Tidak ada file yang berhasil dikonversi.")