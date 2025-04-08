from include.s3_handler import S3Handler
from fastapi.responses import StreamingResponse
from fastapi import APIRouter
from include.llm_functions import LLMHelper
import json
from typing import Optional, List

chat_router = APIRouter()

s3_handler = S3Handler()


def send_image_to_llm(prompt: str, image_path: str, streaming: bool = True):
    temp_file = s3_handler.get_object(image_path, local_filename='temp_file')
    llm_helper = LLMHelper(system_prompt=prompt)
    return llm_helper.get_response_to_image_request(temp_file,
                                                    streaming=streaming)


def get_file_with_image_descriptions(folder: str,
                                     images_description_path: str = None):
    images_description_key = \
        f'{folder}/images_descriptions/{images_description_path}'
    temp_file_path = 'temp_file.json'
    s3_handler.get_object(images_description_key,
                          temp_file_path)
    with open(temp_file_path, "r") as f:
        images_description = json.load(f)
    temp_file_path = s3_handler.get_object(folder + '/parsed_file.md',
                                           local_filename='temp_file')
    with open(temp_file_path, 'r') as f:
        source_file_md = f.read()
    user_prompt = f'''File Name: {folder}
    {source_file_md}'''
    if images_description_path:
        user_prompt += \
            f"\nThese are the images: {images_description['images']}"
    return user_prompt


def get_last_index_from_s3(folder_name, path, must_exist=False):
    images_descriptions_files = s3_handler\
        .list_objects(prefix=folder_name + path,
                      recursive=True)
    if not images_descriptions_files and not must_exist:
        index = 1
    elif not images_descriptions_files and must_exist:
        raise Exception("Image Description Doesn't Exist")
    else:
        indexes = [int(f.split('/')[-1].split('.')[0].split('_')[-1])
                   for f in images_descriptions_files]
        index = max(indexes) + 1
    return index


def get_last_file_path(folder_name, dir_path, file_name):
    index = get_last_index_from_s3(folder_name, f'{dir_path}',
                                   must_exist=True) - 1
    updated_file = file_name.format(index=index)
    return updated_file


def send_text_to_llm(prompt: str, folder: str,
                     images_description_path: str = None,
                     streaming: bool = True):
    user_prompt = get_file_with_image_descriptions(folder,
                                                   images_description_path)
    llm_helper = LLMHelper(system_prompt=prompt)
    return llm_helper.get_response_to_text_request(text_request=user_prompt,
                                                   streaming=streaming)


def send_texts_to_llm(prompt: str, folders: List[str],
                      streaming: bool = True):
    user_prompts = ''
    for folder in folders:
        images_description_path = get_last_file_path(
            folder,
            '/images_descriptions/',
            'images_description_{index}.json')
        user_prompt = get_file_with_image_descriptions(
            folder,
            images_description_path)
        user_prompts += '-'*15 + user_prompt + '-'*15
    llm_helper = LLMHelper(system_prompt=prompt)
    return llm_helper.get_response_to_text_request(text_request=user_prompts,
                                                   streaming=streaming)


@chat_router.get("/get_image_description")
async def get_image_description(prompt: str, image_path: str):
    return StreamingResponse(send_image_to_llm(prompt, image_path),
                             media_type='text/plain')


@chat_router.post("/load_images_descriptions")
async def load_images_descriptions(prompt: str, folder_name: str):
    images_paths = s3_handler.list_objects(prefix=folder_name + '/images/',
                                           recursive=True)
    images_descriptions = {'prompt': prompt, 'images': {}}
    for image_path in images_paths:
        image_name = image_path.split('/')[-1]
        images_descriptions['images'][image_name] \
            = send_image_to_llm(prompt, image_path, streaming=False)
    index = get_last_index_from_s3(folder_name, '/images_descriptions/')
    s3_folder = f'{folder_name}/images_descriptions'
    s3_path = f'{s3_folder}/images_description_{index}.json'
    s3_handler.put_object(s3_path,
                          json.dumps(images_descriptions).encode('utf-8'))
    return s3_path


@chat_router.get("/get_parsed_file")
async def get_parsed_file(prompt: str, folder_name: str,
                          images_description_path: Optional[str] = None):
    if not images_description_path:
        images_description_path = get_last_file_path(
            folder_name, '/images_descriptions/',
            'images_description_{index}.json')
    return StreamingResponse(
        send_text_to_llm(prompt=prompt,
                         folder=folder_name,
                         images_description_path=images_description_path),
        media_type='text/plain')


@chat_router.post("/load_parsed_file")
async def load_parsed_file(prompt: str, folder_name: str,
                           images_description_path: Optional[str] = None):
    if not images_description_path:
        images_description_path = get_last_file_path(
            folder_name, '/images_descriptions/',
            'images_description_{index}.json')
    llm_output = send_text_to_llm(
        prompt=prompt,
        folder=folder_name,
        images_description_path=images_description_path,
        streaming=False)
    start_index = llm_output.find('{')
    json_str_llm_output = llm_output[start_index:]
    json_llm_output = json.loads(json_str_llm_output)
    index = get_last_index_from_s3(folder_name, '/parsed_document/')
    s3_path = f'{folder_name}/parsed_document/parsed_document_{index}.json'
    final_json = {
        'data': json_llm_output,
        'prompt': prompt,
        'images_description_path': images_description_path
    }
    s3_handler.put_object(s3_path,
                          json.dumps(final_json).encode('utf-8'))


@chat_router.get("/get_common_schema")
async def get_common_schema(prompt: str, folders: str):
    folders = folders.split(',')
    return StreamingResponse(
        send_texts_to_llm(prompt=prompt,
                          folders=folders),
        media_type='text/plain')


@chat_router.post("/load_common_schema")
async def load_common_schema(prompt: str, folders: str):
    folders = folders.split(',')
    llm_output = send_texts_to_llm(
        prompt=prompt,
        folders=folders,
        streaming=False)
    start_index = llm_output.find('{')
    json_str_llm_output = llm_output[start_index:]
    json_llm_output = json.loads(json_str_llm_output)
    index = get_last_index_from_s3('common_schemas', '/common_schemas_jsons/')
    s3_path = f'common_schemas/common_schemas_jsons/common_schema_{index}.json'
    final_json = {
        'schema': json_llm_output,
        'prompt': prompt,
        'files': folders
    }
    s3_handler.put_object(s3_path,
                          json.dumps(final_json).encode('utf-8'))
