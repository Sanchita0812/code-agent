"""
Repository structure analysis service.
"""
import os
from pathlib import Path
from typing import List, Set


def analyze_repo_structure(repo_path: str) -> str:
    """
    Analyze the structure of a cloned repository and generate a concise summary.
    
    Args:
        repo_path: Path to the cloned repository
        
    Returns:
        String containing a formatted summary of the repository structure
    """
    # Files and directories to ignore
    IGNORE_PATTERNS = {
        '.git', '.gitignore', '.github', '.vscode', '.idea',
        'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache',
        'venv', 'env', '.env', '.venv',
        'dist', 'build', 'target', 'out',
        '.DS_Store', 'Thumbs.db',
        '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll',
        '*.log', '*.tmp', '*.cache',
        'package-lock.json', 'yarn.lock', 'poetry.lock'
    }
    
    IMPORTANT_FILES = {
        'package.json', 'requirements.txt', 'Pipfile', 'pyproject.toml',
        'Dockerfile', 'docker-compose.yml', 'Makefile',
        'README.md', 'LICENSE', 'CHANGELOG.md',
        '.env.example', 'config.py', 'settings.py'
    }
    
    def should_ignore(path: str, name: str) -> bool:
        """Check if a file or directory should be ignored."""
        # Check exact matches
        if name in IGNORE_PATTERNS:
            return True
        
        # Check pattern matches
        for pattern in IGNORE_PATTERNS:
            if pattern.startswith('*') and name.endswith(pattern[1:]):
                return True
        
        # Ignore hidden files/directories (except important ones)
        if name.startswith('.') and name not in IMPORTANT_FILES:
            return True
            
        return False
    
    def get_file_info(file_path: str) -> dict:
        """Get basic information about a file."""
        try:
            stat = os.stat(file_path)
            size = stat.st_size
            
            # Try to determine if it's a text file
            is_text = True
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Try to read first 100 chars
            except:
                is_text = False
            
            return {
                'size': size,
                'is_text': is_text
            }
        except:
            return {'size': 0, 'is_text': False}
    
    # Walk through the repository
    structure = []
    file_types = {}
    total_files = 0
    
    for root, dirs, files in os.walk(repo_path):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(root, d)]
        
        # Get relative path from repo root
        rel_path = os.path.relpath(root, repo_path)
        if rel_path == '.':
            rel_path = ''
        
        # Process files in current directory
        current_files = []
        for file in files:
            if should_ignore(root, file):
                continue
                
            file_path = os.path.join(root, file)
            file_info = get_file_info(file_path)
            
            # Track file extensions
            ext = Path(file).suffix.lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
            
            # Mark important files
            importance = "📄"
            if file in IMPORTANT_FILES:
                importance = "⭐"
            elif ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.rs', '.go']:
                importance = "📝"
            elif ext in ['.md', '.txt', '.rst']:
                importance = "📋"
            elif ext in ['.json', '.yaml', '.yml', '.toml', '.xml']:
                importance = "⚙️"
            
            current_files.append(f"{importance} {file}")
            total_files += 1
        
        # Add directory info if it has files
        if current_files:
            if rel_path:
                structure.append(f"\n📁 {rel_path}/")
            else:
                structure.append("📁 / (root)")
            
            # Limit files shown per directory
            if len(current_files) > 10:
                structure.extend([f"  {f}" for f in current_files[:8]])
                structure.append(f"  ... and {len(current_files) - 8} more files")
            else:
                structure.extend([f"  {f}" for f in current_files])
    
    # Generate summary
    summary_parts = [
        "REPOSITORY STRUCTURE ANALYSIS",
        "=" * 40,
        f"Total files analyzed: {total_files}",
        ""
    ]
    
    # File type distribution
    if file_types:
        summary_parts.append("FILE TYPES:")
        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_types[:10]:  # Top 10 file types
            summary_parts.append(f"  {ext}: {count} files")
        summary_parts.append("")
    
    # Key files detection
    key_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file in IMPORTANT_FILES:
                rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                key_files.append(rel_path)
    
    if key_files:
        summary_parts.append("KEY CONFIGURATION FILES:")
        for file in key_files[:5]:  # Show top 5 key files
            summary_parts.append(f"  ⭐ {file}")
        summary_parts.append("")
    
    # Directory structure
    summary_parts.append("DIRECTORY STRUCTURE:")
    summary_parts.extend(structure)
    
    # Add helpful context
    summary_parts.extend([
        "",
        "ANALYSIS NOTES:",
        "- Files marked with ⭐ are configuration/important files",
        "- Files marked with 📝 are source code files", 
        "- Files marked with ⚙️ are configuration files",
        "- Hidden files and common build artifacts are excluded",
        f"- This analysis covers {total_files} files in the repository"
    ])
    
    return "\n".join(summary_parts)


def get_file_summary(repo_path: str, file_path: str) -> str:
    """
    Get a summary of a specific file's content.
    
    Args:
        repo_path: Path to the repository
        file_path: Relative path to the file within the repo
        
    Returns:
        String summary of the file content
    """
    full_path = os.path.join(repo_path, file_path)
    
    if not os.path.exists(full_path):
        return f"File {file_path} does not exist"
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        summary = [
            f"FILE: {file_path}",
            f"Lines: {len(lines)}",
            f"Size: {len(content)} characters",
            ""
        ]
        
        # Show first few lines if it's a small file
        if len(lines) <= 20:
            summary.append("CONTENT:")
            summary.extend([f"  {i+1:2d}: {line}" for i, line in enumerate(lines)])
        else:
            summary.append("CONTENT (first 10 lines):")
            summary.extend([f"  {i+1:2d}: {line}" for i, line in enumerate(lines[:10])])
            summary.append(f"  ... ({len(lines) - 10} more lines)")
        
        return "\n".join(summary)
        
    except UnicodeDecodeError:
        return f"File {file_path} appears to be binary (cannot read as text)"
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"