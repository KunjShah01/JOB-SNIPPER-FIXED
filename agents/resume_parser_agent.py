"""
Resume Parser Agent
Parses resume content and extracts structured information
"""

from agents.multi_ai_base import MultiAIAgent
from agents.agent_base import FallbackAgent
import re
import logging

logger = logging.getLogger(__name__)

class ResumeParserAgent(MultiAIAgent):
    """Agent for parsing resume content"""
    
    def __init__(self):
        super().__init__(
            name="ResumeParser",
            prompt_template="""
            Parse the following resume text and extract structured information.
            Return a JSON object with the following fields:
            - name: Full name of the candidate
            - email: Email address
            - phone: Phone number
            - skills: List of technical skills
            - experience: List of work experiences with company, role, and duration
            - education: List of educational qualifications
            - summary: Brief professional summary
            
            Resume text:
            {input}
            
            Return only valid JSON without any additional text.
            """,
            use_gemini=True,
            use_mistral=True,
            return_mode="aggregate"
        )
    
    def run(self, input_data):
        """
        Parse resume content
        
        Args:
            input_data: Resume text or message containing resume text
        
        Returns:
            Parsed resume data
        """
        try:
            # Parse input
            parsed_input = self.parse_input(input_data)
            resume_text = ""
            
            if isinstance(parsed_input, dict):
                resume_text = parsed_input.get("resume_text", parsed_input.get("data", ""))
            else:
                resume_text = str(parsed_input)
            
            if not resume_text.strip():
                return self.fallback_parsing("")
            
            # Try AI parsing first
            try:
                ai_result = super().run(resume_text)
                
                if ai_result.get("success") and ai_result.get("response"):
                    # Try to parse AI response as JSON
                    from utils.json_helper import safe_json_loads
                    parsed_data = safe_json_loads(ai_result["response"])
                    
                    # Validate and enhance the parsed data
                    validated_data = self.validate_parsed_data(parsed_data, resume_text)
                    
                    return {
                        "success": True,
                        "parsed_data": validated_data,
                        "method": "ai_parsing",
                        "provider": ai_result.get("primary_provider", "unknown")
                    }
                else:
                    raise Exception("AI parsing failed")
                    
            except Exception as e:
                logger.warning(f"AI parsing failed: {e}, using fallback")
                return self.fallback_parsing(resume_text)
                
        except Exception as e:
            logger.error(f"Error in resume parsing: {e}")
            return self.fallback_parsing(input_data)
    
    def fallback_parsing(self, resume_text):
        """
        Fallback parsing using regex and text analysis
        
        Args:
            resume_text: Resume text to parse
        
        Returns:
            Parsed resume data using fallback methods
        """
        try:
            if not resume_text:
                resume_text = ""
            
            text = str(resume_text).lower()
            original_text = str(resume_text)
            
            # Extract basic information using regex
            parsed_data = {
                "name": self._extract_name(original_text),
                "email": self._extract_email(text),
                "phone": self._extract_phone(text),
                "skills": self._extract_skills(text),
                "experience": self._extract_experience(original_text),
                "education": self._extract_education(original_text),
                "summary": self._extract_summary(original_text)
            }
            
            return {
                "success": True,
                "parsed_data": parsed_data,
                "method": "fallback_parsing",
                "provider": "regex_parser"
            }
            
        except Exception as e:
            logger.error(f"Fallback parsing failed: {e}")
            return {
                "success": False,
                "parsed_data": self._get_empty_structure(),
                "method": "error_fallback",
                "error": str(e)
            }
    
    def _extract_name(self, text):
        """Extract name from resume text"""
        try:
            lines = text.split('\n')
            # Usually name is in the first few lines
            for line in lines[:5]:
                line = line.strip()
                if len(line) > 2 and len(line) < 50:
                    # Check if line looks like a name (contains letters and spaces)
                    if re.match(r'^[A-Za-z\s\.]+$', line) and len(line.split()) >= 2:
                        return line
            return "Name not found"
        except:
            return "Name not found"
    
    def _extract_email(self, text):
        """Extract email from resume text"""
        try:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            return emails[0] if emails else "Email not found"
        except:
            return "Email not found"
    
    def _extract_phone(self, text):
        """Extract phone number from resume text"""
        try:
            phone_patterns = [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
                r'\+\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
            ]
            
            for pattern in phone_patterns:
                phones = re.findall(pattern, text)
                if phones:
                    return phones[0]
            
            return "Phone not found"
        except:
            return "Phone not found"
    
    def _extract_skills(self, text):
        """Extract skills from resume text"""
        try:
            # Common technical skills
            skill_keywords = [
                'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'html', 'css',
                'machine learning', 'data science', 'aws', 'docker', 'kubernetes',
                'git', 'linux', 'windows', 'excel', 'powerpoint', 'word',
                'project management', 'agile', 'scrum', 'leadership', 'communication'
            ]
            
            found_skills = []
            for skill in skill_keywords:
                if skill in text:
                    found_skills.append(skill.title())
            
            # Look for skills sections
            skills_section_patterns = [
                r'skills?[:\-\s]+(.*?)(?:\n\n|\n[A-Z])',
                r'technical skills?[:\-\s]+(.*?)(?:\n\n|\n[A-Z])',
                r'technologies?[:\-\s]+(.*?)(?:\n\n|\n[A-Z])'
            ]
            
            for pattern in skills_section_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    # Split by common delimiters
                    skills_text = re.split(r'[,;•\n]', match)
                    for skill in skills_text:
                        skill = skill.strip()
                        if skill and len(skill) > 1 and len(skill) < 30:
                            found_skills.append(skill.title())
            
            return list(set(found_skills)) if found_skills else ["Skills not found"]
            
        except:
            return ["Skills not found"]
    
    def _extract_experience(self, text):
        """Extract work experience from resume text"""
        try:
            experience = []
            
            # Look for experience sections
            exp_patterns = [
                r'experience[:\-\s]+(.*?)(?:\n\n|\neducation|\nskills)',
                r'work experience[:\-\s]+(.*?)(?:\n\n|\neducation|\nskills)',
                r'employment[:\-\s]+(.*?)(?:\n\n|\neducation|\nskills)'
            ]
            
            for pattern in exp_patterns:
                matches = re.findall(pattern, text.lower(), re.IGNORECASE | re.DOTALL)
                for match in matches:
                    # Split into individual experiences
                    exp_items = re.split(r'\n(?=[A-Z])', match)
                    for item in exp_items:
                        item = item.strip()
                        if len(item) > 10:
                            experience.append(item[:200])  # Limit length
            
            return experience if experience else ["Experience not found"]
            
        except:
            return ["Experience not found"]
    
    def _extract_education(self, text):
        """Extract education from resume text"""
        try:
            education = []
            
            # Look for education sections
            edu_patterns = [
                r'education[:\-\s]+(.*?)(?:\n\n|\nexperience|\nskills)',
                r'academic[:\-\s]+(.*?)(?:\n\n|\nexperience|\nskills)',
                r'qualifications?[:\-\s]+(.*?)(?:\n\n|\nexperience|\nskills)'
            ]
            
            for pattern in edu_patterns:
                matches = re.findall(pattern, text.lower(), re.IGNORECASE | re.DOTALL)
                for match in matches:
                    # Split into individual education items
                    edu_items = re.split(r'\n(?=[A-Z])', match)
                    for item in edu_items:
                        item = item.strip()
                        if len(item) > 5:
                            education.append(item[:200])  # Limit length
            
            return education if education else ["Education not found"]
            
        except:
            return ["Education not found"]
    
    def _extract_summary(self, text):
        """Extract professional summary"""
        try:
            lines = text.split('\n')
            
            # Look for summary sections
            summary_keywords = ['summary', 'objective', 'profile', 'about']
            
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                for keyword in summary_keywords:
                    if keyword in line_lower and ':' in line_lower:
                        # Get next few lines as summary
                        summary_lines = []
                        for j in range(i+1, min(i+5, len(lines))):
                            if lines[j].strip() and not lines[j].isupper():
                                summary_lines.append(lines[j].strip())
                            else:
                                break
                        if summary_lines:
                            return ' '.join(summary_lines)[:300]
            
            # If no summary section found, use first paragraph
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if len(para) > 50 and len(para) < 500:
                    return para[:300]
            
            return "Summary not found"
            
        except:
            return "Summary not found"
    
    def validate_parsed_data(self, parsed_data, original_text):
        """Validate and enhance parsed data"""
        try:
            if not isinstance(parsed_data, dict):
                return self._get_empty_structure()
            
            # Ensure all required fields exist
            required_fields = ["name", "email", "phone", "skills", "experience", "education", "summary"]
            
            for field in required_fields:
                if field not in parsed_data or not parsed_data[field]:
                    # Try to extract using fallback methods
                    if field == "name":
                        parsed_data[field] = self._extract_name(original_text)
                    elif field == "email":
                        parsed_data[field] = self._extract_email(original_text.lower())
                    elif field == "phone":
                        parsed_data[field] = self._extract_phone(original_text.lower())
                    elif field == "skills":
                        parsed_data[field] = self._extract_skills(original_text.lower())
                    elif field == "experience":
                        parsed_data[field] = self._extract_experience(original_text)
                    elif field == "education":
                        parsed_data[field] = self._extract_education(original_text)
                    elif field == "summary":
                        parsed_data[field] = self._extract_summary(original_text)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error validating parsed data: {e}")
            return self._get_empty_structure()
    
    def _get_empty_structure(self):
        """Get empty data structure"""
        return {
            "name": "Not found",
            "email": "Not found",
            "phone": "Not found",
            "skills": ["Not found"],
            "experience": ["Not found"],
            "education": ["Not found"],
            "summary": "Not found"
        }