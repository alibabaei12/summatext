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
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

import re

max_input_length = 4000
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
    toc = ""
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

    if end_table_of_contents_index == len(elements)-1:
        print("couldn't find the end of TOC")

    for element in elements[start_table_of_contents_index:end_table_of_contents_index]:
        page_content = element.page_content

        if "." in page_content:
            page_content = page_content.replace(".", "")
        page_content = re.sub(' +', ' ', page_content)
        toc += page_content + "\n"
        word_count += len(page_content)

    # Custom logic to find the table of contents
    return toc



if __name__ == "__main__":
    # Define your schema
    schema = {
        "properties": {
            "chapter_title": {"type": "string"},
            "chapter_topics": {"type": "string"},
            "chapter_sub_topics": {"type": "string"},
            "page_number": {"type": "integer"}
            # Add more fields as necessary
        },
        "required": ["chapter_title", "page_number"]
    }

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=max_output_length)
    # chain = create_extraction_chain(schema, llm)

    # Initialize ConversationBufferMemory
    memory = ConversationBufferMemory()

    # Initialize ConversationChain with the memory
    conversation = ConversationChain(llm=llm, memory=memory, verbose=True)

    try:
        input_text = find_table_of_contents()
        print("Extracted TOC Text: ", input_text)

        splitted_text = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", " ", ""]
        ).split_text(input_text)
          # Debug: Print the extracted text
        print("Splitted Text: ", splitted_text)

        for chunk in splitted_text:
            prompt = "take in this chunk and dont return any response yet. MOST IMPORTANT ROLE IS DO NOT RESPOND ANYTHING\n\n" + chunk
            response = conversation.predict(input=prompt)
            print("Response: ", response)

        final_prompt = "ok now Based on all the text processed, list all chapter titles and main points."
        final_response = conversation.predict(input=final_prompt)
        print("Final Response: ", final_response)
    except Exception as e:
        print("Error occurred:", str(e))