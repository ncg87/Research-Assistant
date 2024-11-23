def formulate_search_query(topic: str):
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
</instruction>

Output format:
[search terms only]"""
    return prompt

def assess_relevence_prompt(abstract: str):
    """Assesses the relevance of a paper"""
    prompt = f"""
    """
    return prompt