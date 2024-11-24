from structures import ResearchPaper


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

def formulate_topic_importance(original_topic: str, topic: str, paper: ResearchPaper) -> str:
    """
    Generates a prompt to analyze how a research paper relates to and can be applied to the original topic.
    
    Args:
        original_topic (str): Main research topic
        topic (str): Related sub-topic
        paper (ResearchPaper): Paper to analyze
        
    Returns:
        str: Formatted analysis prompt
    """
    
    prompt = f"""<instruction>
TASK: Analyze how this research paper's findings and methodologies can be applied to or expand upon the original research topic.

ORIGINAL RESEARCH TOPIC: {original_topic}
RELATED SUB-TOPIC: {topic}

PAPER DETAILS:
Title: {paper.title}
Authors: {', '.join(paper.authors)}
URL: {paper.url}
Abstract: {paper.abstract}

REQUIREMENTS:
1. Provide specific examples and details from the paper
2. Include direct connections to the original topic
3. Specify technical requirements for implementation
4. Note any gaps between paper focus and original topic
5. Do not make assumptions about unstated results
6. State explicitly if information is insufficient
7. Include all relevant details from paper content
8. Do not use phrases like "Based on the absence of selected results" or similar.
9. If the information is paraphrased from the paper cite the first author using " [Author : Title]"

OUTPUT FORMAT:
1. Brief Overview (5-6 sentences)
2. Direct Applications to {original_topic}
3. Potential Extensions/Adaptations
4. Implementation Considerations and how to apply the paper to the original topic
5. Information Gaps (if any)
6. Conclusion

Do not use phrases like "Based on the absence of selected results" or similar.
If content lacks sufficient information, explicitly state what is missing and why it matters.
Provide as much relevant detail as possible from the available content.
</instruction>"""

    return prompt

def formulate_topic_summary(research_analysis: str):
    pass