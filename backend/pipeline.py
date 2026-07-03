from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
from openai import AuthenticationError, RateLimitError


def _quota_help_message(stage: str, err: Exception) -> str:
    return (
        f"OpenAI request failed during '{stage}' due to account limits. "
        "Your code is fine, but the API returned insufficient_quota (429). "
        "Add billing/credits in OpenAI, switch to a different API key, or use a different LLM provider/model. "
        f"Original error: {err}"
    )

def run_research_pipeline(topic:str) -> dict:

    state = {}

    print("\n\n\n"+"="*50)
    print("step 1 - search agent is working...")
    print("\n\n\n"+"="*50)

    search_agent = build_search_agent()
    try:
        search_result = search_agent.invoke({"messages": [("user", f"Find reliable and detailed information about: {topic}\n\n\n")]})
    except (RateLimitError, AuthenticationError) as err:
        state["error"] = _quota_help_message("search step", err)
        print("\nERROR:\n", state["error"])
        return state

    state["search_results"] = search_result['messages'][-1].content
    print("\nsearch result",state)

    #step2 - reader agent 
    print("\n"+"="*50)
    print("step 2 - reader agent is working...")
    print("="*50)

    reader_agent = build_reader_agent()
    try:
        reader_result = reader_agent.invoke({
            "messages": [("user",
                    f"Based on the following search results about '{topic}',"
                    f"pick the most relevant Url and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}"
         )]
        })
    except (RateLimitError, AuthenticationError) as err:
        state["error"] = _quota_help_message("reader step", err)
        print("\nERROR:\n", state["error"])
        return state
    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nscraped content:\n",state['scraped_content'])

    #step3-write chain 

    print("\n"+"="*50)
    print("step 3 - Reader agent is scraping top resources")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results'][:800]}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content'][:800]}"

    )
    try:
        state["report"] = writer_chain.invoke({
            "topic":topic,
            "research":research_combined
        })
    except (RateLimitError, AuthenticationError) as err:
        state["error"] = _quota_help_message("writer step", err)
        print("\nERROR:\n", state["error"])
        return state

    print("\n final report\n",state['report'])


    #critic report 
    print("\n"+"="*50)
    print("step 4 - Critic agent is reviewing the report")
    print("="*50)

    try:
        state['feedback'] = critic_chain.invoke({
            "report":state['report'],
        })
    except (RateLimitError, AuthenticationError) as err:
        state["error"] = _quota_help_message("critic step", err)
        print("\nERROR:\n", state["error"])
        return state

    print("\n critic report \n",state['feedback'])

    return state 


if __name__ == "__main__":
    topic = input("\n Enter topic: ") 
    run_research_pipeline(topic)
