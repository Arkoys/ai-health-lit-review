"""
Paper summarization with multiple provider fallback.
Uses OpenRouter (primary), Gemini (fallback), HuggingFace (tertiary).
"""
import os
import json
import logging
import time
import re
import requests
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

def estimate_token_count(text: str) -> int:
    """Rough token estimation: ~4 chars per token for English, /3 for dense text."""
    return max(1, len(text) // 3)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/summarizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def summarize(self, paper: Dict[str, Any], max_words: int = 300) -> Optional[Dict[str, str]]:
        """Generate summary, critique, methods extraction, and gap identification."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the provider is reachable and authenticated."""
        pass

class GeminiProvider(BaseLLMProvider):
    """Google Gemini AI Studio provider (free tier: 2M tokens/month)."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        self.session = requests.Session()
    
    def summarize(self, paper: Dict[str, Any], max_words: int = 300) -> Optional[Dict[str, str]]:
        """Generate structured summary of a paper."""
        prompt = self._build_prompt(paper, max_words)
        
        try:
            response = self.session.post(
                f"{self.base_url}?key={self.api_key}",
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": max_words * 2,  # approx tokens
                        "temperature": 0.3
                    }
                },
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API error {response.status_code}: {response.text[:200]}")
                return None
            
            result = response.json()
            if 'candidates' not in result or not result['candidates']:
                logger.error("Gemini returned no candidates")
                return None
            
            text = result['candidates'][0]['content']['parts'][0]['text']
            return self._parse_response(text)
            
        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            return None
    
    def _build_prompt(self, paper: Dict[str, Any], max_words: int) -> str:
        """Build structured prompt for summarization."""
        return f"""You are an expert AI researcher reviewing a paper on AI for healthcare.

Title: {paper['title']}

Authors: {', '.join(paper.get('authors', []))}

Abstract: {paper.get('abstract', 'N/A')}

Venue: {paper.get('venue', 'Unknown')}

Please provide a structured review with the following sections (be concise):

1. SUMMARY (approx {max_words} words)
   - What is the main contribution?
   - What problem does it solve?
   - How does it compare to prior work?

2. METHODS & TECHNIQUES
   - Model architecture/dataset used
   - Training/evaluation methodology
   - Key technical innovations

3. KEY RESULTS
   - Main claims and supporting evidence
   - Metrics used and performance achieved
   - How does it compare to state-of-the-art?

4. CRITICAL EVALUATION
   - Main limitations and assumptions
   - Potential biases or methodological concerns
   - Strength of evidence (small/large study, retrospective/prospective, etc.)

5. RESEARCH GAPS & FUTURE DIRECTIONS
   - What questions remain unanswered?
   - Suggested improvements or next steps
   - Potential impact on clinical practice

6. KEYWORDS
   - Extract 5-10 relevant keywords from this paper

7. CONNECTIONS
   - If this builds on or contradicts known papers, mention them
   - Otherwise, leave as "No specific connections identified"

Format your response with clear section headers (1., 2., 3., etc.) and ensure each section is substantive but concise."""
    
    def _parse_response(self, text: str) -> Dict[str, str]:
        """Parse the LLM response into structured components."""
        sections = {
            'summary': '',
            'methods': '',
            'results': '',
            'critique': '',
            'gaps': '',
            'keywords': '',
            'connections': ''
        }
        
        # Simple parsing based on section numbers/headers
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'summary' in line_lower and 'approx' in line_lower:
                current_section = 'summary'
                continue
            elif 'methods' in line_lower and 'techniques' in line_lower:
                current_section = 'methods'
                continue
            elif 'key results' in line_lower:
                current_section = 'results'
                continue
            elif 'critical evaluation' in line_lower:
                current_section = 'critique'
                continue
            elif ('research gaps' in line_lower) or ('future directions' in line_lower):
                current_section = 'gaps'
                continue
            elif 'keywords' in line_lower:
                current_section = 'keywords'
                continue
            elif 'connections' in line_lower:
                current_section = 'connections'
                continue
            
            if current_section and line.strip():
                sections[current_section] += line + '\n'
        
        # Clean up whitespace
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def test_connection(self) -> bool:
        """Test Gemini API connectivity."""
        try:
            test_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
            response = self.session.get(test_url, timeout=10)
            return response.status_code == 200
        except:
            return False

class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace Inference API provider (free tier: ~30K tokens/month)."""
    
    def __init__(self, api_key: str, model: str = "meta-llama/Llama-3.3-70B-Instruct"):
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/v1/chat/completions"
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def summarize(self, paper: Dict[str, Any], max_words: int = 300) -> Optional[Dict[str, str]]:
        """Generate structured summary using Llama 3.3."""
        prompt = self._build_prompt(paper, max_words)
        
        try:
            response = self.session.post(
                self.base_url,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an expert AI research scientist reviewing healthcare AI papers."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_words * 2,
                    "temperature": 0.3
                },
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"HuggingFace API error {response.status_code}: {response.text[:200]}")
                return None
            
            result = response.json()
            if 'choices' not in result or not result['choices']:
                logger.error("HuggingFace returned no choices")
                return None
            
            text = result['choices'][0]['message']['content']
            return self._parse_response(text)
            
        except Exception as e:
            logger.error(f"HuggingFace request failed: {e}")
            return None
    
    def _build_prompt(self, paper: Dict[str, Any], max_words: int) -> str:
        """Build prompt (similar to Gemini but adapted for Llama)."""
        return f"""You are an AI research expert. Provide a structured review of this healthcare AI paper.

TITLE: {paper['title']}

AUTHORS: {', '.join(paper.get('authors', []))}

ABSTRACT: {paper.get('abstract', 'N/A')}

VENUE: {paper.get('venue', 'Unknown')}

Structure your response with these exact section headers (keep each section concise):

===SUMMARY===
(~{max_words} words: main contribution, problem solved, comparison to prior work)

===METHODS===
(Model architecture, dataset, training/evaluation methodology, key innovations)

===RESULTS===
(Key claims, supporting evidence, metrics, SOTA comparison)

===CRITIQUE===
(Limitations, assumptions, biases, evidence strength)

===GAPS===
(Unanswered questions, improvements, clinical impact)

===KEYWORDS===
(5-10 relevant keywords, comma-separated)

===CONNECTIONS===
(Related work: builds on/contradicts specific papers, or "None")

Ensure each section has meaningful content. Do not omit any section."""
    
    def _parse_response(self, text: str) -> Dict[str, str]:
        """Parse response based on ===SECTION=== markers."""
        sections = {
            'summary': '',
            'methods': '',
            'results': '',
            'critique': '',
            'gaps': '',
            'keywords': '',
            'connections': ''
        }
        
        lines = text.split('\n')
        current_section = None
        capture = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check for section headers
            if '===SUMMARY===' in line_stripped:
                current_section = 'summary'
                capture = True
                continue
            elif '===METHODS===' in line_stripped:
                current_section = 'methods'
                capture = True
                continue
            elif '===RESULTS===' in line_stripped:
                current_section = 'results'
                capture = True
                continue
            elif '===CRITIQUE===' in line_stripped:
                current_section = 'critique'
                capture = True
                continue
            elif '===GAPS===' in line_stripped:
                current_section = 'gaps'
                capture = True
                continue
            elif '===KEYWORDS===' in line_stripped:
                current_section = 'keywords'
                capture = True
                continue
            elif '===CONNECTIONS===' in line_stripped:
                current_section = 'connections'
                capture = True
                continue
            elif line_stripped.startswith('===') and line_stripped.endswith('==='):
                # Unknown section header, stop capturing
                current_section = None
                capture = False
                continue
            
            if capture and current_section and line_stripped:
                sections[current_section] += line + '\n'
        
        # Clean up
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def test_connection(self) -> bool:
        """Test HuggingFace API connectivity."""
        try:
            response = self.session.post(
                self.base_url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider (primary: gpt-4o)."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def summarize(self, paper: Dict[str, Any], max_words: int = 300) -> Optional[Dict[str, str]]:
        """Summarize using OpenAI with retry logic."""
        prompt = self._build_prompt(paper, max_words)
        
        max_retries = 2
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    self.base_url,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are an AI research expert. Provide structured outputs with exact section headers."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_words * 2,
                        "temperature": 0.3
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        text = result['choices'][0]['message']['content']
                        return self._parse_loose_response(text)
                    else:
                        logger.warning(f"OpenAI returned no choices")
                        return None
                
                elif response.status_code == 429:
                    retry_after = response.headers.get('Retry-After', base_delay * (2 ** attempt))
                    delay = int(retry_after)
                    logger.warning(f"OpenAI rate limited. Retrying in {delay}s")
                    time.sleep(delay)
                    continue
                
                else:
                    logger.error(f"OpenAI error {response.status_code}: {response.text[:200]}")
                    return None
                    
            except Exception as e:
                logger.error(f"OpenAI request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                else:
                    return None
        
        return None
    
    def _build_prompt(self, paper: Dict[str, Any], max_words: int) -> str:
        return f"""Review this AI in healthcare paper:

Title: {paper['title']}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}
Venue: {paper.get('venue', 'Unknown')}

Provide a structured review with these exact section headers (one per line, plain text):
SUMMARY
[summary text]

METHODS
[methods text]

RESULTS
[results text]

CRITIQUE
[critique text]

GAPS
[gaps text]

KEYWORDS
[keywords, comma-separated]

CONNECTIONS
[connections to other work]

Each section should be concise but substantive."""
    
    def _parse_loose_response(self, text: str) -> Dict[str, str]:
        """Parse OpenAI response into sections."""
        sections = {
            'summary': '',
            'methods': '',
            'results': '',
            'critique': '',
            'gaps': '',
            'keywords': '',
            'connections': ''
        }
        
        lines = text.split('\n')
        current = None
        
        for line in lines:
            line_lower = line.strip().lower()
            
            if 'summary' in line_lower and len(line_lower) < 20:
                current = 'summary'
                continue
            elif 'method' in line_lower and len(line_lower) < 20:
                current = 'methods'
                continue
            elif 'result' in line_lower and len(line_lower) < 20:
                current = 'results'
                continue
            elif 'critique' in line_lower or 'evaluation' in line_lower:
                current = 'critique'
                continue
            elif 'gap' in line_lower or 'future' in line_lower:
                current = 'gaps'
                continue
            elif 'keyword' in line_lower:
                current = 'keywords'
                continue
            elif 'connection' in line_lower or 'related' in line_lower:
                current = 'connections'
                continue
            
            if current and line.strip():
                sections[current] += line + '\n'
        
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def test_connection(self) -> bool:
        """Test OpenAI connectivity."""
        try:
            response = self.session.post(
                self.base_url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 1
                },
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter provider (fallback)."""
    
    def __init__(self, api_key: str, model: str = "stepfun/step-3.5-flash:free"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://hermes-agent.local",
            "X-Title": "AI Health Lit Review"
        })
    
    def summarize(self, paper: Dict[str, Any], max_words: int = 300) -> Optional[Dict[str, str]]:
        """Summarize using OpenRouter with retry logic for rate limits."""
        prompt = self._build_prompt(paper, max_words)
        
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    self.base_url,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are an AI research expert."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_words * 2,
                        "temperature": 0.3
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        message = result['choices'][0]['message']
                        # Some OpenRouter models (StepFun) return reasoning instead of content
                        text = message.get('content')
                        if text is None:
                            # Try reasoning field (used by some models)
                            text = message.get('reasoning', '')
                        if text:
                            parsed = self._parse_loose_response(text)
                            return self._postprocess_sections(parsed, paper, text)
                        else:
                            logger.warning(f"OpenRouter returned empty content on attempt {attempt+1}")
                            return None
                    else:
                        logger.warning(f"OpenRouter returned no choices on attempt {attempt+1}")
                        return None
                
                elif response.status_code == 429:
                    # Rate limited - parse retry-after header if present
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        delay = int(retry_after)
                    else:
                        delay = base_delay * (2 ** attempt)  # exponential backoff
                    
                    logger.warning(f"OpenRouter rate limited (429). Retrying in {delay}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(delay)
                    continue
                
                else:
                    logger.error(f"OpenRouter error {response.status_code}: {response.text[:200]}")
                    return None
                    
            except Exception as e:
                logger.error(f"OpenRouter request failed on attempt {attempt+1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                else:
                    return None
        
        logger.error(f"OpenRouter failed after {max_retries} attempts")
        return None
    
    def _build_prompt(self, paper: Dict[str, Any], max_words: int) -> str:
        return f"""Paper: {paper['title']}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}
Venue: {paper.get('venue', 'Unknown')}

Output in this exact format:
===SUMMARY===
===METHODS===
===RESULTS===
===CRITIQUE===
===GAPS===
===KEYWORDS===
===CONNECTIONS===

Fill each section."""
    
    def _parse_loose_response(self, text: str) -> Dict[str, str]:
        """Parse response using ===SECTION=== markers. If none found, return raw text in summary."""
        sections = {
            'summary': '',
            'methods': '',
            'results': '',
            'critique': '',
            'gaps': '',
            'keywords': '',
            'connections': ''
        }
        
        lines = text.split('\n')
        current = None
        found_markers = False
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Check for ===MARKER=== format
            if line_stripped.startswith('===') and line_stripped.endswith('==='):
                found_markers = True
                marker = line_stripped[3:-3].strip().lower()
                if marker == 'summary':
                    current = 'summary'
                elif marker == 'methods':
                    current = 'methods'
                elif marker == 'results':
                    current = 'results'
                elif marker == 'critique':
                    current = 'critique'
                elif marker == 'gaps':
                    current = 'gaps'
                elif marker == 'keywords':
                    current = 'keywords'
                elif marker in ('connections', 'related'):
                    current = 'connections'
                else:
                    current = None
                continue
            
            # Fallback: keyword detection (only if no formal markers found yet)
            if current is None and not found_markers:
                if 'summary' in line_lower and len(line_lower) < 20:
                    current = 'summary'
                elif 'method' in line_lower and len(line_lower) < 20:
                    current = 'methods'
                elif 'result' in line_lower and len(line_lower) < 20:
                    current = 'results'
                elif 'critique' in line_lower or 'evaluation' in line_lower:
                    current = 'critique'
                elif 'gap' in line_lower or 'future' in line_lower:
                    current = 'gaps'
                elif 'keyword' in line_lower:
                    current = 'keywords'
                elif 'connection' in line_lower:
                    current = 'connections'
                else:
                    # No section header found, skip this line
                    continue
            
            if current and line_stripped:
                sections[current] += line_stripped + '\n'
        
        # Clean up
        for key in sections:
            sections[key] = sections[key].strip()
        
        # If no structured sections were found, put everything in summary as raw text
        if not found_markers and all(not v for v in sections.values()):
            sections['summary'] = text.strip()
        
        return sections
    
    def _postprocess_sections(self, sections: Dict[str, str], paper: Dict[str, Any], raw_text: str) -> Dict[str, str]:
        """Repair low-quality/empty structured output with deterministic fallbacks from the paper metadata."""
        abstract = (paper.get('abstract') or '').strip()
        title = (paper.get('title') or '').strip()
        raw_lower = (raw_text or '').lower()
        
        meta_reasoning_markers = [
            'okay, let me', 'i need to', 'the user wants', 'the paper details',
            'looking at the abstract', 'first, i need', 'now, let\'s extract'
        ]
        looks_like_reasoning = any(marker in raw_lower[:800] for marker in meta_reasoning_markers)
        
        abstract_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if s.strip()]
        title_lower = title.lower()
        abstract_lower = abstract.lower()
        
        def shorten(text: str, limit: int = 320) -> str:
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:limit].rstrip() + ('...' if len(text) > limit else '')
        
        if looks_like_reasoning or not sections.get('summary'):
            if abstract_sentences:
                sections['summary'] = shorten(' '.join(abstract_sentences[:2]), 420)
            elif title:
                sections['summary'] = shorten(title, 220)
        
        if not sections.get('methods'):
            method_bits = []
            if any(term in abstract_lower for term in ['retrospective', 'prospective', 'multicenter', 'cohort', 'randomized']):
                for term in ['retrospective', 'prospective', 'multicenter', 'cohort', 'randomized']:
                    if term in abstract_lower:
                        method_bits.append(term)
            if any(term in title_lower + ' ' + abstract_lower for term in ['deep learning', 'machine learning', 'large language model', 'llm', 'radiomics', 'multimodal']):
                for term in ['deep learning', 'machine learning', 'large language model', 'radiomics', 'multimodal']:
                    if term in title_lower + ' ' + abstract_lower:
                        method_bits.append(term)
            if abstract_sentences:
                sections['methods'] = shorten(abstract_sentences[0], 320)
                if method_bits:
                    sections['methods'] += ' Key signals: ' + ', '.join(dict.fromkeys(method_bits)) + '.'
        
        if not sections.get('results') and abstract_sentences:
            result_sentences = [s for s in abstract_sentences if re.search(r'\b\d+(?:\.\d+)?%|\bauroc\b|\bauc\b|\baccuracy\b|\bsensitivity\b|\bspecificity\b|\bf1\b', s, re.I)]
            sections['results'] = shorten(' '.join(result_sentences[:2]) if result_sentences else abstract_sentences[-1], 320)
        
        if not sections.get('critique') or looks_like_reasoning:
            critique_parts = []
            if 'single-center' in abstract_lower:
                critique_parts.append('Single-center validation may limit generalizability.')
            if 'retrospective' in abstract_lower:
                critique_parts.append('Retrospective design may not reflect prospective deployment performance.')
            if 'multicenter' not in abstract_lower:
                critique_parts.append('External validation details are unclear from the available metadata.')
            if not critique_parts:
                critique_parts.append('The abstract alone provides limited detail on datasets, baselines, and error analysis.')
            sections['critique'] = ' '.join(critique_parts)
        
        if not sections.get('gaps'):
            sections['gaps'] = 'Need clearer reporting on external validation, subgroup performance, and real-world clinical impact.'
        
        if not sections.get('keywords'):
            kws = []
            for term in ['artificial intelligence', 'machine learning', 'deep learning', 'large language model', 'multimodal', 'radiology', 'oncology', 'pathology', 'clinical', 'diagnosis', 'prediction', 'biomarker', 'diabetes']:
                if term in title_lower + ' ' + abstract_lower:
                    kws.append(term)
            sections['keywords'] = kws[:6]  # always a list
        
        if not sections.get('connections'):
            sections['connections'] = 'Related to recent AI-for-clinical-decision-support and medical-imaging validation literature.'
        
        return sections
    
    def test_connection(self) -> bool:
        """Test OpenRouter connectivity (checks auth, not rate limits)."""
        try:
            # Use a tiny request to test connectivity
            response = self.session.post(
                self.base_url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 1
                },
                timeout=10
            )
            # Accept 200 (OK) or 429 (rate-limited) as "connected"
            # Because 429 means the key works but quota exhausted temporarily
            return response.status_code in (200, 429)
        except:
            return False

class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider (runs models on local GPU/CPU)."""
    
    def __init__(self, api_key: str = "", model: str = "llama3:8b"):
        # api_key not used for local, but kept for interface consistency
        self.api_key = api_key
        self.model = model
        self.base_url = "http://localhost:11434/v1/chat/completions"  # OpenAI-compatible API
        self.session = requests.Session()
    
    def summarize(self, paper: Dict[str, Any], max_words: int = 300) -> Optional[Dict[str, str]]:
        """Summarize using local Ollama model."""
        prompt = self._build_prompt(paper, max_words)
        
        try:
            response = self.session.post(
                self.base_url,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an AI research expert. Provide structured outputs with exact section headers."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_words * 2,
                    "temperature": 0.3,
                    "stream": False
                },
                timeout=120  # Local inference can be slower
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error {response.status_code}: {response.text[:200]}")
                return None
            
            result = response.json()
            if 'choices' in result and result['choices']:
                text = result['choices'][0]['message']['content']
                return self._parse_loose_response(text)
            else:
                logger.warning("Ollama returned no choices")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.error("Ollama not running. Start with: ollama serve")
            return None
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return None
    
    def _build_prompt(self, paper: Dict[str, Any], max_words: int) -> str:
        return f"""Review this AI in healthcare paper:

Title: {paper['title']}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}
Venue: {paper.get('venue', 'Unknown')}

Provide a structured review with these exact section headers (one per line, plain text):
SUMMARY
[summary text]

METHODS
[methods text]

RESULTS
[results text]

CRITIQUE
[critique text]

GAPS
[gaps text]

KEYWORDS
[keywords, comma-separated]

CONNECTIONS
[connections to other work]

Each section should be concise but substantive."""
    
    def _parse_loose_response(self, text: str) -> Dict[str, str]:
        """Parse Ollama response into sections."""
        sections = {
            'summary': '',
            'methods': '',
            'results': '',
            'critique': '',
            'gaps': '',
            'keywords': '',
            'connections': ''
        }
        
        lines = text.split('\n')
        current = None
        
        for line in lines:
            line_lower = line.strip().lower()
            
            if 'summary' in line_lower and len(line_lower) < 20:
                current = 'summary'
                continue
            elif 'method' in line_lower and len(line_lower) < 20:
                current = 'methods'
                continue
            elif 'result' in line_lower and len(line_lower) < 20:
                current = 'results'
                continue
            elif 'critique' in line_lower or 'evaluation' in line_lower:
                current = 'critique'
                continue
            elif 'gap' in line_lower or 'future' in line_lower:
                current = 'gaps'
                continue
            elif 'keyword' in line_lower:
                current = 'keywords'
                continue
            elif 'connection' in line_lower or 'related' in line_lower:
                current = 'connections'
                continue
            
            if current and line.strip():
                sections[current] += line + '\n'
        
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and model is available."""
        try:
            # First check if Ollama server is up
            response = self.session.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            
            # Check if model is available
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            return self.model in model_names or f"{self.model}:latest" in model_names
        except:
            return False

class Summarizer:
    """Main summarizer with fallback chain."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models_config = config.get('summarization', {}).get('models', {})
        self.providers = []
        
        # Initialize providers in priority order
        self._init_providers()
    
    def _init_providers(self):
        """Initialize provider chain based on config and available API keys."""
        # Get provider configs from YAML (order matters!)
        providers_config = self.config.get('providers', {})
        
        # Get API keys from environment
        api_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'gemini': os.getenv('GEMINI_API_KEY'),
            'huggingface': os.getenv('HUGGINGFACE_API_KEY'),
            'openrouter': os.getenv('OPENROUTER_API_KEY')
        }
        
        # Map provider names to classes
        provider_classes = {
            'ollama': OllamaProvider,
            'openai': OpenAIProvider,
            'gemini': GeminiProvider,
            'openrouter': OpenRouterProvider,
            'huggingface': HuggingFaceProvider
        }
        
        # Initialize in order defined in config
        for name, p_config in providers_config.items():
            if not p_config.get('enabled', False):
                logger.info(f"Provider {name} disabled in config, skipping")
                continue
            
            model = p_config.get('model')
            provider_class = provider_classes.get(name)
            if not provider_class:
                logger.warning(f"Unknown provider: {name}")
                continue
            
            # Ollama doesn't need an API key
            if name == 'ollama':
                api_key = ""  # Dummy, not used
            else:
                api_key = api_keys.get(name)
                if not api_key:
                    logger.info(f"No API key found for provider: {name}, skipping")
                    continue
            
            try:
                # Initialize with specific model if provided
                if model:
                    provider = provider_class(api_key, model=model)
                else:
                    provider = provider_class(api_key)
                
                # Test connection
                if provider.test_connection():
                    logger.info(f"Provider {name} ({model or 'default'}) initialized and tested OK")
                    self.providers.append((name, provider))
                else:
                    logger.warning(f"Provider {name} failed connection test, skipping")
            except Exception as e:
                logger.error(f"Failed to initialize provider {name}: {e}")
        
        if not self.providers:
            raise RuntimeError("No summarization providers available! Please set at least one API key.")
    
    def summarize_paper(self, paper: Dict[str, Any], max_words: int = 300) -> Optional[Dict[str, str]]:
        """Summarize a paper using the first available provider (with retries)."""
        for provider_name, provider in self.providers:
            try:
                logger.info(f"Attempting to summarize paper {paper['paper_id']} using {provider_name}")
                result = provider.summarize(paper, max_words)
                if result:
                    logger.info(f"Successfully summarized with {provider_name}")
                    # Add provider info
                    result['summarized_by'] = provider_name
                    result['summarized_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    return result
                else:
                    logger.warning(f"{provider_name} returned None, trying next provider...")
            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                continue
        
        logger.error(f"All providers failed for paper {paper['paper_id']}")
        return None
    
    def batch_summarize(self, papers: List[Dict[str, Any]], max_words: int = 300) -> List[Dict[str, Any]]:
        """Summarize multiple papers."""
        results = []
        for paper in papers:
            summary = self.summarize_paper(paper, max_words)
            if summary:
                paper.update(summary)
                results.append(paper)
            else:
                logger.error(f"Failed to summarize {paper['paper_id']}")
        return results

if __name__ == "__main__":
    # Quick test with sample paper
    sample_paper = {
        'paper_id': 'test:123',
        'title': 'A Large Language Model for Clinical Decision Support',
        'authors': ['John Doe', 'Jane Smith'],
        'abstract': 'We present a novel LLM architecture...',
        'venue': 'NeurIPS 2024',
        'published_date': '2025-04-01'
    }
    
    with open('config.yaml') as f:
        import yaml
        config = yaml.safe_load(f)
    
    summarizer = Summarizer(config)
    result = summarizer.summarize_paper(sample_paper)
    print("Summary result:", result.keys() if result else "None")