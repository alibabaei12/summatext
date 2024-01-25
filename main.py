from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate

if __name__ == '__main__':
    pdf_path = '/Users/alibabaei/Code/git/summatext/Designing Data-Intensive Applications.pdf'

    loader = PyPDFLoader(file_path=pdf_path)
    document = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
    docs = text_splitter.split_documents(documents=document)

    embeddings = OpenAIEmbeddings()

    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local("faiss_index_prompt")

    new_vectorstore = FAISS.load_local("faiss_index_prompt", embeddings)
    qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0, model_name="gpt-4"), chain_type="stuff",
                                     retriever=new_vectorstore.as_retriever())


   #  prompt = """
   #  devide the response in the following two:
   #  - ** the topics
   #      - Give me each topic of chapter one.
   #
   #  - ** the summery of the chapter
   #      -Summerize chapter 1 of the Designing Data-Intensive applications book
   #      -the result must be in form of bullet points and each bullet point should be less than 25 words
   # """

    prompt = """ 
        give me the table of content of the "designing data intensive application" book in bullte points
        
       """

    res = qa.run(prompt)
    print(res)
