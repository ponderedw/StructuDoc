from fastapi import APIRouter, UploadFile, File
from typing import Annotated, Optional
from include.s3_handler import S3Handler
from include.document_parsing import DocumentParse
from fastapi_modules.helper.helper_functions import \
    help_upload_source_file_to_s3, \
    help_upload_parsed_source_file_to_s3, help_upload_extracted_images_to_s3
import json


chat_router = APIRouter()

s3_handler = S3Handler()


def upload_metadata_json(file_key, metadata_file_key):
    metadata = {'source_file': file_key}
    s3_handler.put_object(metadata_file_key,
                          json.dumps(metadata).encode('utf-8'))


@chat_router.post("/upload_source_file_to_s3")
async def upload_source_file_to_s3(file: Annotated[UploadFile, File()],
                                   path: Optional[str] = None):
    file_content = await file.read()
    file_name = file.filename
    temp_file_path, folder, file_key = \
        help_upload_source_file_to_s3(s3_handler, file_name, file_content,
                                      path)
    upload_metadata_json(file_key, folder + '/metadata.json')
    document_parse = DocumentParse(source_document_local_path=temp_file_path,
                                   image_folder='images')
    help_upload_parsed_source_file_to_s3(s3_handler, document_parse, folder)
    help_upload_extracted_images_to_s3(s3_handler, document_parse, folder)
    return {"filename": file_key, "message": "File uploaded successfully"}


@chat_router.post("/parse_s3_path")
async def parse_s3_path(path: str):
    temp_file_path = s3_handler\
        .get_object(path,
                    local_filename='temp_file')
    document_parse = DocumentParse(source_document_local_path=temp_file_path,
                                   image_folder='images')
    folder = path.rsplit('/', 1)[0] \
        + '/structudoc_' + path.split('/')[-1].split('.')[0]
    upload_metadata_json(path, folder + '/metadata.json')
    help_upload_parsed_source_file_to_s3(s3_handler, document_parse, folder)
    help_upload_extracted_images_to_s3(s3_handler, document_parse, folder)
    return {"filename": folder, "message": "File parsed successfully"}


@chat_router.get("/get_all_the_folders")
async def get_all_the_folders():
    all_the_files = s3_handler.list_objects(recursive=True)
    print(all_the_files)
    all_the_files = [f.rsplit('/', 1)[0]
                     for f in all_the_files
                     if f.split('/')[-2].startswith("structudoc_")]
    all_the_files = list(set(all_the_files))
    all_the_files = [{
        'folder_path': f,
        'folder_name': f.rsplit('/', 1)[1]
    } for f in all_the_files]
    return all_the_files
