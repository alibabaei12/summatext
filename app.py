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
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.chains import create_extraction_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator

import re

max_input_length = 1000
max_output_length = 1000

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
    end_table_of_contents_index = len(elements)-1
    entered_toc = False
    word_count = 0
    for i in range(len(elements)-1):
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

        if "." in page_content:
            page_content = page_content.replace(".", "")
        page_content = re.sub(' +', ' ', page_content)
        toc.append(page_content)
        word_count += len(page_content)

    # Custom logic to find the table of contents

    return toc



class Chapter(BaseModel):
    chapter_title: str
    chapter_sub_title: list

class TOC(BaseModel):
    """ Identify the chapter title and the subtitles under that chapter"""

    toc: Sequence[Chapter]

if __name__ == "__main__":

    # Set up a parser + inject instructions into the prompt template.
    parser = PydanticOutputParser(pydantic_object=TOC)


    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=max_input_length)
    # chain = create_extraction_chain(schema, llm)

    try:
        tocs = find_table_of_contents()

        for section in tocs[2:]:
            print("Extracted TOC Text: ",section)
            prompt = PromptTemplate(
                template="Answer the user query.\n{format_instructions}\n{query}\nThe answer must be only {max_tokens} tokens\nIf the input doesnt makes sense, just ignore it",
                input_variables=["query"],
                partial_variables={"format_instructions": parser.get_format_instructions(), "max_tokens": max_output_length},
            )
            _input = prompt.format_prompt(query=section)
            result = llm(_input.to_string())
            parser.parse(result)
            # results = chain.run(section)

            print(result)
    except Exception as e:
        print("Error occurred:", str(e))