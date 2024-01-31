# from flask import Flask
#
# app = Flask(__name__)
#
# @app.route('/')
# def hello_world():
#     return 'Hello, World!'
#
# if __name__ == '__main__':
#     app.run(debug=True)
from typing import Sequence

from langchain.output_parsers import PydanticOutputParser
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
import os
import json
import re

max_input_length = 12000
max_output_length = 12000


def parse_pdf(pdf_path):
    """
    Parse the PDF and return the text of each page.
    """
    pdf_path = pdf_path

    loader = UnstructuredPDFLoader(pdf_path, mode="elements")
    data = loader.load()
    return data


def find_table_of_contents():
    """
    Implement your logic to find the table of contents from the parsed documents.
    This is a placeholder function. You need to write custom logic based on your PDF structure.
    """
    toc = []
    elements = parse_pdf('/Users/alibabaei/Code/git/summatext/Designing Data-Intensive Applications.pdf')
    i = 1
    start_table_of_contents_index = 0
    end_table_of_contents_index = len(elements) - 1
    entered_toc = False
    word_count = 0
    for i in range(len(elements) - 1):
        # Assuming each element corresponds to a page
        page_content = elements[i].page_content
        if "Content" in page_content and not entered_toc:
            start_table_of_contents_index = i
            entered_toc = True
            continue

        if page_content.startswith("Index") and entered_toc:
            end_table_of_contents_index = i
            break

        if i >= max_input_length:
            print("toc not finished")
            break

    for element in elements[start_table_of_contents_index:end_table_of_contents_index]:
        page_content = element.page_content

        # if "." in page_content:
        #     page_content = page_content.replace(".", "")
        # page_content = re.sub(' +', ' ', page_content)
        toc.append(page_content)
        word_count += len(page_content)

    # Custom logic to find the table of contents

    return toc

if __name__ == "__main__":

    llm = ChatMistralAI(mistral_api_key=os.environ["MISTRAL_API_KEY"], temperature=0, model="mistral-small",
                        max_tokens=max_output_length)

    try:
        toc = find_table_of_contents()
        # section= """1 Reliable, Scalable, and Maintainable Applications 3 Thinking About Data Systems 4 Reliability 6 Hardware Faults 7 Software Errors 8 Human Errors 9 How Important Is Reliability? 10 Scalability 10 Describing Load 11 Describing Performance 13 Approaches for Coping with Load 17 Maintainability 18 Operability: Making Life Easy for Operations 19 Simplicity: Managing Complexity 20 Evolvability: Making Change Easy 21 Summary 22"""
        # for section in tocs[2:]:
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant capable of analyzing an unstructured table of contents and "
                       "returning the response strictly in a clean JSON format without additional comments or "
                       "explanations."),
            ("human", f"Can you organize this unstructured Table of contents? {toc}"),

        ])

        _input = chat_prompt.format_messages(response="")

        result = llm.invoke(_input)

        clean_json_string = result.content.split('\n\n')[0].replace("content='", "").replace("'", "")
        json_output = json.loads(clean_json_string)
        print(json_output)

    except Exception as e:
        print("Error occurred:", str(e))
