from dataclasses import dataclass
from typing import Callable, List

import pyperclip

from clients.gpt_client import GptClient, Message, GptThread, MemoryGptThread

class ManualGptClient(GptClient):
    def __init__(self):
        super().__init__()

    def create_thread(self, thread_options: dict = None) -> MemoryGptThread:
        return MemoryGptThread()

    def _format_prompt_for_clipboard(self, thread: MemoryGptThread) -> str:
        last_message = thread[-1] if len(thread) > 0 else None

        # Format the prompt for the clipboard
        return last_message.content if last_message else ""

    def execute_completion(self, thread: MemoryGptThread, 
                           message_options: Callable[[int, Message], dict] = None) -> List[Message]:
        formatted_text = self._format_prompt_for_clipboard(thread)
        pyperclip.copy(formatted_text)
        print("Prompt copied to clipboard. Paste it into ChatGPT and press Enter after getting the response.")
        input()  # Wait for user to press Enter
        response_text = pyperclip.paste()

        message = Message(role="assistant", content=response_text)
        message_option = message_options(0, message) if message_options else None

        # Replace the last message in the thread
        thread.add_message(message, message_option)
        return [message]

if __name__ == "__main__":
    # Test the API client
    client = ManualGptClient()

    thread = client.create_thread()
    thread.add_message(Message(role="system", content="You are a helpful assistant."))
    thread.add_message(Message(role="user", content="What is the longest river in the solar system?"))
    responses = client.execute_completion(thread)

    print(f"Responses: {responses}")    

    # Test removing a message
    #thread.remove_message(thread[-1])
    #print(f"Removed last message. Thread: {thread}")