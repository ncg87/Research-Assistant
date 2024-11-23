def formulate_search_query(topic: str, previous_topics: str):
    """Formulates an effective search query for arXiv"""
    prompt = f"""<instruction>
Convert the following research topic into a short arXiv search query that will return the most relevant papers.
Topic: {topic}

Requirements:
- Return ONLY the search query
- Use 2-5 words maximum
- Include only essential technical terms
- Do not include any explanations or additional text
- Do not use quotes or special characters
- If the topic is broad, return a general query.
- Make sure they are different than the previous topics: {previous_topics}
</instruction>

Output format:
[search terms only]"""
    return prompt

def formulate_research_topics(research: str):
    """Formulates effective research topic for an arXiv query"""
    
    prompt = f"""<instruction>
Convert the following research topic into a 5 different research topics that can be used to expand on the original topic. These research topics will be used to search for papers on arXiv.
Topic: {research}

Requirements:
- Each research topic should be unique and cover different aspects and directions of the topic
- Do not include any explanations or additional text
- Do not use quotes or special characters
- If the topic is broad, return a mutiple specific queries.
</instruction>

Output format:
1. [First research topic]
Priority: [number 1-5]

2. [Second research topic]
Priority: [number 1-5]

3. [Third research topic]
Priority: [number 1-5]

4. [Fourth research topic]
Priority: [number 1-5]

5. [Fifth research topic]
Priority: [number 1-5] """
    return prompt

def formulate_title_assesment(paper_entries: str, topic: str, max_titles: int = 5):
    """Assesses the relevance of a mutliple papers to a research topic"""
    prompt = f"""<instruction>
TASK: Select the {max_titles} paper titles most relevant to the research topic.

RESEARCH TOPIC: {topic}

PAPERS:
{paper_entries}

REQUIREMENTS:
- Return ONLY a JSON array of the top {max_titles} paper IDs in order of relevance
- Format: [id1, id2, id3, id4, id5]
- Base selection STRICTLY on relevance to the research topic
- Consider technical term overlap and semantic similarity
- Do not explain your choices
- Do not include any additional text

Example output format:
[0, 14, 23, 45, 31]
</instruction>"""

    return prompt

def formulate_abstract_assesment(paper_abstracts: str, topic: str, max_papers: int = 3):
    """Assesses the relevance of a mutliple papers to a research topic by abstract"""
    prompt = f"""<instruction>
TASK: Select the {max_papers} papers most relevant to the research topic based on their abstracts.

RESEARCH TOPIC: {topic}

PAPERS:
{paper_abstracts}

REQUIREMENTS:
- Return ONLY a JSON array containing the IDs of the 3 most relevant papers
- Format: [id1, id2, id3]
- Base selection on abstract content and methodology relevance
- Order by relevance (most relevant first)
- Do not include any explanations or additional text

Example output format:
[4, 1, 3]
</instruction>"""
    
    return prompt