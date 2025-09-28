"""
LLM-based edit planning service.
"""
import json
import os
from typing import Dict, List

import google.generativeai as genai


async def plan_changes(prompt: str, repo_structure: str) -> Dict[str, List[str]]:
    """
    Use Gemini to analyze the repository and plan which files need to be changed.
    
    Args:
        prompt: User's natural language request
        repo_structure: String representation of the repository structure
        
    Returns:
        Dictionary with keys 'edit', 'create', 'delete' containing lists of file paths
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    system_prompt = """You are an expert software engineer analyzing a repository structure to plan code changes.

Your task is to analyze the user's request and the repository structure, then return a JSON object specifying exactly which files need to be modified.

IMPORTANT RULES:
1. Return ONLY a valid JSON object, no other text
2. Use relative paths from the repository root
3. Be conservative - only include files that definitely need changes
4. Focus on the most important files that directly address the user's request
5. Limit changes to a maximum of 5-8 files to keep the scope manageable
6. Consider the existing codebase structure and patterns

JSON Format:
{
  "edit": ["path/to/existing/file1.py", "path/to/existing/file2.js"],
  "create": ["path/to/new/file3.py"],
  "delete": ["path/to/obsolete/file4.py"]
}

Common scenarios:
- Adding features: Usually edit main files + create new modules
- Bug fixes: Usually edit 1-2 existing files
- Refactoring: Edit existing files, sometimes create new ones
- Adding dependencies: Edit package.json/requirements.txt + main files
- Configuration changes: Edit config files + affected modules"""

    user_message = f"""USER REQUEST: {prompt}

REPOSITORY STRUCTURE:
{repo_structure}

Analyze this request and repository structure. Return a JSON object specifying which files to edit, create, or delete."""

    try:
        full_prompt = f"{system_prompt}\n\n{user_message}"
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        
        # Extract the JSON from the response
        content = response.text.strip()
        
        # Try to parse as JSON
        try:
            changes_plan = json.loads(content)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                changes_plan = json.loads(json_match.group())
            else:
                raise ValueError("No valid JSON found in response")
        
        # Validate the structure
        if not isinstance(changes_plan, dict):
            raise ValueError("Response is not a JSON object")
        
        # Ensure all required keys exist with default empty lists
        result = {
            "edit": changes_plan.get("edit", []),
            "create": changes_plan.get("create", []),
            "delete": changes_plan.get("delete", [])
        }
        
        # Validate that all values are lists
        for key, value in result.items():
            if not isinstance(value, list):
                result[key] = []
        
        # Limit the number of files to avoid overwhelming changes
        max_files = 8
        total_files = len(result["edit"]) + len(result["create"]) + len(result["delete"])
        
        if total_files > max_files:
            # Prioritize edits over creates, and creates over deletes
            result["edit"] = result["edit"][:6]
            result["create"] = result["create"][:2]
            result["delete"] = result["delete"][:2]
        
        return result
        
    except Exception as e:
        # Fallback: return a minimal change plan
        fallback_plan = {
            "edit": [],
            "create": [],
            "delete": []
        }
        
        # Try to make a simple guess based on common patterns
        if "readme" in prompt.lower() or "documentation" in prompt.lower():
            fallback_plan["edit"] = ["README.md"]
        elif "test" in prompt.lower():
            fallback_plan["create"] = ["test_new_feature.py"]
        elif "config" in prompt.lower():
            fallback_plan["edit"] = ["config.py", "settings.py"]
        
        return fallback_plan


def extract_project_info(repo_structure: str) -> Dict[str, str]:
    """
    Extract key information about the project from the repository structure.
    
    Args:
        repo_structure: String representation of the repository structure
        
    Returns:
        Dictionary containing project information
    """
    info = {
        "language": "unknown",
        "framework": "unknown",
        "type": "unknown"
    }
    
    # Detect primary language
    if "package.json" in repo_structure:
        info["language"] = "javascript"
        if "react" in repo_structure.lower():
            info["framework"] = "react"
        elif "vue" in repo_structure.lower():
            info["framework"] = "vue"
        elif "angular" in repo_structure.lower():
            info["framework"] = "angular"
        elif "express" in repo_structure.lower():
            info["framework"] = "express"
        elif "next" in repo_structure.lower():
            info["framework"] = "nextjs"
    elif "requirements.txt" in repo_structure or "pyproject.toml" in repo_structure:
        info["language"] = "python"
        if "django" in repo_structure.lower():
            info["framework"] = "django"
        elif "flask" in repo_structure.lower():
            info["framework"] = "flask"
        elif "fastapi" in repo_structure.lower():
            info["framework"] = "fastapi"
    elif "Gemfile" in repo_structure:
        info["language"] = "ruby"
        info["framework"] = "rails" if "rails" in repo_structure.lower() else "ruby"
    elif "pom.xml" in repo_structure or "build.gradle" in repo_structure:
        info["language"] = "java"
        if "spring" in repo_structure.lower():
            info["framework"] = "spring"
    elif "Cargo.toml" in repo_structure:
        info["language"] = "rust"
    elif "go.mod" in repo_structure:
        info["language"] = "go"
    
    # Detect project type
    if "api" in repo_structure.lower() or "server" in repo_structure.lower():
        info["type"] = "api"
    elif "frontend" in repo_structure.lower() or "client" in repo_structure.lower():
        info["type"] = "frontend"
    elif "mobile" in repo_structure.lower() or "android" in repo_structure.lower() or "ios" in repo_structure.lower():
        info["type"] = "mobile"
    elif "cli" in repo_structure.lower() or "command" in repo_structure.lower():
        info["type"] = "cli"
    elif "lib" in repo_structure.lower() or "package" in repo_structure.lower():
        info["type"] = "library"
    else:
        info["type"] = "application"
    
    return info


def validate_file_paths(repo_structure: str, file_paths: List[str]) -> List[str]:
    """
    Validate that file paths make sense given the repository structure.
    
    Args:
        repo_structure: String representation of the repository structure
        file_paths: List of file paths to validate
        
    Returns:
        List of validated file paths (may be modified or filtered)
    """
    validated_paths = []
    
    for path in file_paths:
        # Skip empty paths
        if not path or not path.strip():
            continue
            
        # Normalize path separators
        path = path.replace('\\', '/')
        
        # Remove leading slashes
        path = path.lstrip('/')
        
        # Skip paths that go outside the repository
        if '..' in path:
            continue
            
        # Skip binary file extensions
        binary_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.pdf',
                           '.zip', '.tar', '.gz', '.rar', '.7z', '.exe', '.dll', '.so',
                           '.dylib', '.bin', '.dat', '.sqlite', '.db'}
        
        if any(path.lower().endswith(ext) for ext in binary_extensions):
            continue
            
        validated_paths.append(path)
    
    return validated_paths