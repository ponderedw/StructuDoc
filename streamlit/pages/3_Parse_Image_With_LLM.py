from st_ant_tree import st_ant_tree
import streamlit as st
from helper import build_tree, get_from_backend_streaming
from helper import get_from_backend, post_to_backend

paths = get_from_backend(backend_method='s3_interactions/get_all_the_folders')
paths = [folder['folder_path'] for folder in paths]
tree = build_tree(paths)['children']


with st.form("user_form"):
    selected_values = st_ant_tree(
        treeData=tree,
        treeCheckable=True,
        allowClear=True,
        only_children_select=True,
        placeholder='Choose Files You Want to Parse'
    )
    prompt_value = ''
    with open('streamlit/default_images_prompt.txt', 'r') as f:
        prompt_value = f.read()
    prompt = st.text_area("Prompt",
                          value=prompt_value,
                          height=200)
    submitted = st.form_submit_button("View Result")
    submitted_save = st.form_submit_button("Save Result")

if submitted:
    if selected_values:
        for folder in selected_values:
            with st.expander(folder):
                backend_method = 's3_interactions/get_all_the_images'
                images = get_from_backend(backend_method=backend_method,
                                          folder_path=folder)
                images = {k: v for k, v in images.items()}
                backend_mathod = 'parse_data_with_llm/get_image_description'
                for image_name, image_bytes in images.items():
                    st.markdown(f"""## {image_name}

![{image_name}](data:image/{image_name.split('.')[-1]};base64,{image_bytes})

                            """,
                                unsafe_allow_html=True)
                    st.write_stream(get_from_backend_streaming(
                        backend_method=backend_mathod,
                        params={
                            'prompt': prompt,
                            'image_path': folder + '/images/' + image_name
                        }
                    )
                                    )
    else:
        st.warning('Please Choose At Least One Folder')

if submitted_save:
    if selected_values:
        backend_method = 'parse_data_with_llm/load_images_descriptions'
        for folder in selected_values:
            data = post_to_backend(backend_method=backend_method,
                                   params={'prompt': prompt,
                                           'folder_name': folder})
            st.write(f'Load is finished for {folder}')
            st.write(data)
    else:
        st.warning('Please Choose At Least One Folder')
