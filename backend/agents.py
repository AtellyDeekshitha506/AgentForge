from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url
import os 
from dotenv import load_dotenv

load_dotenv()

llm = ChatMistralAI(model = "mistral-small-2506",temperature = 0)

#first agent 
def build_search_agent():
    return create_agent(
        model= llm,
        tools = [web_search]
    )

#2nd agent

def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url]
    )
#writer chain 

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Always return clean Markdown with H1/H2/H3 headings and concise bullet points."),
    ("human", """Write a detailed research report on the topic below.
     Topic : {topic}
     Research Gathered:
     {research}

     Return output in this exact Markdown structure:

     # Research Report: {topic}

     ## Executive Summary
     - 3 to 5 bullet points with the most important takeaways.

     ## Introduction
     - Brief context and why this topic matters.

     ## Key Findings
     ### Finding 1
     - What was found
     - Why it matters
     - Supporting evidence from the research

     ### Finding 2
     - What was found
     - Why it matters
     - Supporting evidence from the research

     ### Finding 3
     - What was found
     - Why it matters
     - Supporting evidence from the research

     ## Conclusion
     - 3 to 4 bullet points summarizing final insights.

     ## Sources
     - Bullet list of all relevant URLs from the research.

     Rules:
     - Use clear and simple language.
     - Prefer bullet points over long paragraphs.
     - Be factual, professional, and specific.
     - Do not output any text outside this structure."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()



#critic_chain

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Always respond in clean Markdown with H1/H2/H3 headings and bullet points."),
    ("human", """Review the research report below and evaluate it strictly.
    Report:{report}
    Respond in this exact Markdown format:

    # Report Review

    ## Overall Score
    - Score: X/10

    ## Strengths
    - Bullet points only.

    ## Areas for Improvement
    - Bullet points only.

    ## Actionable Suggestions
    ### High Priority
    - Bullet points only.

    ### Medium Priority
    - Bullet points only.

    Rules:
    - Be direct and specific.
    - Keep items practical and easy to apply.
    - Do not output any text outside this structure.
    """),
])
critic_chain = critic_prompt | llm | StrOutputParser()

