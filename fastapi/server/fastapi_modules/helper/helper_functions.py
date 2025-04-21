import os


main_folder_prefix = 'structudoc'


def get_folder_path(filename, path):
    folder_name = main_folder_prefix + '_' +\
        filename.split('/')[-1].split('.')[0]
    if path:
        return path + '/' + folder_name
    return folder_name


def help_upload_source_file_to_s3(s3_handler, file_name, file_content, path):
    folder_name, extension = file_name.split('.')
    main_folder = get_folder_path(file_name, path)
    file_key = f'{main_folder}/{folder_name}.{extension}'
    s3_handler.put_object(key=file_key,
                          file_bytes=file_content)
    temp_file_path = f'temp_file.{extension}'
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content)
    return (temp_file_path, main_folder, file_key)


def help_upload_parsed_source_file_to_s3(s3_handler, document_parse, folder):
    md_path = document_parse.convert_file_to_markdown()
    with open(md_path, "rb") as f:
        s3_handler.put_object(key=f'{folder}/parsed_file.md',
                              file_bytes=f.read())


def help_upload_extracted_images_to_s3(s3_handler, document_parse, folder):
    s3_handler.remove_all_files_indir(
        f'{folder}/{document_parse.images_folder}')
    document_parse.extract_images_from_file()
    for filename in os.listdir(document_parse.images_folder):
        file_path = os.path.join(document_parse.images_folder, filename)
        with open(file_path, 'rb') as f:
            s3_handler.put_object(key=f'{folder}/images/{filename}',
                                  file_bytes=f.read())


def get_last_index_from_s3(s3_handler, folder_name, path, must_exist=False):
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


def get_last_file_path(s3_handler, folder_name, dir_path, file_name):
    index = get_last_index_from_s3(s3_handler, folder_name, f'{dir_path}',
                                   must_exist=True) - 1
    updated_file = file_name.format(index=index)
    return updated_file
