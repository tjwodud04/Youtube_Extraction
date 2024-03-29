"""
MIT License

Copyright (c) 2023 Kristian S. Stangeland
"""
import streamlit as st
import argparse
import os
import openai
import pysrt
import logging

from time import sleep
from clients.gpt_client import GptClient, GptThread, Message, MemoryGptThreadOptions
from clients.manual_client import ManualGptClient
from clients.openai_client import ApiGptClient
from subtitles import IndexedSubtitle, indexed_subtitles_to_text, parse_indexed_subtitles
from utils import get_batches, resize_chunk

def translate_chunk(chunk: list[IndexedSubtitle],
                    client: GptClient, thread: GptThread,
                    source_lang: str, target_lang: str, dry_run=False, retries: int = 3):
    """
    Translate a chunk of subtitles from Japanese to English.

    Args:
        chunk: A list of indexed subtitles to translate.
        client: The OpenAI client to use.
        source_lang: The source language of the subtitles.
        target_lang: The target language of the subtitles.
        dry_run: Whether to run the script without calling OpenAI to simulate output.
        retries: The number of times to retry the translation if it fails.
    """
    prompt = f"아래 자막을 {source_lang}에서 {target_lang}(으)로 번역해주세요. 각 자막 사이에 있는 번호가 동기화를 위해 필요하므로 그대로 유지해주세요:\n\n"
    # prompt = f"Please translate the following subtitles from {source_lang} to {target_lang}. Keep the numbered lines in between each subtitle as they are needed for synchronization:\n\n"
    prompt += indexed_subtitles_to_text(chunk)

    attempt = 1
    retry_delay = 1  # seconds

    logging.debug(f"Invoking OpenAI with prompt: {prompt}")

    if dry_run:  # In dry-run mode, don't call OpenAI
        print("Dry-run mode - skipping OpenAI API call.")
        return chunk

    # The messages to send to the API
    prompt_message = Message(role="user", content=prompt)
    thread.add_message(prompt_message)

    responses = None
    success = False

    while attempt <= retries:
        try:
            responses = client.execute_completion(thread)

            response = responses[0]
            translated_chunk = list(parse_indexed_subtitles(response.content))

            # If translation does not have the expected line count, adjust accordingly
            if len(translated_chunk) != len(chunk):
                if attempt == retries:
                    logging.warning(
                        f"Attempt {attempt}: Received {len(translated_chunk)} translated lines, expected {len(chunk)}. Truncating or padding the translation to match the expected line count.")

                    offset = chunk[0].index if len(chunk) > 0 else 0
                    translated_chunk = resize_chunk(translated_chunk, len(chunk),
                                                    lambda index: IndexedSubtitle(index + offset, ""))

                else:
                    logging.warning(
                        f"Attempt {attempt}: Received {len(translated_chunk)} translated lines, expected {len(chunk)}. Retrying.")

                    # Retry
                    attempt += 1
                    continue
            else:
                logging.info(f"Received {len(translated_chunk)} translated lines.")

            success = True
            return translated_chunk

        except openai.OpenAIError as e:
            logging.error(f"An OpenAI error occurred: {e}")
            attempt += 1

            if attempt > retries:
                sleep(retry_delay)
                retry_delay *= 2
            else:
                # If we've reached the max retries, throw the error
                raise e

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e

        finally:
            # Remove completion if the attempt failed
            if not success:
                for response in responses:
                    thread.remove_message(response)


# Main function to process the SRT file and translate it
def process_srt(file_path, output_file_path, client: GptClient, thread: GptThread, source_lang: str, target_lang: str,
                dry_run=False):

    subs = pysrt.open(file_path, encoding='utf-8')

    indexed_subs = [IndexedSubtitle(sub.index, sub.text) for sub in subs]
    chunks = list(get_batches(indexed_subs, 40))

    for chunk in chunks:
        translated_chunk = translate_chunk(chunk, client, thread,
                                           source_lang=source_lang, target_lang=target_lang, dry_run=dry_run)

        # Assume translated_chunk is a single string, here's how to parse and apply the translations using your parse_chunk function
        for line in translated_chunk:
            # -1 because pysrt works with 0-based index, but SRT files are 1-based.
            subs[line.index - 1].text = line.text

    # Save the modified subs back into an SRT file.
    subs.save(output_file_path, encoding='utf-8')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate an SRT file from Japanese to English.")
    parser.add_argument("input_srt", help="The input SRT file to be translated.")
    parser.add_argument("output_srt", help="The output SRT file to save the translation.")
    parser.add_argument("--source-lang", help="The source language of the SRT file.", default="Japanese")
    parser.add_argument("--target-lang", help="The target language for the translation.", default="English")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run the script without calling OpenAI to simulate output.")
    parser.add_argument("--api-key",
                        help="The OpenAI API key to use. If not specified, the OPENAI_API_KEY environment variable will be used.",
                        default=os.environ.get("OPENAI_API_KEY", None))
    parser.add_argument("--client-type", help="The type of client to use. If not specified, defaults to 'api'.",
                        choices=["api", "manual"], default="api")
    args = parser.parse_args()

    # Set up client
    if args.client_type.lower() == "api":
        client = ApiGptClient(args.api_key)
        thread = client.create_thread(thread_options=MemoryGptThreadOptions(max_message_window=5))
        thread.add_message(Message(role="system", content="You are a helpful assistant."))
    elif args.client_type.lower() == "manual":
        client = ManualGptClient()
        thread = client.create_thread()
    else:
        raise ValueError(f"Invalid client type: {args.client_type}")

    # Process the SRT file
    process_srt(args.input_srt, args.output_srt, client, thread, source_lang=args.source_lang,
                target_lang=args.target_lang, dry_run=args.dry_run)