import httpx

from api.client import auth_headers
from api.handlers import authenticate, search_commits, search_contents, search_repos


def main():
     with httpx.Client() as s:
        s.headers.update(auth_headers)
        
        if authenticate(s):
            search_repos(s, key_word="django-blog", language="python", fork="only", count_in_page=10)
            search_commits(s, key_word="Initial", count_in_page=10)
            search_contents(s, owner="zakirovtech", repo="zakirovtech", path="README.md")


if __name__ == "__main__":
    main()
