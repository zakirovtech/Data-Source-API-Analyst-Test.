# GitHub API Python Integration

## Repository Structure

This repository interacts with the GitHub API using Python and the `httpx` library. The main purpose of this repository is to demonstrate how to perform authenticated requests to GitHub's REST API, including retrieving repositories, commits, and file contents, while handling rate limits and other potential API constraints.
## Structure
```
/github_api_python
    /api
        ├── client.py      # Contains client configuration and authentication logic.
        ├── handlers.py    # Contains functions for interacting with the GitHub API.
        ├── settings.py    # Contains environment variable management for the GitHub API token.
        ├── .env.example   # Example .env file for setting up GitHub API token.
        ├── main.py        # The main entry point to run the application.
    /tests
        ├── test_handlers.py   # Unit tests for the handler functions.
    README.md                  # Documentation for the repository.
```


## Purpose of Each Part

### 1. `client.py`
This file contains the configuration for the HTTP client that interacts with the GitHub API. It manages authentication and authorization by handling the API token and adding necessary headers.

### 2. `handlers.py`
The core logic for interacting with GitHub's API is contained in this file. It includes the following key functions:

#### **`authenticate`**
Authenticates the user by sending a request to GitHub's `/user` endpoint.
- **Parameters:** `s` - An authenticated HTTP client.
- **Returns:** `True` if authentication is successful, otherwise `False`.

#### **`search_repos`**
Searches for repositories on GitHub based on various parameters.
- **Parameters:**
  - `session` - An authenticated HTTP client.
  - `key_word` - A string keyword to search for in repository names or descriptions (required).
  - `user` (optional) - GitHub username to filter repositories by owner.
  - `language` (optional) - Programming language to filter repositories.
  - `count_in_page` (optional) - Number of results per page (default: 100).
  - `sort` (optional) - Sort results by: `stars`, `forks`, `help-wanted-issues`, or `updated` (default: `stars`).
  - `order` (optional) - Order of results: `desc` or `asc` (default: `desc`).
  - `fork` (optional) - Filter repositories by fork status: `true`, `false`, or `only`.
- **Returns:** 
  - None (The function processes the response and extracts data).

#### **`search_commits`**
Searches for commits on GitHub based on various parameters.
- **Parameters:**
  - `session` - An authenticated HTTP client.
  - `key_word` (optional) - A string keyword to search for in commit messages (default: `Initial`).
  - `user` (optional) - GitHub username to filter commits by author or committer.
  - `author` (optional) - The author of the commit.
  - `committer` (optional) - The committer of the commit.
  - `repo` (optional) - The repository to filter commits by.
  - `count_in_page` (optional) - Number of results per page (default: 100).
  - `sort` (optional) - Sort commits by: `stars`, `forks`, `help-wanted-issues`, or `updated` (default: `stars`).
  - `order` (optional) - Order of results: `desc` or `asc` (default: `desc`).
  - `fork` (optional) - Filter commits by fork status: `true`, `only`.
- **Returns:** 
  - None (The function processes the response and extracts data).

#### **`search_contents`**
Searches for file contents in a specific repository.
- **Parameters:**
  - `session` - An authenticated HTTP client.
  - `path` - The path of the file in the repository.
  - `owner` - The owner of the repository (e.g., GitHub username or organization name).
  - `repo` - The repository name in **owner/repo** format.
- **Returns:**
  - The contents of the file, either as base64-encoded data or a link.

### 3. `settings.py`
This file manages environment variables, specifically loading the GitHub API token from a `.env` file. It allows for secure storage of the API token without hardcoding it into the source code.

### 4. `.env.example`
This is an example `.env` file that you should copy to `.env` and populate it with your GitHub API token (`GITHUB_API_TOKEN`). It is used for securely storing your GitHub API token.

### 5. `main.py`
The main entry point for the application. It sets up the HTTP client, authenticates the user, and calls the search functions for repositories, commits, and contents.

---

## API Interaction Approach

The code interacts with GitHub’s REST API to perform authenticated requests. Here's a breakdown of how the API calls are made:

1. **Authentication:**
   The `authenticate` function checks if the user is authenticated by sending a request to the GitHub API. If the authentication fails, an error message is logged. If successful, the user's login name is logged.

2. **Rate Limiting:**
   GitHub imposes a rate limit on the number of requests that can be made in a certain time window. The `check_rate_limit` function checks the current rate limits. If the remaining search requests are exhausted, the function calculates the time to wait until the rate limit is reset and sleeps for that duration.

3. **Repository Search (`search_repos`):**
   The `search_repos` function sends a search query to the GitHub API for repositories matching the given filters such as keyword, language, and fork status. It handles pagination and calls a helper function to extract the data from each page.

4. **Commit Search (`search_commits`):**
   Similar to the repository search, the `search_commits` function sends a search query to find commits that match the provided filters. It handles rate limits and retries when necessary. 

5. **Content Search (`search_contents`):**
   The `search_contents` function retrieves the content of a specific file from a repository. The file’s content is returned either as a base64-encoded string or as a link to the content.

---