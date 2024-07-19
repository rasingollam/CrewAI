from dotenv import load_dotenv
import os
from crewai import Agent, Task, Crew
from anthropic import Anthropic
from openai import OpenAI

load_dotenv()

anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
sonnet = os.getenv('SONNET')
haiku = os.getenv('HAIKU')

client = Anthropic(api_key=anthropic_api_key)

niche = "Facebook Add Agent"
location = "San Francisco"
num_leads = 5

#-------------------------------------------------------------------------------------
# Import the ChatAnthropic class from the langchain_anthropic library
from langchain_anthropic import ChatAnthropic

# for tasks requiring deterministic, reproducible results
Consistent = ChatAnthropic(
    temperature=0.0, # no randomness
    model_name=sonnet
)

# for tasks benefiting from more varied and creative outputs
Creative = ChatAnthropic(
    temperature=0.8,
    model_name=haiku
)

#-------------------------------------------------------------------------------------
# Define a new AI Agent
#-------------------------------------------------------------------------------------
# This agent is responsible for generating unique & relevant search queries
variation_agent = Agent(
    # Specify the agent's role in the lead generation process
    role='Search Query Specialist',

    # Define the primary objective of this agent
    goal='Generate 10 different and effective search queries for lead generation',

    # Provide a detailed system prompt to guide the agent's behavior
    backstory="""You are an expert in crafting search queries that yield high-quality business leads.
    Your expertise lies in understanding user intent and translating it into 10 various search phrases
    that capture different aspects of the target business niche and location.""",

    # Enable verbose mode for detailed logging of the agent's actions
    verbose=True,

    # Prevent this agent from delegating tasks to other agents
    allow_delegation=False,

    # Use the Creative LLM we defined earlier
    llm=Creative
)


# Define the Search Query Agent Task
#-------------------------------------------------------------------------------------
# This task specifies the exact instructions for generating search queries
generate_variations = Task(
    # Detailed description of what the task should accomplish
    description=f"""Generate 10 different and concise search queries for {niche} in {location}.
    Make sure every search query is short and direct, it should be optimized for SerpAPI.
    Each query should be unique and different from the rest. Do not use quotation marks.
    DO NOT INCLUDE ANY EXTRA TEXT. JUST OUTPUT THE 10 SEARCH QUERY VARIATIONS. NOTHING BEFORE IT, NOTHING AFTER IT.""",

    # Specify the expected format of the task's output
    expected_output="A list of 10 unique search queries, each on a new line",

    # Assign this task to the previously defined variation_agent
    agent=variation_agent
)

#-------------------------------------------------------------------------------------
# Create a Crew for the Search Query Agent
search_query_crew = Crew(
    agents=[variation_agent],
    tasks=[generate_variations],
    verbose=2  # Set to 2 for detailed logging
)

#-------------------------------------------------------------------------------------
# Execute the Search Query Crew
search_queries_result = search_query_crew.kickoff()

# # Print the results
# print("\nGenerated Search Queries:")
# print(search_queries_result)

#-------------------------------------------------------------------------------------
# Process the search query results
search_queries = search_queries_result.split('\n')

# Remove any empty queries and strip whitespace
search_queries = [query.strip() for query in search_queries if query.strip()]

# Limit to exactly 10 queries
search_queries = search_queries[:10] # Search Queries.....................................................................

# Print the final list of search queries
print(f"\nFinal list of {len(search_queries)} search queries:")
for i, query in enumerate(search_queries, 1):
    print(f"{i}. {query}")
    

#-------------------------------------------------------------------------------------
# Search Agent  
#-------------------------------------------------------------------------------------

# Import the SerperDevTool
from crewai_tools import SerperDevTool

# Set up the SerpAPI key
os.environ["SERPER_API_KEY"] = os.getenv('SERPER_API_KEY')

# Create SerperDevTool instance
search_tool = SerperDevTool()

#-------------------------------------------------------------------------------------
# Define a new agent that will use the search tool
search_agent = Agent(
    role='Web Search Specialist',
    goal='Use the "search_tool" function you have assigned. Only use the tool.',
    backstory="""Your only task is to execute the "search_tool" you have access to.
    Do not perform any other actions, or generate any other text. Simply use the tool.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=Consistent  # Using the Consistent LLM we defined earlier
)


#-------------------------------------------------------------------------------------
# Create a Task for the search agent
search_task = Task(
    description=f"""Use the provided "search_tool" to find {num_leads} unique {niche} in {location}.
    Use these exact search queries: {search_queries}. DO NOT INVENT YOUR OWN SEARCH TERMS, ONLY USE THOSE 10 QUERIES.
    ONLY OUTPUT THE WEBSITES OF THOSE BUSINESSES. NO OTHER INFO, WEBSITES ONLY.
    Do not add any formatting. Simply output each website on a new line. That's it.""",
    expected_output=f"A clean list, with no formatting, of {num_leads} websites in the {niche} niche.",
    agent=search_agent
)


#-------------------------------------------------------------------------------------
# Create a Crew for the search process
search_crew = Crew(
    agents=[search_agent],
    tasks=[search_task],
    verbose=2  # Set to 2 for detailed logging
)

# Run the search crew and retrieve the results
search_results = search_crew.kickoff()

# print("\nSearch Results:")
# print(search_results)

# Process the search results
websites = search_results.strip().split('\n') # WebSites........................................................................................

print(f"\nFound {len(websites)} potential leads:")
for i, website in enumerate(websites, 1):
    print(f"{i}. {website}")


#-------------------------------------------------------------------------------------
# Link Extractor Agent
#-------------------------------------------------------------------------------------

from firecrawl import FirecrawlApp

# Set the Firecrawl API key
os.environ["FIRECRAWL_API_KEY"] = os.getenv('FIRECRAWL_API_KEY')

# Create the Firecrawl client
app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])

#-------------------------------------------------------------------------------------
# Create a variable targeting a single website
current_link = websites[3]

# Use Firecrawl to scrape the content of the home page
scrape_result = app.scrape_url(current_link)

# Print the first 500 characters to see how our scrape looks
# print(f"\nWebsite: {current_link}")
# print(scrape_result['markdown'][:500])


#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
# Define the Link Extractor Agent
link_extractor_agent = Agent(
    role='Link Extractor',
    goal='Extract about page and contact page links from homepage content',
    backstory="""You are an expert in web scraping and link extraction.
    Your task is to analyze homepage content and identify the URLs for the about page and contact page.""",
    verbose=True,
    allow_delegation=False,
    llm=Consistent
)

#-------------------------------------------------------------------------------------
# Describe the Link Extraction task
extract_links = Task(
    description=f"""Analyze the provided homepage content and extract the URLs for the about page and contact page.
    Use this exact content:

    ---
    {scrape_result['markdown']}
    ---

    DO NOT INVENT OR ASSUME ANY INFORMATION. ONLY OUTPUT THE ABOUT PAGE AND CONTACT PAGE URLS. NO OTHER INFO, JUST URLS.
    If a URL is not found, output None for that URL. Do not add any formatting.
    Simply output the about page URL, then a newline, then the contact page URL. That's it.""",
    expected_output="The about page URL and contact page URL, each on a new line. No formatting. If not found, output None for that URL.",
    agent=link_extractor_agent
)

#-------------------------------------------------------------------------------------
# Create a new Crew
link_crew = Crew(
    agents=[link_extractor_agent],
    tasks=[extract_links],
    verbose=1  # you might wanna use '1' here
)

#-------------------------------------------------------------------------------------
# Run the crew and retrieve the results
link_results = link_crew.kickoff()

# print("\nAGENT OUTPUT:")
# print(link_results)

#-------------------------------------------------------------------------------------
# Process the Agent output & add the original link into the list
links = link_results.strip().split('\n')
links.insert(0, current_link)
print(f"\nFound {len(links)} links:")
for i, link in enumerate(links, 1):
    print(f"{i}. {link}\n")

#-------------------------------------------------------------------------------------
# Let's add a function to scrape the about and contact pages
def scrape_pages(links):
    scraped_content = {}
    for page_type, link in zip(['home', 'about', 'contact'], links):
        if link != 'None':
            scraped_content[page_type] = app.scrape_url(link)['markdown']
        else:
            scraped_content[page_type] = ''
    return scraped_content

# Scrape the pages
scraped_content = scrape_pages(links)

# print("\nScrapped Content ", scraped_content['about'])

all_content = f"{scraped_content['home']} {scraped_content['about']} {scraped_content['contact']} "


#-------------------------------------------------------------------------------------
# Anthropic API Call for final Result
#-------------------------------------------------------------------------------------

# Here we define a new string called 'prompt' with clear instructions for the LLM
prompt = f"""FROM THE FOLLOWING WEB SCRAPE, OUTPUT 3 THINGS: THE EMAIL, THE TWITTER LINK, THE LINKEDIN LINK.
DO NOT INCLUDE ANY EXTRA TEXT BEFORE / AFTER.

---
{all_content}
---

Output the results in the following format:
Email: [email address]
Twitter: [Twitter handle]
LinkedIn: [LinkedIn profile URL]

If any information is not found, output None for that field.
NO EXTRA TEXT!! just the email, twitter and linkedin.
"""

#-------------------------------------------------------------------------------------
# Extract the contact info with a single Anthropic API call
message = client.messages.create(
    model=sonnet,
    max_tokens=200,
    temperature=0.1,  # low temperature = predictable outputs
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print(message.content[0].text)















print("done")