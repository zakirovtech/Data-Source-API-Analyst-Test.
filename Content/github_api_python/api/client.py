from api import settings

auth_headers = {
    "Authorization": f"Bearer {settings.API_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}
