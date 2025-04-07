import os
import base64
from langchain_core.messages import HumanMessage


class LLMHelper:
    def __init__(self, system_prompt) -> None:
        self.system_prompt = system_prompt

    @property
    def messages(self):
        _messages = [
            ('system', self.system_prompt),
        ]
        return _messages

    @property
    def llm(self):
        model_type, model_id = os.environ.get('LLM_MODEL').split(':', 1)
        if model_type == 'Bedrock':
            from langchain_aws import ChatBedrock
            _llm = ChatBedrock(
                model_id=model_id,
                model_kwargs=dict(temperature=0, max_tokens=4096,),
            )
        elif model_type == 'Anthropic':
            from langchain_anthropic import ChatAnthropic
            _llm = ChatAnthropic(
                model=model_id,
                temperature=0,
                max_tokens=4096,
            )
        return _llm

    def invoke_model_return(self, messages):
        return self.llm.invoke(self.messages +
                               [*messages]).content

    def invoke_model(self, messages):
        for chunk in self.llm.stream(self.messages +
                                     [*messages]):
            yield chunk.content

    def get_response_to_text_request(self, text_request: str, streaming: bool):
        if streaming:
            return self.invoke_model([('human', text_request)])
        else:
            return self.invoke_model_return([('human', text_request)])

    def get_response_to_image_request(self, image_path: str, streaming: bool):
        file_type = image_path.split('.')[-1]
        with open(image_path, 'rb') as image_f:
            image_content = image_f.read()
        image_content = base64.b64encode(image_content).decode('utf-8')
        message = HumanMessage(content=[
            {"type": "image_url",
                "image_url": {
                    "url": f"data:image/{file_type};base64,{image_content}"
                    }},
            ],
        )
        if streaming:
            return self.invoke_model([message])
        else:
            return self.invoke_model_return([message])
