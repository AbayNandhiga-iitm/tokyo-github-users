import requests
import csv
import time

# GitHub API token (replace with your actual token)
token = "Confidential"
headers = {'Authorization': f'token {token}'}
users = []
repositories = []

# Step 1: Fetch users in Tokyo with more than 200 followers
user_search_url = "https://api.github.com/search/users"
user_params = {
    'q': 'location:Tokyo followers:>200',
    'per_page': 100,
    'page': 1
}

# Fetch users with pagination
while True:
    response = requests.get(user_search_url, headers=headers, params=user_params)
    
    if response.status_code == 403:
        print("Rate limit reached, sleeping for 60 seconds...")
        time.sleep(60)
        continue  # Retry the same request after sleep
    
    elif response.status_code != 200:
        print(f"Error fetching users: {response.status_code}, {response.text}")
        break
    
    users_data = response.json().get('items', [])
    if not users_data:
        print("No more users found.")
        break
    
    for user in users_data:
        # Fetch each user's details
        user_details = requests.get(f"https://api.github.com/users/{user['login']}", headers=headers).json()
        
        # Clean up company names
        company_name = (user_details.get('company', '') or '').lstrip('@').strip().upper()
        
        # Add user to users list
        user_row = {
            'login': user_details['login'],
            'name': user_details.get('name', ''),
            'company': company_name,
            'location': user_details.get('location', ''),
            'email': user_details.get('email', ''),
            'hireable': user_details.get('hireable', ''),
            'bio': user_details.get('bio', ''),
            'public_repos': user_details.get('public_repos', 0),
            'followers': user_details['followers'],
            'following': user_details['following'],
            'created_at': user_details['created_at']
        }
        users.append(user_row)

        # Step 2: Fetch repositories for each user
        repos_url = f"https://api.github.com/users/{user['login']}/repos"
        repo_response = requests.get(repos_url, headers=headers, params={'per_page': 500, 'sort': 'pushed'}).json()
        
        if isinstance(repo_response, dict) and repo_response.get('message'):
            print(f"Error fetching repositories for {user['login']}: {repo_response['message']}")
            continue
        
        for repo in repo_response:
            repo_row = {
                'login': user['login'],
                'full_name': repo['full_name'],
                'created_at': repo['created_at'],
                'stargazers_count': repo['stargazers_count'],
                'watchers_count': repo['watchers_count'],
                'language': repo.get('language', ''),
                'has_projects': repo['has_projects'],
                'has_wiki': repo['has_wiki'],
                'license_name': repo['license']['key'] if repo['license'] else ''
            }
            repositories.append(repo_row)
    
    # Proceed to the next page of users
    user_params['page'] += 1
    time.sleep(1)  # Avoid hitting rate limits

# Step 3: Save user data to users.csv if there is data
if users:
    with open('users.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
    print("Saved users.csv")

# Step 4: Save repository data to repositories.csv if there is data
if repositories:
    with open('repositories.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=repositories[0].keys())
        writer.writeheader()
        writer.writerows(repositories)
    print("Saved repositories.csv")
else:
    print("No repository data to save.")

