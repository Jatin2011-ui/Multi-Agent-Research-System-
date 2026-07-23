from langchain.agents import create_react_agent, AgentExecutor  # CHANGED
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate  # CHANGED
from tools import web_search, scrape_url
from dotenv import load_dotenv

load_dotenv()

# model setup
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

# ReAct agent needs a single PromptTemplate with these exact variables
agent_prompt = PromptTemplate.from_template("""You are a helpful research assistant.
Answer the following questions as best you can using the available tools.

You have access to the following tools:
{tools}

Use the following format strictly:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}""")

# 1st agent
def build_search_agent():
    agent = create_react_agent(          # CHANGED
        llm=llm,
        tools=[web_search],
        prompt=agent_prompt,
    )
    return AgentExecutor(agent=agent, tools=[web_search], verbose=True, handle_parsing_errors=True)

# 2nd agent
def build_reader_agent():
    agent = create_react_agent(          # CHANGED
        llm=llm,
        tools=[scrape_url],
        prompt=agent_prompt,
    )
    return AgentExecutor(agent=agent, tools=[scrape_url], verbose=True, handle_parsing_errors=True)

# writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports"),
    ("human", """Write a detailed research report on the topic below.
    Topic: {topic}
    
    Research Gathered:
     {research}

    Structure the report as:
     -Introduction
     -Key Findings( minimum 3 well-explained points)
     -Conclusion
     -Sources (list all URLs found in the research)

    Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific"),
    ("human", """Review the research report below and evaluate it strictly.
     Report: {report}

     Respond in this exact format:
     Score: X/10

     Strengths: 
     - ...
     - ...

     Areas to Improve:
        - ...
        - ...
     One line verdict:
     ..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()