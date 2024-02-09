import requests
import sys
import yaml
import re
import os
from subprocess import run, PIPE

def main():
    comment_body = sys.argv[1]

    # Remove all occurrences of '---'
    comment_body = re.sub(r'---', '', comment_body)

    # Parse the modified comment body as YAML content
    parsed_data = yaml.safe_load(comment_body.strip())

    # Extract project name and Jira ticket number
    project_name = parsed_data.get('project_name', '').replace(' ', '-')  # Replace spaces with hyphens
    jira_ticket_number = parsed_data.get('Jira_ticket_number', '')
    Requester_email = parsed_data.get('Requester_email', '')
    Requester = parsed_data.get('Requester', '')
    Reviewer_email = parsed_data.get('Reviewer', '')

    if not project_name:
        print("Project name not found in comment. Exiting...")
        return

    if not jira_ticket_number:
        print("Jira ticket number not found in comment. Exiting...")
        return

    # Create branch name from Jira ticket number and project name
    branch_name = f"{jira_ticket_number}-{project_name.replace(' ', '-')}"

    # Create configurations directory if it doesn't exist
    config_dir = 'configurations'
    os.makedirs(config_dir, exist_ok=True)

    

    
    # Git commands to create a new branch, add, commit, and push the file
    run(["git", "config", "--global", "user.email", Requester_email])
    run(["git", "config", "--global", "user.name", Requester])
    # Enable pull rebase globally
    run(["git", "config", "--global", "pull.rebase", "true"], stdout=PIPE, stderr=PIPE)
    run(["git", "checkout", "-b", branch_name])  # Create and checkout new branch
    run(["git", "pull", "origin", branch_name])  # pull changes if branch exist
    run(["git", "pull", "--rebase", "origin", "main"])  # Pull changes from the remote main branch

    # Check if there are any conflicts
    conflict_check = run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if conflict_check.stdout:
        print("There are conflicts that need to be resolved before proceeding. Exiting...")
        return
        

    # Generate file path and name
    file_path = os.path.join(config_dir, f"{project_name}.yaml")

    # Write parsed data to YAML file
    with open(file_path, 'w') as file:
        yaml.dump(parsed_data, file)
    
    run(["git", "add", file_path])
    run(["git", "commit", "-m", f"{jira_ticket_number} - Add {project_name} configuration file"])

    # Use the PAT as the authentication token
    pat = os.getenv("GH_TOKEN")

    # Push changes to the new branch
    run(["git", "push", "origin", branch_name], env={"GITHUB_TOKEN": pat})

    ############### Find GIT USER ##############
def get_github_username_from_email(email):
    # GitHub API endpoint for searching users
    search_users_url = "https://api.github.com/search/users"

    # Parameters for the search query
    params = {"q": email}

    # Request to search for users with the given email
    response = requests.get(search_users_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()

        # Check if any users were found
        if response_json["total_count"] > 0:
            # Get the username of the first user found
            return response_json["items"][0]["login"]
        else:
            print("No GitHub user found with the provided email.")
    else:
        print("Failed to fetch GitHub user information.")

    github_username = get_github_username_from_email(Reviewer_email)
    ############################################

    # Create a pull request
    pr_create_command = [
        "gh", "pr", "create",
        "--base", "main",
        "--head", branch_name,
        "--title", f"{jira_ticket_number} - Add {project_name} configuration file",
        "--body", f"request for jira ticket {jira_ticket_number} \n url: https://opsguru.atlassian.net/browse/{jira_ticket_number}",
        "--reviewer", github_username  
    ]
    run(pr_create_command)

if __name__ == "__main__":
    main()
