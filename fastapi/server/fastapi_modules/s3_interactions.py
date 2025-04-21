from fastapi import APIRouter, UploadFile, File, Form
from typing import Annotated, Optional
from include.s3_handler import S3Handler
from include.document_parsing import DocumentParse
from fastapi_modules.helper.helper_functions import \
    help_upload_source_file_to_s3, \
    help_upload_parsed_source_file_to_s3, help_upload_extracted_images_to_s3, \
    main_folder_prefix, get_folder_path, get_last_index_from_s3, \
    get_last_file_path
import json
import base64
import re
from fastapi_modules.common_values import images_description_file_temp, \
    images_description_folder


chat_router = APIRouter()

s3_handler = S3Handler()


def upload_metadata_json(file_key, metadata_file_key):
    metadata = {'source_file': file_key}
    s3_handler.put_object(metadata_file_key,
                          json.dumps(metadata).encode('utf-8'))


def get_markdown_with_images_helper(markdown, images):
    def replacer(match):
        src = match.group(1)
        filename = src.split("/")[-1]
        if filename in images:
            mime = f"image/{filename.split('.')[1]}"
            b64 = images[filename].decode("utf-8")
            return f'<img src="data:{mime};base64,{b64}" />'
        else:
            return match.group(0)
    pattern = r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>'
    return re.sub(pattern, replacer, markdown.decode("utf-8"))


def has_valid_extension(key, extensions):
    return any(key.lower().endswith(ext) for ext in extensions)


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
    folder = get_folder_path(path.split('/')[-1].split('.')[0],
                             path.rsplit('/', 1)[0] if '/' in path
                             else '')
    upload_metadata_json(path, folder + '/metadata.json')
    help_upload_parsed_source_file_to_s3(s3_handler, document_parse, folder)
    help_upload_extracted_images_to_s3(s3_handler, document_parse, folder)
    return {"filename": folder, "message": "File parsed successfully"}


@chat_router.get("/get_all_the_folders")
async def get_all_the_folders():
    all_the_files = s3_handler.list_objects(recursive=True)
    all_the_files = [f.rsplit('/', 1)[0]
                     for f in all_the_files
                     if len(f.split('/')) > 1 and
                     f.split('/')[-2].startswith(f"{main_folder_prefix}_")]
    all_the_files = list(set(all_the_files))
    all_the_files = [{
        'folder_path': f,
        'folder_name': f.rsplit('/', 1)[-1]
    } for f in all_the_files]
    return all_the_files


@chat_router.get("/get_all_the_images")
async def get_all_the_images(folder_path: str):
    images_paths = s3_handler.list_objects(prefix=f'{folder_path}/images/',
                                           recursive=True)
    images_bytes = {}
    for image_path in images_paths:
        images_bytes[image_path.split('/')[-1]] = \
            base64.b64encode(s3_handler.get_object_bytes(image_path))
    return images_bytes


@chat_router.get("/get_markdown")
async def get_markdown(folder_path: str):
    markdown_bytes = \
        s3_handler.get_object_bytes(f'{folder_path}/parsed_file.md')
    return markdown_bytes


@chat_router.get("/get_markdown_with_images")
async def get_markdown_with_images(folder_path: str):
    markdown_bytes = \
        s3_handler.get_object_bytes(f'{folder_path}/parsed_file.md')
    images_paths = s3_handler.list_objects(prefix=f'{folder_path}/images/',
                                           recursive=True)
    images_bytes = {}
    for image_path in images_paths:
        images_bytes[image_path.split('/')[-1]] = \
            base64.b64encode(s3_handler.get_object_bytes(image_path))
    markdown_with_images = get_markdown_with_images_helper(markdown_bytes,
                                                           images_bytes)
    return markdown_with_images


@chat_router.get("/get_images_explanations_paths")
async def get_images_explanations_paths(folder_path: str):
    images_descriptions_paths = s3_handler.list_objects(
        prefix=f'{folder_path}/{images_description_folder}/',
        recursive=True)
    return [f.split('/')[-1] for f in images_descriptions_paths]


@chat_router.get("/get_images_explanation")
async def get_images_explanation(folder_path: str, description_path: str):
    description_json = \
        s3_handler.get_object_bytes(
            f'{folder_path}/{images_description_folder}/{description_path}')
    return description_json


@chat_router.get("/receive_json_parsings_paths")
async def receive_json_parsings_paths(folder_path: str):
    json_parsings_paths = s3_handler.list_objects(
        prefix=f'{folder_path}/parsed_document/',
        recursive=True)
    return [f.split('/')[-1] for f in json_parsings_paths]


@chat_router.get("/receive_json_parsings")
async def receive_json_parsings(folder_path: str, parsing_path: str):
    description_json = \
        s3_handler.get_object_bytes(
            f'{folder_path}/parsed_document/{parsing_path}')
    return description_json


@chat_router.get("/is_folder_exists")
async def is_folder_exists(file_name: str, path: Optional[str] = None):
    folder_path = get_folder_path(file_name, path)
    files_in_folder = s3_handler.list_objects(prefix=f'{folder_path}/',
                                              recursive=True)
    return {'is_exist': len(files_in_folder) > 0,
            'folder_path': folder_path}


@chat_router.get("/get_all_the_common_schemas")
async def get_all_the_common_schemas(folders: Optional[str] = None):
    common_schemas_paths = s3_handler.list_objects(prefix='common_schemas/',
                                                   recursive=True)
    common_schemas = []
    folders_list = None if not folders else folders.split(',')
    for common_schema_path in common_schemas_paths:
        json_bytes = s3_handler.get_object_bytes(object_key=common_schema_path)
        json_str = json_bytes.decode('utf-8')
        if folders_list:
            if bool(set(json.loads(json_str)['files']) & set(folders_list)):
                common_schemas.append(common_schema_path.rsplit('/')[-1])
        else:
            common_schemas.append(common_schema_path.rsplit('/')[-1])
    return common_schemas


@chat_router.get("/get_common_schema_json")
async def get_common_schema_json(common_schema_path: str):
    json_bytes = s3_handler.get_object_bytes(
        object_key=f'common_schemas/common_schemas_jsons/{common_schema_path}')
    return json.loads(json_bytes.decode('utf-8'))


@chat_router.get("/get_files_list")
async def get_files_list(extensions: Optional[str] = None):
    extensions = extensions.split(',')
    final_files_list = []
    files_list = s3_handler.list_objects(recursive=True)
    final_files_list = [file_path for file_path in files_list
                        if has_valid_extension(file_path, extensions)]
    return final_files_list


@chat_router.post("/upload_parsed_file")
async def upload_parsed_file(folder_name: Annotated[str, Form()],
                             subfolder_name: Annotated[str, Form()],
                             file_template: Annotated[str, Form()],
                             parsed_json_file: Annotated[UploadFile, File()]):
    index = get_last_index_from_s3(s3_handler, folder_name,
                                   f'/{subfolder_name}/')
    parsed_json = await parsed_json_file.read()
    s3_folder = f'{folder_name}/{subfolder_name}'
    s3_path = f'{s3_folder}/{file_template}_{index}.json'
    s3_handler.put_object(s3_path,
                          json.dumps(
                              json.loads(parsed_json)).encode('utf-8'))
    return s3_path


@chat_router.get("/get_last_image_file_name")
async def get_last_image_file_name(folder_name: str):
    last_image_path = get_last_file_path(
                s3_handler,
                folder_name,
                f'/{images_description_folder}/',
                f'{images_description_file_temp}')
    return last_image_path.split('/')[-1]
