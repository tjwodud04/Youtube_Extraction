from abc import ABC
from dataclasses import dataclass
from typing import Any, Callable, Generic, List, TypeVar

import uuid
from uuid import UUID

TMessageOptions = TypeVar("TMessageOptions")

@dataclass
class Message:
    role: str
    content: str
    id: UUID

    def __init__(self, role: str, content: str, id: UUID = None):
        self.role = role
        self.content = content
        self.id = id if id else uuid.uuid4()

class GptThread(ABC, Generic[TMessageOptions]):
    def add_message(self, message: Message, options: TMessageOptions = None):
        pass

    def remove_message(self, message: Message) -> bool:
        """
        Remove the given message from the thread.

        Note that not all clients support this operation.
        """
        pass

    def __iter__(self):
        pass

class GptClient(ABC):
    def __init__(self):
        pass

    def create_thread(self, thread_options = None) -> GptThread:
        pass
    
    def execute_completion(self, thread: GptThread, message_options: Callable[[int, Message], Any] = None) -> List[Message]:
        """
        Execute a completion on the given thread, adding the responses to the thread.

        Args:
            thread: The thread to execute the completion on.
            message_options: A function that returns the options for a given message index and message.

        Returns:
            The list of responses added to the thread from the completion.
        """
        pass

@dataclass
class MemoryGptThreadOptions:
    # The maximum number of messages before the oldest non-preserved message is deleted
    max_message_window: int = None

@dataclass
class MemoryGptMessageOptions:
    # If true, the message will always be preserved in the history
    preserve_message: bool = False
    # If true, the message will be deleted from the history after the completion
    delete_message: bool = False

class MemoryGptThread(GptThread[MemoryGptMessageOptions]):
    options: MemoryGptThreadOptions
    messages: List[Message]
    message_options: List[MemoryGptMessageOptions]

    def __init__(self, thread_options: MemoryGptThreadOptions = None):
        super().__init__()
        if not thread_options:
            thread_options = MemoryGptThreadOptions()
        self.options = thread_options

        self.messages = []
        self.message_options = []
        self._message_window_size = 0

    def add_message(self, message: Message, options: MemoryGptMessageOptions = None):
        # Default options
        if not options:
            options = MemoryGptMessageOptions()
        # Do not add deleted messages to the history
        if options.delete_message:
            return
        
        self.messages.append(message)
        self.message_options.append(options)

        # Increment the message window size
        if not options.preserve_message:
            self._message_window_size += 1

        # Trim the message window if it exceeds the maximum size
        if self.options.max_message_window is not None and \
            self._message_window_size > self.options.max_message_window:
            # Find first non-preserved message
            index = next((i for i, options in enumerate(self.message_options) if not options.preserve_message), None)

            if index is not None:
                self._remove_message(index)

    def remove_message(self, message: Message) -> bool:
        """
        Remove the given message from the thread, even if it is marked as preserved.

        Args:
            message: The message to remove.

        Returns:
            True if the message was removed, False if it was not found.
        """
        # Find the message in the list
        index = next((i for i, m in enumerate(self.messages) if m.id == message.id), None)

        if index is None:
            return False
        
        self._remove_message(index)
        return True
    
    def _remove_message(self, message_index: int) -> bool:
        preserved = self.message_options[message_index].preserve_message

        # Remove the message
        del self.messages[message_index]
        del self.message_options[message_index]

        # Decrement the message window size
        if not preserved:
            self._message_window_size -= 1

    def __getitem__(self, key):
        return self.messages[key]
    
    def __len__(self):
        return len(self.messages)

    def __iter__(self):
        return iter(self.messages)