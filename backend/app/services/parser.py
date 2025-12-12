import asyncio
import random
import logging
from typing import Set, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import urllib.parse

from playwright.async_api import async_playwright, Page, BrowserContext

# ================ CONFIG ================
logging.basicConfig(
    filename="parser.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)

# User-Agent pool для ротации
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

# Чёрный список доменов (перекупщики, маркетплейсы, не B2B)
BLACKLIST_DOMAINS = {
    "avito.ru",
    "ozon.ru",
    "wildberries.ru",
    "youla.ru",
    "lamoda.ru",
    "ebay.com",
    "aliexpress.com",
    "yandex.ru",
    "google.com",
    "2gis.ru",
    "dzen.ru",
    "vk.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "pinterest.com",
    "reddit.com",
    "wikipedia.org",
    "twitter.com",
    "tiktok.com",
}

BLACKLIST_KEYWORDS = [
    "forum",
    "blog",
    "wiki",
    "stackoverflow",
    "habr.com",
    "pikabu.ru",
    "livejournal",
]

REDIRECTS_TO_CLEAN = {
    "yandex.ru/clck/",
    "safebrowsing",
}

# ================ HELPERS ================

def is_blacklisted(url: str) -> bool:
    """Проверяем, не в чёрном списке ли домен"""
    domain = urlparse(url).netloc.lower()
    url_lower = url.lower()
    
    # Проверка доменов
    for bl in BLACKLIST_DOMAINS:
        if bl in domain:
            return True
    
    # Проверка ключевых слов
    for kw in BLACKLIST_KEYWORDS:
        if kw in url_lower:
            return True
    
    return False


def is_redirect_link(url: str) -> bool:
    """Проверяем, не редирект ли ссылка"""
    for redir in REDIRECTS_TO_CLEAN:
        if redir in url:
            return True
    return False


def clean_url(url: str) -> Optional[str]:
    """Очищаем URL от параметров и проверяем валидность"""
    if not url:
        return None
    
    # Отбрасываем редиректы
    if is_redirect_link(url):
        return None
    
    # Отбрасываем чёрный список
    if is_blacklisted(url):
        logging.info(f"Исключён из чёрного списка: {url}")
        return None
    
    # Убираем параметры (?xxx&xxx)
    clean = url.split("?")[0].split("#")[0]
    
    # Убираем протокол для дедупликации (https и http одно и то же)
    if clean.startswith("https://"):
        clean = clean.replace("https://", "http://")
    
    return clean if clean.startswith("http") else None


async def human_pause(min_sec: float = 2.0, max_sec: float = 6.0):
    """Пауза с рандомизацией (увеличена для человеческого поведения)"""
    wait_time = random.uniform(min_sec, max_sec)
    await asyncio.sleep(wait_time)


async def human_scroll(page: Page):
    """Более натуральный скроллинг"""
    for _ in range(random.randint(2, 4)):
        direction = random.choice([200, -300, 150])
        await page.mouse.wheel(0, random.randint(direction - 50, direction + 50))
        await human_pause(0.3, 0.8)


async def human_mouse_movement(page: Page):
    """Движения мыши по странице"""
    for _ in range(random.randint(3, 7)):
        x = random.randint(100, 900)
        y = random.randint(100, 700)
        await page.mouse.move(x, y, steps=random.randint(5, 15))
        await human_pause(0.1, 0.4)


async def very_human_behavior(page: Page):
    """Комплексное человеческое поведение"""
    await human_pause(1.5, 3.5)
    await human_mouse_movement(page)
    await human_pause(0.8, 2.0)
    await human_scroll(page)
    await human_pause(1.5, 4.0)


async def detect_captcha(page: Page, engine_name: str) -> bool:
    """Умная детекция капчи (не только по URL)"""
    url = page.url.lower()
    
    # 1) Проверка URL
    if "captcha" in url or "showcaptcha" in url or "recaptcha" in url:
        logging.warning(f"{engine_name}: Капча (по URL)")
        return True
    
    # 2) Проверка по видимому тексту
    try:
        captcha_text = await page.locator("text=/капча|подтвердите|проверка/i").count()
        if captcha_text > 0:
            logging.warning(f"{engine_name}: Капча (по тексту)")
            return True
    except:
        pass
    
    # 3) Проверка Яндекса: если нет результатов = может быть капча
    if engine_name == "YANDEX":
        try:
            results = await page.locator("li.serp-item").count()
            if results == 0:
                logging.warning(f"{engine_name}: Нет результатов (капча?)")
                return True
        except:
            pass
    
    # 4) Проверка Google: если нет элементов = может быть капча
    if engine_name == "GOOGLE":
        try:
            results = await page.locator("div.g").count()
            if results == 0:
                logging.warning(f"{engine_name}: Нет результатов (капча?)")
                return True
        except:
            pass
    
    return False


async def wait_for_page_load(page: Page, timeout: int = 15):
    """Ждём полной загрузки страницы"""
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout * 1000)
    except:
        logging.warning(f"Page load timeout ({timeout}s), continuing anyway...")


# ================ PARSERS ================

async def parse_yandex(
    page: Page,
    query: str,
    pages: int,
    collected_links: Set[str],
    max_retries: int = 3,
):
    """Парсинг Яндекса с умной обработкой капчи"""
    
    query_encoded = urllib.parse.quote(query)
    base_url = f"https://yandex.ru/search/?text={query_encoded}"
    
    for attempt in range(max_retries):
        try:
            logging.info(f"YANDEX: Попытка {attempt + 1}/{max_retries}")
            await page.goto(base_url, wait_until="domcontentloaded")
            await wait_for_page_load(page)
            
            if await detect_captcha(page, "YANDEX"):
                if attempt < max_retries - 1:
                    logging.info("YANDEX: Ждём 30 сек перед повтором...")
                    await human_pause(25, 35)
                    continue
                else:
                    logging.error("YANDEX: Капча не пройдена, пропускаем")
                    return
            
            # Успешно зашли
            break
        except Exception as e:
            logging.error(f"YANDEX: Ошибка загрузки - {e}")
            if attempt < max_retries - 1:
                await human_pause(10, 15)
            else:
                return
    
    # Парсим страницы
    for page_num in range(1, pages + 1):
        try:
            logging.info(f"YANDEX: Страница {page_num}")
            print(f"🔍 Яндекс: страница {page_num}")
            
            await very_human_behavior(page)
            
            # Проверяем капчу
            if await detect_captcha(page, "YANDEX"):
                logging.warning("YANDEX: Капча на странице, выходим")
                break
            
            # Парсим ссылки (несколько селекторов для надёжности)
            selectors = [
                "a.Link",
                "a.Link-Item",
                "h2 a",
            ]
            
            links_on_page = set()
            for selector in selectors:
                try:
                    elems = page.locator(selector)
                    count = await elems.count()
                    
                    for i in range(count):
                        try:
                            href = await elems.nth(i).get_attribute("href")
                            cleaned = clean_url(href)
                            if cleaned:
                                links_on_page.add(cleaned)
                        except:
                            pass
                except:
                    pass
            
            collected_links.update(links_on_page)
            logging.info(f"YANDEX: Найдено {len(links_on_page)} ссылок на странице {page_num}")
            
            # Переход на следующую
            if page_num < pages:
                try:
                    next_btn = page.locator("a[aria-label='Следующая страница']")
                    if await next_btn.count() > 0:
                        await human_pause(4, 10)
                        await next_btn.click()
                        await wait_for_page_load(page)
                    else:
                        logging.info("YANDEX: Нет кнопки 'Далее', выходим")
                        break
                except Exception as e:
                    logging.error(f"YANDEX: Ошибка клика - {e}")
                    break
        
        except Exception as e:
            logging.error(f"YANDEX: Ошибка парсинга страницы {page_num} - {e}")
            continue
    
    logging.info(f"YANDEX: Итого {len(collected_links)} уникальных ссылок")


async def parse_google(
    page: Page,
    query: str,
    pages: int,
    collected_links: Set[str],
    max_retries: int = 3,
):
    """Парсинг Google с умной обработкой капчи"""
    
    query_encoded = urllib.parse.quote(query)
    base_url = f"https://www.google.com/search?q={query_encoded}&hl=ru&gl=ru"
    
    for attempt in range(max_retries):
        try:
            logging.info(f"GOOGLE: Попытка {attempt + 1}/{max_retries}")
            await page.goto(base_url, wait_until="domcontentloaded")
            await wait_for_page_load(page)
            
            if await detect_captcha(page, "GOOGLE"):
                if attempt < max_retries - 1:
                    logging.info("GOOGLE: Ждём 30 сек перед повтором...")
                    await human_pause(25, 35)
                    continue
                else:
                    logging.error("GOOGLE: Капча не пройдена, пропускаем")
                    return
            
            break
        except Exception as e:
            logging.error(f"GOOGLE: Ошибка загрузки - {e}")
            if attempt < max_retries - 1:
                await human_pause(10, 15)
            else:
                return
    
    # Парсим страницы
    for page_num in range(1, pages + 1):
        try:
            logging.info(f"GOOGLE: Страница {page_num}")
            print(f"🔍 Google: страница {page_num}")
            
            await very_human_behavior(page)
            
            if await detect_captcha(page, "GOOGLE"):
                logging.warning("GOOGLE: Капча на странице, выходим")
                break
            
            # Парсим ссылки
            selectors = [
                "a[data-sokoban-click]",
                "div.g a",
                "h3 a",
            ]
            
            links_on_page = set()
            for selector in selectors:
                try:
                    elems = page.locator(selector)
                    count = await elems.count()
                    
                    for i in range(count):
                        try:
                            href = await elems.nth(i).get_attribute("href")
                            # Google может вернуть /url?q=... параметр
                            if "/url?q=" in str(href):
                                href = str(href).split("/url?q=")[1].split("&")[0]
                            
                            cleaned = clean_url(href)
                            if cleaned:
                                links_on_page.add(cleaned)
                        except:
                            pass
                except:
                    pass
            
            collected_links.update(links_on_page)
            logging.info(f"GOOGLE: Найдено {len(links_on_page)} ссылок на странице {page_num}")
            
            # Переход на следующую
            if page_num < pages:
                try:
                    next_btn = page.locator("a#pnnext")
                    if await next_btn.count() > 0:
                        await human_pause(4, 10)
                        await next_btn.click()
                        await wait_for_page_load(page)
                    else:
                        logging.info("GOOGLE: Нет кнопки 'Далее', выходим")
                        break
                except Exception as e:
                    logging.error(f"GOOGLE: Ошибка клика - {e}")
                    break
        
        except Exception as e:
            logging.error(f"GOOGLE: Ошибка парсинга страницы {page_num} - {e}")
            continue
    
    logging.info(f"GOOGLE: Итого {len(collected_links)} уникальных ссылок")


# ================ MAIN ================

async def search_suppliers(
    query: str,
    pages: int = 3,
    use_proxy: Optional[str] = None,
) -> Set[str]:
    """
    Основная функция парсинга (для FastAPI integration)
    
    Args:
        query: Поисковый запрос (напр. "Труба ПНД купить")
        pages: Кол-во страниц (default 3)
        use_proxy: Optional proxy (http://proxy:port)
    
    Returns:
        Set уникальных очищенных URL
    """
    
    collected_links = set()
    
    async with async_playwright() as p:
        try:
            # Запуск браузера (может быть с прокси)
            launch_args = {}
            if use_proxy:
                launch_args["proxy"] = {"server": use_proxy}
            
            browser = await p.chromium.launch(**launch_args)
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
            )
            
            y_page = await context.new_page()
            g_page = await context.new_page()
            
            # Параллельный парсинг
            await asyncio.gather(
                parse_yandex(y_page, query, pages, collected_links),
                parse_google(g_page, query, pages, collected_links),
            )
            
            await browser.close()
        
        except Exception as e:
            logging.error(f"Критическая ошибка: {e}")
    
    logging.info(f"✅ Финал: {len(collected_links)} уникальных ссылок")
    return collected_links


async def main():
    """Для тестирования скрипта из консоли"""
    query = input("Введи поисковый запрос (напр. 'Труба ПНД купить'): ").strip()
    pages = int(input("Глубина поиска (страницы, default 3): ") or "3")
    
    print(f"\n🚀 Начинаю парсинг: '{query}' ({pages} страниц)...\n")
    
    results = await search_suppliers(query, pages)
    
    print(f"\n✅ Найдено {len(results)} ссылок:\n")
    for url in sorted(results):
        print(url)


if __name__ == "__main__":
    asyncio.run(main())
