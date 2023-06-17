import requests
import openai
import re

openai.api_key = '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'
token = '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'

# GitHub API headers
headers = {
    'Authorization': f'Token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Fetch user repositories from GitHub
def get_user_repositories(user):
    url = f'https://api.github.com/users/{user}/repos'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch repositories. Status code: {response.status_code}")
        return None

# Preprocess code from repository
def preprocess_code(code):
    # Remove comments
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

    # Remove leading and trailing whitespace
    code = code.strip()

    # Tokenization (split by whitespace)
    tokens = code.split()

    # Normalize tokens to lowercase
    tokens = [token.lower() for token in tokens]

    # Join tokens back into code string
    preprocessed_code = ' '.join(tokens)

    return preprocessed_code

# Generate complexity evaluation using GPT model
def generate_complexity_evaluation(prompt):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt[:4000],  # Limit the prompt length to 4000 tokens
        max_tokens=100
    )

    return response.choices[0].text.strip()

# Calculate complexity score
def calculate_complexity_score(complexity_evaluation):
    # Implement your complexity score calculation logic here
    # Return the complexity score

    # Example implementation: Calculate score based on keywords
    score = 0
    if 'complex' in complexity_evaluation.lower():
        score += 1
    if 'difficult' in complexity_evaluation.lower():
        score += 1
    return score

# Main program
def main():
    # Input GitHub user URL
    github_user_url = input("Enter the GitHub user URL: ")
    username = github_user_url.split('/')[-1]

    # Fetch user repositories from GitHub
    repositories = get_user_repositories(username)
    if repositories is not None:
        complexity_scores = []
        for repo in repositories:
            repo_name = repo['name']
            print(f"Repository: {repo_name}")

            # Fetch code from repository
            code_url = repo['url'] + '/contents'
            response = requests.get(code_url, headers=headers)
            if response.status_code == 200:
                code_files = response.json()
                code = ''
                for file in code_files:
                    if file['type'] == 'file':
                        file_response = requests.get(file['download_url'], headers=headers)
                        code += file_response.text
                preprocessed_code = preprocess_code(code)

                # Generate complexity evaluation using GPT model
                prompt = f"Evaluate the technical complexity of the code in the repository '{repo_name}':\n{preprocessed_code}\n"
                complexity_evaluation = generate_complexity_evaluation(prompt)

                # Calculate complexity score
                complexity_score = calculate_complexity_score(complexity_evaluation)
                complexity_scores.append((repo_name, complexity_score))
                print(f"Complexity Score: {complexity_score}\n")

        # Sort repositories by complexity score
        complexity_scores.sort(key=lambda x: x[1], reverse=True)

        if complexity_scores:
            most_complex_repo = complexity_scores[0][0]
            print(f"The most technically complex repository is: {most_complex_repo}")
        else:
            print("No repositories found.")

if __name__ == '__main__':
    main()
