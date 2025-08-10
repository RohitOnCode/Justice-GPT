from langchain.memory import ConversationBufferMemory

def build_shared_memory():
    # Single shared memory instance used by both agents
    return ConversationBufferMemory(return_messages=True)
