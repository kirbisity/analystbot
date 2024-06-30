#!/usr/bin/python
import os
import shutil
import tempfile
import urllib
import urllib.request

# OpenAI
import openai


class ChatGPTCaller(object):
    """
    Makes a call to the ChatGPT API with the message and returns response.
    """
    def __init__(self, api_key:str=None):
        if api_key is None:
            if "OPENAI_API_KEY" not in os.environ:
                raise Exception("OPENAI_API_KEY must be declared in the environment. If you do not have one yet, please set up one in the ChatGPT API dashboard.")
            openai.api_key = os.environ["OPENAI_API_KEY"]
        else:
            openai.api_key = api_key

        self.model = "gpt-3.5-turbo"

        # Verify api key validity
        messages = [{"role": "user", "content": ""}]
        chat = openai.ChatCompletion.create(model=self.model, messages=messages)
        reply = chat.choices[0].message.content


    def send_message(self, message:list):
        """Send message to ChatGPT
        Args:
            message (list): The message to ChatGPT in the structure of
            [
                {"role": "system", "content": "You are a role."},
                {"role": "user", "content": "I have a question?"},
                {"role": "assistant", "content": "Provide more data."},
                {"role": "user", "content": "What is this?"}
            ]
        Returns:
            str: The response from ChatGPT.
        """
        try:
            chat = openai.ChatCompletion.create(model=self.model, messages=message)
            reply = chat.choices[0].message.content
        except Exception as e:
            return ""
        return reply

    def is_api_key_valid(self):
        try:
            messages = [{"role": "user", "content": ""}]
            chat = openai.ChatCompletion.create(model=self.model, messages=messages)
            reply = chat.choices[0].message.content
        except Exception as e:
            return False
        return True
