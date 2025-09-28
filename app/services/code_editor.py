"""
Gemini-based code editing service.
"""
import os
from typing import Tuple

import google.generativeai as genai


async def apply_edits(repo_path: str, file_path: str, prompt: str, is_new_file: bool = False) -> None:
    """
    Use Gemini to edit a specific file based on the user's prompt.
    
    Args:
        repo_path: Path to the repository
        file_path: Relative path to the file within the repo
        prompt: User's natural language request
        is_new_file: Whether this is a new file being created
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    full_file_path = os.path.join(repo_path, file_path)
    
    # Read existing file content or prepare for new file
    if is_new_file or not os.path.exists(full_file_path):
        existing_content = ""
        file_status = "NEW FILE"
    else:
        try:
            with open(full_file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            file_status = "EXISTING FILE"
        except UnicodeDecodeError:
            # Handle binary files or files with different encoding
            existing_content = ""
            file_status = "BINARY/ENCODED FILE"
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {str(e)}")
    
    # Determine file type for context
    file_extension = os.path.splitext(file_path)[1].lower()
    
    language_context = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript', 
        '.jsx': 'React JSX',
        '.tsx': 'React TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.go': 'Go',
        '.rs': 'Rust',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.xml': 'XML',
        '.md': 'Markdown',
        '.txt': 'Plain Text',
        '.sh': 'Shell Script',
        '.sql': 'SQL'
    }.get(file_extension, 'Plain Text')
    
    system_prompt = f"""You are an expert software engineer tasked with editing code files.

IMPORTANT RULES:
1. Return ONLY the complete file content, no explanations or markdown formatting
2. Make targeted changes that directly address the user's request
3. Preserve existing code structure and style unless changes are needed
4. Follow best practices for the {language_context} language
5. Ensure the code is syntactically correct and follows proper conventions
6. For new files, create complete, working code that serves the intended purpose
7. Do not add unnecessary comments unless they add significant value

FILE CONTEXT:
- File: {file_path}
- Language: {language_context}
- Status: {file_status}

If this is a new file, create complete, functional code that addresses the user's request.
If this is an existing file, make the minimal necessary changes while preserving the existing structure."""

    if is_new_file:
        user_message = f"""CREATE NEW FILE: {file_path}

USER REQUEST: {prompt}

Create a complete {language_context} file that addresses this request. Return only the file content."""
    else:
        user_message = f"""EDIT EXISTING FILE: {file_path}

USER REQUEST: {prompt}

CURRENT FILE CONTENT:
{existing_content}

Modify this file to address the user's request. Return the complete updated file content."""

    try:
        full_prompt = f"{system_prompt}\n\n{user_message}"
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4000,
            )
        )
        
        new_content = response.text.strip()
        
        # Remove markdown code blocks if present
        if new_content.startswith('```'):
            lines = new_content.split('\n')
            if len(lines) > 2:
                # Remove first and last lines (code block markers)
                new_content = '\n'.join(lines[1:-1])
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
        
        # Write the updated content
        with open(full_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    except Exception as e:
        raise Exception(f"Failed to edit file {file_path}: {str(e)}")


async def generate_pr_description(prompt: str, changes_plan: dict) -> Tuple[str, str]:
    """
    Generate a pull request title and description based on the user's prompt and changes.
    
    Args:
        prompt: User's original request
        changes_plan: Dictionary containing the planned changes
        
    Returns:
        Tuple of (title, description)
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    system_prompt = """You are tasked with creating a professional pull request title and description.

REQUIREMENTS:
1. Title should be concise (50 characters or less) and descriptive
2. Description should be professional and informative
3. Include a summary of changes made
4. Use proper markdown formatting for the description
5. Be specific about what was implemented/fixed/changed

FORMAT YOUR RESPONSE AS:
TITLE: Your pull request title here
DESCRIPTION:
Your detailed description here with proper markdown formatting"""

    files_summary = []
    if changes_plan.get('edit'):
        files_summary.append(f"Modified {len(changes_plan['edit'])} existing files")
    if changes_plan.get('create'):
        files_summary.append(f"Created {len(changes_plan['create'])} new files")
    if changes_plan.get('delete'):
        files_summary.append(f"Deleted {len(changes_plan['delete'])} files")
    
    user_message = f"""Generate a professional pull request title and description for these changes:

ORIGINAL REQUEST: {prompt}

CHANGES MADE:
{' | '.join(files_summary) if files_summary else 'Various file modifications'}

FILES AFFECTED:
- Edited: {', '.join(changes_plan.get('edit', [])) or 'None'}
- Created: {', '.join(changes_plan.get('create', [])) or 'None'}
- Deleted: {', '.join(changes_plan.get('delete', [])) or 'None'}"""

    try:
        full_prompt = f"{system_prompt}\n\n{user_message}"
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=1000,
            )
        )
        
        content = response.text.strip()
        
        # Parse the response
        lines = content.split('\n')
        title = ""
        description = ""
        
        in_description = False
        for line in lines:
            if line.startswith('TITLE:'):
                title = line[6:].strip()
            elif line.startswith('DESCRIPTION:'):
                in_description = True
            elif in_description:
                description += line + '\n'
        
        # Fallback if parsing fails
        if not title:
            title = f"AI Agent: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
        
        if not description:
            description = f"""## AI-Generated Changes

This pull request was created by an AI coding agent based on the following request:

> {prompt}

### Changes Summary
{' | '.join(files_summary) if files_summary else 'Various file modifications'}

### Files Modified
{'- ' + chr(10).join(f'`{f}`' for f in changes_plan.get('edit', [])) if changes_plan.get('edit') else ''}
{'- ' + chr(10).join(f'`{f}` (new)' for f in changes_plan.get('create', [])) if changes_plan.get('create') else ''}
{'- ' + chr(10).join(f'`{f}` (deleted)' for f in changes_plan.get('delete', [])) if changes_plan.get('delete') else ''}

### Notes
- This PR was generated automatically by an AI agent
- Please review all changes carefully before merging
- Test the changes in your development environment"""
        
        return title.strip(), description.strip()
        
    except Exception as e:
        # Fallback to simple description
        title = f"AI Agent: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
        description = f"""## AI-Generated Changes

This pull request was created by an AI coding agent.

**Original Request:** {prompt}

**Changes:** {' | '.join(files_summary) if files_summary else 'Various file modifications'}

Please review all changes carefully before merging."""
        
        return title, description


def validate_code_syntax(file_path: str, content: str) -> Tuple[bool, str]:
    """
    Basic syntax validation for common file types.
    
    Args:
        file_path: Path to the file
        content: File content to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.py':
            import ast
            ast.parse(content)
        elif file_extension == '.json':
            import json
            json.loads(content)
        elif file_extension in ['.yaml', '.yml']:
            import yaml
            yaml.safe_load(content)
        
        return True, ""
        
    except SyntaxError as e:
        return False, f"Syntax error: {str(e)}"
    except json.JSONDecodeError as e:
        return False, f"JSON error: {str(e)}"
    except yaml.YAMLError as e:
        return False, f"YAML error: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"