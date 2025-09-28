"""
Main API endpoint for the AI coding agent.
Handles the streaming workflow of analyzing repos and creating pull requests.
"""
import asyncio
import json
import os
import tempfile
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.request import CodeRequest
from app.services.git_service import GitService
from app.services.repo_analyzer import analyze_repo_structure
from app.services.edit_planner import plan_changes
from app.services.code_editor import apply_edits, generate_pr_description

router = APIRouter()


def create_sse_message(event: str, data: str) -> str:
    """Create a Server-Sent Events formatted message."""
    return f"event: {event}\ndata: {data}\n\n"


async def event_generator(request: CodeRequest) -> AsyncGenerator[str, None]:
    """
    Async generator that orchestrates the entire AI coding workflow
    and yields SSE messages at each step.
    """
    temp_dir = None
    
    try:
        # Initialize
        yield create_sse_message("start", "Initializing AI coding agent...")
        
        # Get environment variables
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(status_code=500, detail="GitHub token not configured")
            
        # Initialize services
        git_service = GitService(github_token)
        branch_name = f"ai-agent-{uuid.uuid4().hex[:8]}"
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        repo_path = os.path.join(temp_dir, "repo")
        
        yield create_sse_message("setup", f"Created temporary workspace: {branch_name}")
        
        # Clone repository
        yield create_sse_message("clone", "Cloning repository...")
        await asyncio.sleep(0.1)  # Small delay for better UX
        
        try:
            git_service.clone_repo(str(request.repoUrl), repo_path)
            yield create_sse_message("clone", "Repository cloned successfully.")
        except Exception as e:
            yield create_sse_message("error", f"Failed to clone repository: {str(e)}")
            return
            
        # Analyze repository structure
        yield create_sse_message("analyze", "Analyzing repository structure...")
        await asyncio.sleep(0.1)
        
        try:
            repo_structure = analyze_repo_structure(repo_path)
            yield create_sse_message("analyze", "Repository analysis complete.")
        except Exception as e:
            yield create_sse_message("error", f"Failed to analyze repository: {str(e)}")
            return
            
        # Plan changes using LLM
        yield create_sse_message("plan", "Planning code changes with AI...")
        await asyncio.sleep(0.1)
        
        try:
            changes_plan = await plan_changes(request.prompt, repo_structure)
            plan_summary = f"Files to edit: {len(changes_plan.get('edit', []))}, " \
                          f"Files to create: {len(changes_plan.get('create', []))}, " \
                          f"Files to delete: {len(changes_plan.get('delete', []))}"
            
            yield create_sse_message("plan", f"Planning complete: {plan_summary}")
        except Exception as e:
            yield create_sse_message("error", f"Failed to plan changes: {str(e)}")
            return
            
        # Create new branch
        try:
            git_service.create_branch(repo_path, branch_name)
            yield create_sse_message("branch", f"Created new branch: {branch_name}")
        except Exception as e:
            yield create_sse_message("error", f"Failed to create branch: {str(e)}")
            return
            
        # Apply edits to existing files
        files_modified = 0
        for file_path in changes_plan.get('edit', []):
            yield create_sse_message("edit", f"Editing file: {file_path}")
            await asyncio.sleep(0.1)
            
            try:
                full_file_path = os.path.join(repo_path, file_path)
                if os.path.exists(full_file_path):
                    await apply_edits(repo_path, file_path, request.prompt)
                    files_modified += 1
                    yield create_sse_message("edit", f"Successfully edited: {file_path}")
                else:
                    yield create_sse_message("warning", f"File not found, skipping: {file_path}")
            except Exception as e:
                yield create_sse_message("warning", f"Failed to edit {file_path}: {str(e)}")
                
        # Create new files
        for file_path in changes_plan.get('create', []):
            yield create_sse_message("create", f"Creating file: {file_path}")
            await asyncio.sleep(0.1)
            
            try:
                full_file_path = os.path.join(repo_path, file_path)
                os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
                
                # Use LLM to generate content for new file
                await apply_edits(repo_path, file_path, request.prompt, is_new_file=True)
                files_modified += 1
                yield create_sse_message("create", f"Successfully created: {file_path}")
            except Exception as e:
                yield create_sse_message("warning", f"Failed to create {file_path}: {str(e)}")
                
        # Delete files (if any)
        for file_path in changes_plan.get('delete', []):
            yield create_sse_message("delete", f"Deleting file: {file_path}")
            try:
                full_file_path = os.path.join(repo_path, file_path)
                if os.path.exists(full_file_path):
                    os.remove(full_file_path)
                    yield create_sse_message("delete", f"Successfully deleted: {file_path}")
            except Exception as e:
                yield create_sse_message("warning", f"Failed to delete {file_path}: {str(e)}")
                
        if files_modified == 0:
            yield create_sse_message("warning", "No files were modified. Check if the repository structure matches the planned changes.")
            
        # Commit and push changes
        yield create_sse_message("commit", "Committing and pushing changes...")
        await asyncio.sleep(0.1)
        
        try:
            commit_message = f"AI Agent: {request.prompt[:100]}{'...' if len(request.prompt) > 100 else ''}"
            git_service.commit_and_push(repo_path, commit_message, branch_name)
            yield create_sse_message("commit", "Changes committed and pushed successfully.")
        except Exception as e:
            yield create_sse_message("error", f"Failed to commit and push: {str(e)}")
            return
            
        # Generate PR description
        yield create_sse_message("pr", "Generating pull request description...")
        await asyncio.sleep(0.1)
        
        try:
            pr_title, pr_body = await generate_pr_description(request.prompt, changes_plan)
            yield create_sse_message("pr", "PR description generated.")
        except Exception as e:
            # Fallback to simple description
            pr_title = f"AI Agent: {request.prompt[:50]}{'...' if len(request.prompt) > 50 else ''}"
            pr_body = f"This pull request was created by an AI coding agent.\n\nPrompt: {request.prompt}\n\nChanges applied automatically based on the provided instructions."
            yield create_sse_message("warning", f"Using fallback PR description: {str(e)}")
            
        # Create pull request
        yield create_sse_message("pr", "Creating pull request...")
        await asyncio.sleep(0.1)
        
        try:
            pr_url = git_service.create_pull_request(
                str(request.repoUrl), 
                branch_name, 
                pr_title, 
                pr_body
            )
            
            result = {
                "pr_url": pr_url,
                "branch_name": branch_name,
                "files_modified": files_modified,
                "summary": f"Successfully created pull request with {files_modified} modified files."
            }
            
            yield create_sse_message("done", json.dumps(result))
            
        except Exception as e:
            yield create_sse_message("error", f"Failed to create pull request: {str(e)}")
            return
            
    except Exception as e:
        yield create_sse_message("error", f"Unexpected error: {str(e)}")
        
    finally:
        # Cleanup temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                yield create_sse_message("cleanup", "Temporary files cleaned up.")
            except Exception as e:
                yield create_sse_message("warning", f"Failed to cleanup temporary files: {str(e)}")


@router.post("/prompt_on_repo")
async def process_code_request(request: CodeRequest):
    """
    Main endpoint that processes a code request and streams the workflow progress.
    
    Returns a Server-Sent Events stream with the following event types:
    - start: Workflow initialization
    - clone: Repository cloning progress
    - analyze: Repository analysis progress
    - plan: Change planning progress
    - edit/create/delete: File modification progress
    - commit: Git operations progress
    - pr: Pull request creation progress
    - done: Final results with PR URL
    - error: Error messages
    - warning: Non-fatal warnings
    - cleanup: Cleanup operations
    """
    return StreamingResponse(
        event_generator(request),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )