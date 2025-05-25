import requests
import os
import requests


def search_commons_images(queries, max_images=5):
    search_url = "https://commons.wikimedia.org/w/api.php"
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".tif", ".tiff")

    collected = []

    for query in queries:
        if len(collected) >= max_images:
            break

        # Step 1: Search
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srnamespace": 6,
            "srlimit": 10,
        }

        response = requests.get(search_url, params=search_params)
        results = response.json().get("query", {}).get("search", [])
        titles = [f"File:{r['title']}" for r in results]

        if not titles:
            continue

        # Step 2: Get URLs
        info_params = {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "iiprop": "url",
            "titles": "|".join(titles),
        }

        info_response = requests.get(search_url, params=info_params)
        pages = info_response.json().get("query", {}).get("pages", {})
        for page in pages.values():
            title = page.get("title", "").lower()

            if title.endswith(image_extensions):
                collected.append(page["title"])

                if len(collected) >= max_images:
                    break

    return collected


def get_commons_file_metadata(file_titles):
    """
    Given a list of Wikimedia Commons file titles (e.g., "File:Example.jpg"),
    returns metadata, description, and content for each file.
    """
    base_url = "https://commons.wikimedia.org/w/api.php"
    results = []

    # API requires titles joined by "|"
    title_str = "|".join(file_titles)

    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo|description|info",
        "iiprop": "url|extmetadata",
        "inprop": "url",
        "titles": title_str
    }

    response = requests.get(base_url, params=params)
    pages = response.json().get("query", {}).get("pages", {})

    for page_id, page in pages.items():
        file_info = {
            "title": page.get("title"),
            "description_url": page.get("fullurl"),
            "image_url": None,
            "extmetadata": {},
        }

        # Image info (URL, metadata)
        imageinfo = page.get("imageinfo", [])
        if imageinfo:
            imageinfo = imageinfo[0]
            file_info["image_url"] = imageinfo.get("url", "")
            file_info["extmetadata"] = imageinfo.get("extmetadata", {})

        results.append(file_info)

    return results


def download_commons_image(image_url, save_dir="downloads", filename=None):
    os.makedirs(save_dir, exist_ok=True)
    if not filename:
        filename = os.path.basename(image_url.split("?")[0])
    path = os.path.join(save_dir, filename)

    headers = {
        "User-Agent": "WikiMediaImageDownloader/1.0 (contact@example.com)"
    }

    response = requests.get(image_url, stream=True, headers=headers)
    response.raise_for_status()

    with open(path, "wb") as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)

    print(f"Image saved to {path}")
    return path


def query_and_download_images(queries: list[str]) -> list[str]:
    image_urls = search_commons_images(
        queries=queries,
        max_images=10)
    parsed_image_urls = []
    for image_url in image_urls:
        image_url = image_url.replace("File:File", "File")
        parsed_image_urls.append(image_url)

    file_metadatas = get_commons_file_metadata(parsed_image_urls)
    paths = []
    for url in file_metadatas:
        paths.append(download_commons_image(url["image_url"]))
    return paths
