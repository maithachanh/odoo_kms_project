import time
try:
    print("Importing langchain_ollama...")
    from langchain_ollama import ChatOllama
    print("Initializing ChatOllama with phi3 model...")
    llm = ChatOllama(model="phi3", temperature=0.3)
    
    print("Invoking model directly: 'Hi, who are you?'...")
    t0 = time.time()
    response = llm.invoke("Hi, who are you?")
    t1 = time.time()
    print("Success!")
    print("Time taken:", round(t1 - t0, 2), "seconds")
    print("Response content:")
    print(response.content)
except Exception as e:
    print("Error calling Ollama direct:", e)
