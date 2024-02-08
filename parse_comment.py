import sys
import yaml
import re
import os
from subprocess import run

def main():
    comment_body = sys.argv[1]

    # Remove all occurrences of '---'
    comment_body = re.sub(r'---', '', comment_body)

    # Parse the modified comment body as YAML content
    parsed_data = yaml.safe_load(comment_body.strip())

    # Extract project name and Jira ticket number
    project_name = parsed_data.get('project_name', '').replace(' ', '-')  # Replace spaces with hyphens
    jira_ticket_number = parsed_data.get('Jira_ticket_number', '')

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

    # Generate file path and name
    file_path = os.path.join(config_dir, f"{project_name}.yaml")

    # Write parsed data to YAML file
    with open(file_path, 'w') as file:
        yaml.dump(parsed_data, file)

    
    # Git commands to create a new branch, add, commit, and push the file
    run(["git", "config", "--global", "user.email", "automation@gmail.com"])
    run(["git", "config", "--global", "user.name", "Automation"])
    run(["git", "checkout", "-b", branch_name])  # Create and checkout new branch
    run(["git", "add", file_path])
    run(["git", "commit", "-m", f"Add {project_name} configuration file"])

    # Use the PAT as the authentication token
    pat = os.getenv("ACCESS_TOKEN")
    if not pat:
        print("ACCESS_TOKEN secret not found. Exiting...")
        return

    # Push changes to the new branch
    run(["git", "push", "origin", branch_name], env={"GITHUB_TOKEN": pat})

    # Create a pull request
    run(["gh", "pr", "create", "--base", "main", "--head", branch_name, "--title", f"Add {project_name} configuration file - Jira: {jira_ticket_number}"])

if __name__ == "__main__":
    main()
