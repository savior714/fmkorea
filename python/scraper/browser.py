"""
FM Korea 스크래퍼 - Playwright 브라우저 설정
Cloudflare 우회를 위한 스텔스 모드 적용
"""

import asyncio
import random
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


async def create_stealth_browser(headless: bool = False) -> Browser:
    """
    스텔스 모드가 적용된 Playwright 브라우저 생성
    
    Args:
        headless: 헤드리스 모드 여부 (기본값: False - GUI 모드)
    
    Returns:
        Browser 인스턴스
    """
    p = await async_playwright().start()
    
    browser = await p.chromium.launch(
        headless=headless,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
        ]
    )
    
    return browser


async def create_context(browser: Browser) -> BrowserContext:
    """
    실제 사용자처럼 보이는 브라우저 컨텍스트 생성
    
    Args:
        browser: Browser 인스턴스
    
    Returns:
        BrowserContext 인스턴스
    """
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={'width': 1920, 'height': 1080'},
        locale='ko-KR',
        timezone_id='Asia/Seoul',
    )
    
    # navigator.webdriver 제거
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    return context


async def handle_cloudflare_challenge(page: Page, timeout: int = 10) -> bool:
    """
    Cloudflare 챌린지 처리
    
    Args:
        page: Page 인스턴스
        timeout: 대기 시간 (초)
    
    Returns:
        성공 여부
    """
    try:
        # Cloudflare 챌린지 감지
        challenge_frame = page.frame_locator('iframe[src*="challenges.cloudflare.com"]')
        if await challenge_frame.locator('input[type="checkbox"]').count() > 0:
            print("⚠️  Cloudflare 챌린지 감지됨. 수동으로 체크박스를 클릭해주세요...")
            await asyncio.sleep(timeout)
        
        return True
    except Exception as e:
        print(f"Cloudflare 챌린지 처리 중 에러: {e}")
        return False


async def random_delay(min_sec: float = 2.0, max_sec: float = 5.0):
    """
    랜덤 지연 시간 추가 (봇 탐지 우회)
    
    Args:
        min_sec: 최소 대기 시간 (초)
        max_sec: 최대 대기 시간 (초)
    """
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)
