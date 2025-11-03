from typing import Optional
from bs4 import BeautifulSoup

from fkstream.utils.common_logger import logger
from fkstream.utils.database import get_custom_source_from_cache, save_custom_source_to_cache


async def scrape_videas_url(http_client, page_url: str) -> Optional[str]:
    """Scrape une page videas pour extraire le lien direct."""
    try:
        cached_url = await get_custom_source_from_cache(page_url)
        if cached_url:
            logger.log("FKSTREAM", f"URL custom depuis le cache: {page_url}")
            return cached_url

        logger.log("FKSTREAM", f"Scraping de l'URL custom: {page_url}")

        response = await http_client.get(page_url)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        articles = soup.find_all('article', class_='media')

        for article in articles:
            strong_tag = article.find('strong')
            if strong_tag and strong_tag.get_text(strip=True) == 'Source':
                media_right = article.find('div', class_='media-right')
                if media_right:
                    link = media_right.find('a', href=True)
                    if link:
                        direct_url = link['href']

                        await save_custom_source_to_cache(page_url, direct_url)

                        logger.log("FKSTREAM", f"URL directe extraite et mise en cache: {page_url}")
                        return direct_url

        logger.warning(f"Aucun lien 'Source' trouve dans {page_url}")
        return None

    except Exception as e:
        logger.error(f"Erreur lors du scraping de {page_url}: {e}")
        return None
