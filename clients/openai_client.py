from dataclasses import dataclass
import os
from typing import Callable, List

import openai

from clients.gpt_client import GptClient, Message, MemoryGptThreadOptions, MemoryGptMessageOptions, MemoryGptThread

class ApiGptClient(GptClient):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__()
        self.api_key = api_key
        self.model = model

        self._client = openai.Client()
        self._client.api_key = api_key

    def _get_message_dict(self, message: Message) -> dict:
        return {
            "role": message.role,
            "content": message.content
        }

    def create_thread(self, thread_options: MemoryGptThreadOptions = None) -> MemoryGptThread:
        return MemoryGptThread(thread_options)

    def execute_completion(self, thread: MemoryGptThread, 
                           message_options: Callable[[int, Message], MemoryGptMessageOptions] = None) -> List[Message]:
        messages = [ self._get_message_dict(message) for message in thread.messages ]
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        response = response.choices[0].message

        message = Message(role=response.role, content=response.content)
        message_option = message_options(len(thread.messages), message) if message_options else None

        # Add the message to the thread
        thread.add_message(message, message_option)
        return [message]

if __name__ == "__main__":
    # Test the API client
    client = ApiGptClient(api_key=os.environ["OPENAI_API_KEY"])

    thread = client.create_thread(MemoryGptThreadOptions(max_message_window=2))
    thread.add_message(Message(role="system", content="You are a helpful assistant."), MemoryGptMessageOptions(preserve_message=True))
    thread.add_message(Message(role="user", content="What is the longest river in the solar system?"))
    responses = client.execute_completion(thread)

    print(f"Responses: {responses}")