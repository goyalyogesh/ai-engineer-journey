import warnings
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic

# 1. Mute the underlying Google GenAI SDK architecture warnings
warnings.filterwarnings(
    "ignore", 
    message=".*Direct use of automatic function calling.*"
)
warnings.filterwarnings(
    "ignore", 
    message=".*uses fixed sampling defaults.*"
)



load_dotenv()

llm_openai = ChatOpenAI(model="gpt-4o-mini", temperature=1) #initializing the openai model

llm_google = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=1) #initializing the google model

llm_anthropic = ChatAnthropic(model="claude-haiku-4-5", temperature=1)

m1 = "Who is the Prime Minister of India?" #first question
m2 = " Tell me about the Volcano in Indonesia" #second question
m3 = "What is special about Canada?" #third question

messages_1 = [
    SystemMessage(content ="You are a funny assistant that can answer questions and make jokes."),
    HumanMessage(content = m1)]

messages_2 = [
    SystemMessage(content ="You are a funny assistant that can answer questions and make jokes."),
    HumanMessage(content = m2)]

messages_3 = [
    SystemMessage(content ="You are a funny assistant that can answer questions and make jokes."),
    HumanMessage(content = m3)]




response_1= llm_openai.invoke(messages_1)
#display the type
print(type(response_1))
#display the content
print(response_1.content)

print("---------------------------------------------------")

response_2 = llm_google.invoke(messages_2)
#display the type
print(type(response_2))
#display the content
print(response_2.content)

print("---------------------------------------------------")

response_3 = llm_anthropic.invoke(messages_3)
#display the type
print(type(response_3))
#display the content
print(response_3.content)