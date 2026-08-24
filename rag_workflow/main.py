from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core import get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.llms.cohere import Cohere
from llama_index.core.postprocessor import SimilarityPostprocessor
from pydantic import BaseModel, Field
from typing import List, Literal
from llama_index.core import Settings
from llama_index.core.program import LLMTextCompletionProgram
import json 
from llama_index.llms.cohere import Cohere
from llama_index.core import Settings
import os
from dotenv import load_dotenv
load_dotenv()
import os
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext
from dotenv import load_dotenv
load_dotenv()

input_dirs = {
    "roo-coder": "./TaskClient/docs/roo-docs", 
    "cline": "./TaskClient/docs/cline-logs"
}
documents = []

for agent_name, path in input_dirs.items():
    
    def add_agent_metadata(file_path):
        return {
            "agent_tool": agent_name,
            "source_folder": path
        }

    reader = SimpleDirectoryReader(
        input_dir=path, 
        recursive=True, 
        required_exts=[".md"],
        file_metadata=add_agent_metadata 
    )
    documents.extend(reader.load_data())

print(f"נטענו {len(documents)} מסמכים עם תיוג Agent.")






parser = MarkdownNodeParser()


nodes = parser.get_nodes_from_documents(documents)


print(nodes[0].metadata)




api_key = os.getenv("COHERE_API_KEY")

embed_model = CohereEmbedding(
    cohere_api_key=api_key,
    model_name="embed-multilingual-v3.0",
)

Settings.embed_model = embed_model
Settings.chunk_size = 512 

parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)

index = VectorStoreIndex(nodes)

print(f"הסתיים אינדוקס של {len(nodes)} צמתים.")

MY_API_KEY = os.getenv("PINECONE_API_KEY")


pc = Pinecone(
    api_key=MY_API_KEY, 
    ssl_verify=False
)


index = os.getenv("INDEX_HOST")
pinecone_index = pc.Index(name="rag-index", host=index)


vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index,
    api_key=MY_API_KEY  
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)


index = VectorStoreIndex(
    nodes, 
    storage_context=storage_context,
    show_progress=True
)
print("האינדקס נשמר בהצלחה ב-Pinecone!")


llm = Cohere(
    api_key=os.getenv("COHERE_API_KEY"), 
    model="command-r-08-2024" # או פשוט "command-r-v2" בהתאם לעדכוני Cohere האחרונים
)


Settings.llm = llm


query_engine = index.as_query_engine(
    similarity_top_k=5,
    llm=llm
)


retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=5, 
)


response_synthesizer = get_response_synthesizer(
    llm=llm,
    response_mode="compact" 
)



node_postprocessors = [
    SimilarityPostprocessor(similarity_cutoff=0.45) 
]

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    node_postprocessors=node_postprocessors
)


class DecisionItem(BaseModel):
    title: str = Field(description="כותרת ההחלטה")
    summary: str = Field(description="תמצית ההחלטה")
    status: Literal["active", "deprecated", "pending"]

class RuleItem(BaseModel):
    rule: str = Field(description="הכלל או ההנחיה")
    scope: str = Field(description="תחום (UI, Backend, etc.)")

class StructuredData(BaseModel):
    decisions: List[DecisionItem]
    rules: List[RuleItem]


def extract_structured_data(documents):
   
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=StructuredData,
        prompt_template_str="""עבור הטקסט הבא ממסמכי הפרויקט, חלץ את כל ההחלטות והכללים המופיעים בו:
        ---
        {input_str}
        ---
        """,
        llm=llm # ה-LLM שהגדרת קודם
    )
    
    all_extracted_data = {"decisions": [], "rules": []}
    
    for doc in documents:
        result = program(input_str=doc.get_content())
        all_extracted_data["decisions"].extend(result.decisions)
        all_extracted_data["rules"].extend(result.rules)
        
    return all_extracted_data

# נניח ששמרנו את זה למשתנה גלובלי או לקובץ
project_metadata = extract_structured_data(documents)
# שמירה - המרת Pydantic objects לדיקשנריים
with open('structured_data.json', 'w', encoding='utf-8') as f:
    # המרת כל DecisionItem ו-RuleItem לדיקשנריים
    serializable_data = {
        "decisions": [d.model_dump() if hasattr(d, 'model_dump') else d.dict() for d in project_metadata["decisions"]],
        "rules": [r.model_dump() if hasattr(r, 'model_dump') else r.dict() for r in project_metadata["rules"]]
    }
    json.dump(serializable_data, f, ensure_ascii=False, indent=2)


import json
import gradio as gr
from typing import List, Union
from llama_index.core.workflow import Workflow, step, StartEvent, StopEvent, Event
from llama_index.core import get_response_synthesizer

from llama_index.utils.workflow import draw_all_possible_flows
# --- 1. הגדרת האירועים (Events) ---
class StructuredRetrievalEvent(Event):
    query: str
    data: dict

class RetrievalEvent(Event):
    query: str

class ValidationEvent(Event):
    nodes: list
    query: str

class GenerationEvent(Event):
    nodes: list
    query: str


class AgenticRAGWorkflow(Workflow):
    def __init__(self, retriever, synthesizer, structured_data, **kwargs):
        super().__init__(**kwargs)
        self.retriever = retriever
        self.synthesizer = synthesizer
        self.structured_data = structured_data

    @step
    async def ingest_and_route(self, ev: StartEvent) -> RetrievalEvent | StructuredRetrievalEvent | StopEvent:
        query = ev.get("query")
        
        
        if not query or len(query.strip()) < 3:
            return StopEvent(result="השאילתה קצרה מדי. אנא שאל שאלה מפורטת יותר.")
        
       
        router_prompt = f"""
        אתה מנתח כוונות עבור מערכת RAG. עליך להחליט לאן לנתב את השאלה:
        1. 'structured' - שאלות שמבקשות רשימות, כללים, הנחיות, החלטות, או שאלות מבוססות זמן.
        2. 'semantic' - שאלות ידע כלליות, הסברים, או חיפוש תוכן חופשי.
        
        השאלה: "{query}"
        ענה במילה אחת בלבד: structured או semantic.
        """
        
       
        decision_raw = llm.complete(router_prompt).text.strip().lower()
        decision = "structured" if "structured" in decision_raw else "semantic"
        
        print(f"--- Routing Decision: {decision} ---")

        if decision == "structured":
            return StructuredRetrievalEvent(query=query, data=self.structured_data)
        
        return RetrievalEvent(query=query)

    @step
    async def handle_structured(self, ev: StructuredRetrievalEvent) -> StopEvent:
    
        prompt = f"""
        הנך עוזר טכני המסתמך על מאגר נתונים מובנה (JSON). 
        הנתונים: {ev.data}
        
        השאלה של המשתמש: "{ev.query}"
        
        הנחיות:
        1. ספק רשימות מלאות אם התבקשת.
        2. סנן לפי תאריכים אם השאלה כוללת תנאי זמן.
        3. אם המידע לא מופיע בנתונים המובנים, ציין זאת.
        """
        response = llm.complete(prompt) 
        return StopEvent(result=str(response))

    @step
    async def perform_retrieval(self, ev: RetrievalEvent) -> ValidationEvent:
      
        nodes = self.retriever.retrieve(ev.query)
        return ValidationEvent(nodes=nodes, query=ev.query)

    @step
    async def validate_results(self, ev: ValidationEvent) -> GenerationEvent | StopEvent:
       
        if not ev.nodes or all(getattr(n, 'score', 0) < 0.45 for n in ev.nodes):
            return StopEvent(result="לא מצאתי מידע אמין מספיק במסמכי התיעוד כדי לענות על כך.")
        
        return GenerationEvent(nodes=ev.nodes, query=ev.query)

    @step
    async def generate_response(self, ev: GenerationEvent) -> StopEvent:
        
        response = self.synthesizer.synthesize(query=ev.query, nodes=ev.nodes)
        return StopEvent(result=str(response))


try:
    with open('structured_data.json', 'r', encoding='utf-8') as f:
        project_metadata = json.load(f)
except FileNotFoundError:
    print("Warning: structured_data.json לא נמצא. מוודא שהרצת את ה-Extraction.")
    project_metadata = {"decisions": [], "rules": [], "warnings": []}

retriever = index.as_retriever(similarity_top_k=5)
response_synthesizer = get_response_synthesizer(llm=llm)

rag_wf = AgenticRAGWorkflow(
    retriever=retriever, 
    synthesizer=response_synthesizer, 
    structured_data=project_metadata,
    timeout=60, 
    verbose=True
)


async def workflow_chat(message, history):
   
    result = await rag_wf.run(query=message)
    return str(result)

demo = gr.ChatInterface(
    fn=workflow_chat,
    title="🚀 Agentic Event-Driven RAG",
    description="מערכת RAG משולבת: חיפוש סמנטי + שליפת נתונים מובנים (JSON)"
)



draw_all_possible_flows(rag_wf, filename="workflow_schema.html")


if __name__ == "__main__":
    demo.launch(share=True)







