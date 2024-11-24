import logging
import time
import typing

import httpx

logger = logging.getLogger("streamLogger")


def authenticate(s: httpx.Client) -> bool:
    r = s.get(f"https://api.github.com/user")
    
    if r.status_code != 200:
        logger.info(f"Failed request with code: [{r.status_code}]. Response: [{r.text}]")
        return False
    
    logger.info(f"Successly auth. Your account: [{r.json()["login"]}]")
    return True


def check_rate_limit(s: httpx.Client, retries: int = 2) -> int:
    """Check rate limits"""
    for _ in range(retries):
        try:
            response = s.get("https://api.github.com/rate_limit")
        except Exception as e:
            logger.info(f"Failed with error: [{e}]")
            time.sleep(5)
        else:
            if response.status_code == 200:
                data = response.json()

                remaining = data["resources"]["search"]["remaining"]
                reset_time = data["resources"]["search"]["reset"]
                
                if remaining == 0:
                    wait_time = reset_time - int(time.time()) + 1  
                    logger.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
                    return wait_time
                else:
                    logger.info(f"Remaining search requests: {remaining}")
                    return 0

    logger.info(f"Cannot check rate limits {retries} times")
    return 0


def search_repos(
        session: httpx.Client,
        key_word: str,
        user: typing.Union[str, None] = None,
        language: typing.Union[str, None] = None,
        count_in_page: int = 100,
        sort: typing.Literal["stars", "forks", "help-wanted-issues", "updated"] = "stars",
        order: typing.Literal["desc", "asc"] = "asc",
        fork: typing.Literal["true", "false"] = "false"
        ) -> None:

    q = key_word

    # Filtering
    if user:
        q = q + f"+user:{user}"
    if language:
        q = q + f"+language:{language}"
    if fork:
        q = q + f"+fork:{fork}"
    
    # . . .

    info_url = f"https://api.github.com/search/repositories?q={q}+is:public&sort={sort}&order={order}&per_page={count_in_page}"
    pagination_urls = create_pages_urls(session, info_url, per_page=count_in_page)
    
    for url in pagination_urls:
        code = extract_data(session, url)

        if code:
            logger.error(f"Exit from search function with code: [{code}]. Check logs.")
            return None


def search_commits(
        session: httpx.Client,
        key_word: str = "Initial",
        user: typing.Union[str, None] = None,
        author: typing.Union[str, None] = None,
        committer: typing.Union[str, None] = None,
        repo: typing.Union[str, None] = None,
        count_in_page: int = 100,
        sort: typing.Literal["stars", "forks", "help-wanted-issues", "updated"] = "stars",
        order: typing.Literal["desc", "asc"] = "asc",
        fork: typing.Literal["true", "only"] = None
    ):
    
    q = key_word

    # Filtering
    if user:
        q = q + f"+user:{user}"
    if repo:
        q = q + f"+repo:{repo}"
    if author:
        q = q + f"+author:{author}"
    if committer:
        q = q + f"+committer:{committer}"
    if fork:
        q = q + f"+fork:{fork}"
    
    # . . .

    info_url = f"https://api.github.com/search/commits?q={q}&sort={sort}&order={order}&per_page={count_in_page}"
    pagination_urls = create_pages_urls(session, info_url, per_page=count_in_page)

    for url in pagination_urls:
        code = extract_data(session, url)
        time.sleep(5)  # Escaping secondary rate limit constraint
        if code:
            logger.error(f"Exit from search function with code: [{code}]. Check logs.")
            return None


def search_contents(
        session: httpx.Client,
        path: str,
        owner: str,
        repo: str 
    ):
    """Search and return content (base64 or link) in specified respository by path"""

    base_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    extract_data(session, url=base_url)


def extract_data(s: httpx.AsyncClient, url: str) -> typing.Union[None, int]:
    try:
        wait_time = check_rate_limit(s)
        
        if wait_time:
            time.sleep(wait_time)

        response = s.get(url)
        response.raise_for_status() 
    except httpx.HTTPStatusError as status_e:
        check_status(status_e.response.status_code)
        logger.error(f"Failed request response: {status_e.response.text}")
        return status_e.response.status_code
    else:
        logger.info(f"Extract data from url: {url}")
        data = response.json()
        
        logger.info(f"Data: {data}") # Print response samples for validation


def create_pages_urls(s: httpx.Client, url: str, per_page: int) -> typing.List:
    try:
        response = s.get(url)
        response.raise_for_status()
    except httpx.HTTPStatusError as status_e:
        check_status(status_e.response.status_code)
        logger.error(f"Failed request response: {status_e.response.text}")
        return []
    else:
        urls = []

        items_count = int(response.json().get("total_count"))
        pages_count = int(items_count / per_page) + 1

        logger.info(f"This search operation has {pages_count} pages")
        
        for i in range(1, pages_count + 1):
            item = url + f"&page={i}"
            urls.append(item)
    
        return urls


def check_status(status: int):
    if status == 401:
        logger.error("Authorization failed. Check your access token.")
    elif status == 403:
        logger.error("Forbidden access. You may not have permission to access this resource. Check your token access scopes.")
    elif status == 422:
         logger.warning("Only the first 1000 search results are available in GITHUB API")
    elif status == 500:
        logger.error("Internal server error. Try again later.")
    else:
        logger.error(f"Somethig is going wrong with code: [{status}]")
