import requests

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
