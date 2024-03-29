import sys
import yaml
import re
import os
from subprocess import run, PIPE
from datetime import datetime, timedelta


def main():
    # Read issue description from standard input
    issue_description = sys.stdin.read()

    # Remove all occurrences of '---'
    comment_body = re.sub(r'---', '', issue_description)

    # Parse the modified comment body as YAML content
    parsed_data = yaml.safe_load(comment_body.strip())

    # Extract project name and Jira ticket number
    project_name = parsed_data.get('project_name', '').replace(' ', '-')  # Replace spaces with hyphens
    jira_ticket_number = parsed_data.get('Jira_ticket_number', '')
    Requester_email = parsed_data.get('Requester_email', '')
    Requester = parsed_data.get('Requester', '')
    Reviewer = parsed_data.get('Reviewer', '')
    Expiry_date = parsed_data.get('expiry_date', '') 

    if not project_name:
        print("Project name not found in comment. Exiting...")
        return

    if not jira_ticket_number:
        print("Jira ticket number not found in comment. Exiting...")
        return
    
    if not Expiry_date:
        next_month_date = datetime.now() + timedelta(days=30)
        formatted_date = next_month_date.strftime("%Y-%m-%d")
        # Set Expiry_date to the formatted date
        Expiry_date = formatted_date
        print("There is no Expiry_date. Default is set to one month: ", Expiry_date)


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
    # Reset the working directory to the state of the last commit
    run(["git", "reset", "--hard"])

    # Checkout to the main branch and get the latest changes
    run(["git", "checkout", "main"])
    run(["git", "pull", "origin", "main"])
    
    run(["git", "checkout", "-b", branch_name])  # Create and checkout new branch
    run(["git", "pull", "origin", branch_name])  # pull changes if branch exist
    run(["git", "pull", "--rebase", "origin", "main"])  # Pull changes from the remote main branch

    # Check if there are any conflicts
    #conflict_check = run(["git", "status", "--porcelain"], capture_output=True, text=True)
    #if conflict_check.stdout:
    #    print("There are conflicts that need to be resolved before proceeding. Exiting...")
    #    return

        

    # Generate file path and name
    file_path = os.path.join(config_dir, f"{Expiry_date}-{project_name}.yaml")

    # Write parsed data to YAML file
    with open(file_path, 'w') as file:
        yaml.dump(parsed_data, file)
    
    run(["git", "add", file_path])
    run(["git", "commit", "-m", f"{jira_ticket_number} - Add {project_name} configuration file"])

    # Use the PAT as the authentication token
    pat = os.getenv("GH_TOKEN")
    if not pat:
        print("GitHub token not found. Exiting...")
        return

    # Push changes to the new branch
    run(["git", "push", "origin", branch_name], env={"GITHUB_TOKEN": pat})

    # Create a pull request
    pr_create_command = [
        "gh", "pr", "create",
        "--base", "main",
        "--head", branch_name,
        "--title", f"{jira_ticket_number} - Add {project_name} configuration file",
        "--body", f"request for jira ticket {jira_ticket_number} \n url: https://opsguru.atlassian.net/browse/{jira_ticket_number} \n Reviewer: {Reviewer}"
    ]
    run(pr_create_command)

if __name__ == "__main__":
    main()
