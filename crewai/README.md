# CrewAI Tutorial: Facebook Ad Agent Lead Generation

This tutorial demonstrates how to use the CrewAI framework to create an automated lead generation system for Facebook Ad Agents in San Francisco.

## Overview

The script performs the following tasks:
1. Generates search queries using a Search Query Specialist agent
2. Executes web searches using a Web Search Specialist agent
3. Extracts links from search results using a Link Extractor agent
4. Scrapes content from the extracted links
5. Extracts contact information using the Anthropic API

## Prerequisites

- Python 3.7+
- CrewAI library
- Anthropic API key
- SerperDev API key
- Firecrawl API key

## Setup

1. Clone this repository
2. Install required dependencies:
3. Create a `.env` file in the project root and add your API keys:
                    ANTHROPIC_API_KEY=your_anthropic_api_key SERPER_API_KEY=your_serper_api_key FIRECRAWL_API_KEY=your_firecrawl_api_key

## Usage

Run the script:

The script will output:
- Generated search queries
- Potential lead websites
- Extracted links (home, about, contact pages)
- Contact information (email, Twitter, LinkedIn) for each lead

## Customization

You can modify the following variables in the script to customize the search:
- `niche`: The business niche to search for
- `location`: The location to search in
- `num_leads`: The number of leads to generate

## Note

This script is for educational purposes and should be used responsibly and in compliance with all applicable laws and regulations.

## Reference

This code was created using the following video tutorial as a reference:
(https://www.youtube.com/watch?v=mO4-V7Lmt7c&t=3337s)


