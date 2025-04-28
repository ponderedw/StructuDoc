import subprocess
import os
from docx import Document
import shutil
from pdf2docx import Converter


class DocumentParse:
    def __init__(self, source_document_local_path, image_folder):
        self.source_document_local_path = source_document_local_path
        self.source_document_extension = source_document_local_path\
            .split('.')[-1]
        self.markdown_local_path = source_document_local_path.split('.')[0] \
            + '.md'
        self.images_folder = image_folder

    @staticmethod
    def recreate_folder(folder_path):
        """Deletes a folder if it exists and recreates it."""
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)  # Remove the folder and its contents
        os.makedirs(folder_path)  # Create the folder again
        print(f"Folder '{folder_path}' has been recreated.")

    @staticmethod
    def convert_pdf_to_word(pdf_local_path, docx_local_path):
        cv = Converter(pdf_local_path)
        cv.convert(docx_local_path, start=0, end=None)
        cv.close()

    def convert_word_to_markdown(self):
        command = [
            "pandoc",
            self.source_document_local_path,
            "-f", "docx",
            "-t", "gfm",
            "-o", self.markdown_local_path
        ]
        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print("Command failed with error:", e.stderr)
            print("Exit code:", e.returncode)
            raise e

    def convert_file_to_markdown(self):
        if self.source_document_extension == 'docx':
            self.convert_word_to_markdown()
        return self.markdown_local_path

    def extract_images_from_word(self):
        doc = Document(self.source_document_local_path)
        DocumentParse.recreate_folder(self.images_folder)
        for rel in doc.part.rels:
            if 'image' in doc.part.rels[rel].target_ref:
                if not doc.part.rels[rel].is_external:
                    image_part = doc.part.rels[rel].target_part
                    image_data = image_part.blob
                    image_name = image_part._partname.split('/')[-1]
                    image_path = os.path.join(self.images_folder,
                                              image_name)
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_data)

    def extract_images_from_file(self):
        if self.source_document_extension == 'docx':
            self.extract_images_from_word()
        return self.images_folder
