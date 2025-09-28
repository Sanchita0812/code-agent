"""
Git and GitHub API service for repository operations.
"""
import os
import subprocess
from typing import Optional
from urllib.parse import urlparse

from git import Repo
from github import Github, GithubException


class GitService:
    """Service class for handling Git and GitHub operations."""
    
    def __init__(self, github_token: str):
        """Initialize the GitService with a GitHub token."""
        self.github_token = github_token
        self.github_client = Github(github_token)
    
    def clone_repo(self, repo_url: str, local_path: str) -> None:
        """
        Clone a public GitHub repository to a local directory.
        
        Args:
            repo_url: The GitHub repository URL
            local_path: Local directory path where repo will be cloned
            
        Raises:
            Exception: If cloning fails
        """
        try:
            # Ensure the parent directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Clone the repository with authentication
            if repo_url.startswith('https://github.com/'):
                # Inject token for authentication
                parsed_url = urlparse(repo_url)
                authenticated_url = f"https://{self.github_token}@{parsed_url.netloc}{parsed_url.path}"
                Repo.clone_from(authenticated_url, local_path)
            else:
                Repo.clone_from(repo_url, local_path)
            
        except Exception as e:
            raise Exception(f"Failed to clone repository {repo_url}: {str(e)}")
    
    def create_branch(self, repo_path: str, branch_name: str) -> None:
        """
        Create and checkout a new branch in the local repository.
        
        Args:
            repo_path: Path to the local repository
            branch_name: Name of the new branch to create
            
        Raises:
            Exception: If branch creation fails
        """
        try:
            repo = Repo(repo_path)
            
            # Create new branch from current HEAD
            new_branch = repo.create_head(branch_name)
            
            # Checkout the new branch
            new_branch.checkout()
            
        except Exception as e:
            raise Exception(f"Failed to create branch {branch_name}: {str(e)}")
    
    def commit_and_push(self, repo_path: str, commit_message: str, branch_name: str) -> None:
        """
        Stage all changes, commit them, and push the branch to origin.
        
        Args:
            repo_path: Path to the local repository
            commit_message: Commit message
            branch_name: Name of the branch to push
            
        Raises:
            Exception: If commit or push fails
        """
        try:
            repo = Repo(repo_path)
            
            # Configure git user (required for commits)
            with repo.config_writer() as config:
                config.set_value("user", "name", "AI Coding Agent")
                config.set_value("user", "email", "ai-agent@backspace.dev")
            
            # Stage all changes
            repo.git.add(A=True)
            
            # Check if there are any changes to commit
            if not repo.is_dirty(untracked_files=True):
                raise Exception("No changes to commit")
            
            # Commit changes
            repo.index.commit(commit_message)
            
            # Set up authentication for push - fix the URL format
            origin_url = repo.remotes.origin.url
            
            # Ensure we have the correct authenticated URL format
            if origin_url.startswith('https://'):
                parsed_url = urlparse(origin_url)
                # Remove any existing token from URL first
                clean_netloc = parsed_url.netloc.split('@')[-1]
                authenticated_url = f"https://{self.github_token}@{clean_netloc}{parsed_url.path}"
                
                # Update the remote URL
                repo.remotes.origin.set_url(authenticated_url)
                
                # Push the branch with explicit remote and branch
                try:
                    repo.git.push('origin', branch_name, '--set-upstream')
                except Exception as push_error:
                    # Fallback: try force push if branch exists
                    try:
                        repo.git.push('origin', branch_name, '--force')
                    except Exception:
                        raise Exception(f"Failed to push branch {branch_name}: {str(push_error)}")
            else:
                # For SSH URLs, assume key-based auth is configured
                repo.git.push('origin', branch_name, '--set-upstream')
            
        except Exception as e:
            raise Exception(f"Failed to commit and push changes: {str(e)}")
    
    def create_pull_request(self, repo_url: str, branch_name: str, title: str, body: str) -> str:
        """
        Create a pull request on GitHub.
        
        Args:
            repo_url: The GitHub repository URL
            branch_name: Name of the branch containing changes
            title: PR title
            body: PR description
            
        Returns:
            URL of the created pull request
            
        Raises:
            Exception: If PR creation fails
        """
        try:
            # Parse repository owner and name from URL
            parsed_url = urlparse(repo_url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                raise Exception("Invalid repository URL format")
            
            owner = path_parts[0]
            repo_name = path_parts[1].replace('.git', '')
            
            # Get the repository object
            repo = self.github_client.get_repo(f"{owner}/{repo_name}")
            
            # Get the default branch
            default_branch = repo.default_branch
            
            # Check if branch exists on remote
            try:
                repo.get_branch(branch_name)
            except Exception:
                raise Exception(f"Branch {branch_name} not found on remote. Make sure push was successful.")
            
            # Create the pull request
            pr = repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=default_branch
            )
            
            return pr.html_url
            
        except GithubException as e:
            if e.status == 422 and "pull request already exists" in str(e.data):
                # Try to find existing PR
                try:
                    repo = self.github_client.get_repo(f"{owner}/{repo_name}")
                    pulls = repo.get_pulls(head=f"{owner}:{branch_name}", state='open')
                    for pr in pulls:
                        return pr.html_url
                except:
                    pass
            raise Exception(f"GitHub API error: {str(e)}")
            
        except Exception as e:
            raise Exception(f"Failed to create pull request: {str(e)}")
    
    def get_repo_info(self, repo_url: str) -> dict:
        """
        Get basic information about a GitHub repository.
        
        Args:
            repo_url: The GitHub repository URL
            
        Returns:
            Dictionary containing repo information
        """
        try:
            parsed_url = urlparse(repo_url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                raise Exception("Invalid repository URL format")
            
            owner = path_parts[0]
            repo_name = path_parts[1].replace('.git', '')
            
            repo = self.github_client.get_repo(f"{owner}/{repo_name}")
            
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "default_branch": repo.default_branch,
                "private": repo.private
            }
            
        except Exception as e:
            raise Exception(f"Failed to get repository info: {str(e)}")