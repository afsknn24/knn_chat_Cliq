import os
from langchain_anthropic.chat_models import ChatAnthropic
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

"""
Establecemos una clase para el chat, la cual contiene el modelo de LM, la base de datos vectorial, el prompt como 
atributos, así como los métodos para obtener la pregunta al usuario, obtener los documentos de la base de datos 
vectorial relacionados a su pregunta y realizar la respuesta al usuario con el modelo de LM. 
"""
class Chatbot:
    def __init__(self, model:str, key:str):
        # Se define el modelo a utilizar y se configura acorde a pruebas para mejorar su eficiencia.
        self.llm = ChatAnthropic(
            model_name=model,
            api_key=key,
            temperature=0.2,
            timeout=None,
            streaming=True
        )
        load_dotenv()
        #Establecemos el modelo de embeddings a usar
        self.__embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        self.__pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.__index = self.__pc.Index(name="cliq-vector-db")
        #Cargamos la base de datos vectorial apoyandonos del modelo de embeddings
        self.vector_db = PineconeVectorStore(index=self.__index, embedding=self.__embedder)
        #Establecemos el número de documentos a extraer para acotarlos al contexto
        self.__k = 10
        #Configuramos el prompt para el chatbot
        self.prompt = ChatPromptTemplate([
            ("system",
             """Eres un asistente útil que interactua con el usuario como chatbot.
             El usuario podrá realizarte preguntas acerca de los articulos, manuales o politicas de la empresa.
             Responde solo con la información adjunta en el contexto UNICAMENTE cuando se te hagan preguntas de politicas, manuales y articulos.
             Son fragmentos de los documentos, por lo que deberás utilizar sus metadatos para poder juntar todos los fragmentos de un mismo documento.
             No inventes información ni datos que no estén en los documentos y si la información de los documentos no es suficiente, solo indica que no cuentas con esa información por el momento.
             -----------
             Contexto: {context}"""
             ),
            ("user","{input}")
        ])


#   Establecemos el metodo para que se obtengan los documentos a utilizar como contexto en base a una busqueda de similitud.
    def retrieved_documents(self, question:str):
        return self.vector_db.similarity_search(question,k=self.__k)


#   Establecemos el metodo para realizar las preguntas al chat, haciendo un llamado al modelo de LM y retornando la respuesta.
    def get_response(self, query:str, context_docs):
        """
        Hacemos un llamado al modelo con su metodo '.invoke', pasandole como argumento el prompt formateado (.format())
         con los documentos de contexto (context=context_docs) y la pregunta (input=query).
        :param query: La pregunta a realizar al chatbot.
        :param context_docs: Los documentos de contexto en los que se basa la respuesta.
        :return:
        """
        chat = self.llm.invoke(self.prompt.format(context=context_docs,input=query))
        return chat.content

