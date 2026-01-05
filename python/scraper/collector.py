"""
FM Korea 게시물 수집 모듈
회원번호로 검색 또는 직접 URL로 게시물 수집
"""

import asyncio
import json
import sys
from typing import List, Dict, Callable, Optional
from playwright.async_api import Page
from .browser import create_stealth_browser, create_context, handle_cloudflare_challenge, random_delay
from .parser import parse_post_html


async def collect_posts_by_member(
    member_id: str,
    max_pages: int = 10,
    progress_callback: Optional[Callable] = None
) -> List[str]:
    """
    회원번호로 게시물 URL 목록 수집
    
    Args:
        member_id: FM Korea 회원번호
        max_pages: 최대 페이지 수
        progress_callback: 진행률 콜백 함수
    
    Returns:
        게시물 URL 리스트
    """
    browser = await create_stealth_browser(headless=False)
    context = await create_context(browser)
    page = await context.new_page()
    
    post_urls = []
    
    try:
        for page_num in range(1, max_pages + 1):
            search_url = f"https://www.fmkorea.com/search.php?mid=stock&search_target=member_srl&search_keyword={member_id}&page={page_num}"
            
            if progress_callback:
                progress_callback(f"페이지 {page_num}/{max_pages} 로딩 중...", page_num / max_pages * 50)
            
            print(f"📄 페이지 {page_num} 접근 중: {search_url}")
            
            await page.goto(search_url, wait_until="domcontentloaded")
            await random_delay(3, 5)
            
            # Cloudflare 챌린지 처리
            await handle_cloudflare_challenge(page)
            
            # 게시물 링크 추출
            links = await page.locator('a.hx').all()
            
            if not links:
                print(f"⚠️  페이지 {page_num}에서 게시물을 찾을 수 없습니다. 검색 종료.")
                break
            
            for link in links:
                href = await link.get_attribute('href')
                if href and '/board/' not in href:  # 댓글 링크 제외
                    full_url = f"https://www.fmkorea.com{href}" if href.startswith('/') else href
                    if full_url not in post_urls:
                        post_urls.append(full_url)
            
            print(f"✅ 페이지 {page_num}: {len(links)}개 게시물 발견")
            
            await random_delay(2, 4)
        
        print(f"\n🎯 총 {len(post_urls)}개 게시물 URL 수집 완료")
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    finally:
        try:
            await browser.close()
        except:
            pass
    
    return post_urls


async def collect_posts(
    urls: List[str],
    output_dir: str = "data/raw",
    progress_callback: Optional[Callable] = None
) -> List[str]:
    """
    게시물 URL 리스트에서 상세 내용 수집 (개별 파일로 즉시 저장)
    
    Args:
        urls: 게시물 URL 리스트
        output_dir: 저장 디렉토리
        progress_callback: 진행률 콜백 함수
    
    Returns:
        저장된 파일 경로 리스트
    """
    from pathlib import Path
    import hashlib
    
    # 출력 디렉토리 생성
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    browser = await create_stealth_browser(headless=False)
    context = await create_context(browser)
    page = await context.new_page()
    
    saved_files = []
    total = len(urls)
    
    try:
        for idx, url in enumerate(urls, 1):
            if progress_callback:
                progress_callback(f"게시물 {idx}/{total} 수집 중...", 50 + (idx / total * 50))
            
            print(f"\n📝 [{idx}/{total}] {url}")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await random_delay(2, 4)
                
                # HTML 가져오기
                html = await page.content()
                
                # 파싱
                post_data = parse_post_html(html, url)
                
                if post_data:
                    # URL 해시로 파일명 생성 (중복 방지)
                    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                    filename = f"post_{url_hash}.json"
                    filepath = output_path / filename
                    
                    # 즉시 파일로 저장 (메모리 절약)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(post_data, f, ensure_ascii=False, indent=2)
                    
                    saved_files.append(str(filepath))
                    print(f"✅ 저장: {filename} - {post_data.get('title', 'N/A')[:50]}...")
                else:
                    print(f"⚠️  파싱 실패")
                
            except Exception as e:
                print(f"❌ 에러: {e}")
                continue
        
        print(f"\n🎉 총 {len(saved_files)}개 게시물 파일 저장 완료")
        print(f"📁 저장 위치: {output_path.absolute()}")
        
    except Exception as e:
        print(f"❌ 전체 에러: {e}")
    finally:
        try:
            await browser.close()
        except:
            pass
    
    return saved_files


async def extract_post_data(page: Page) -> Dict:
    """
    현재 페이지에서 게시물 데이터 추출
    
    Args:
        page: Playwright Page 인스턴스
    
    Returns:
        게시물 데이터 딕셔너리
    """
    html = await page.content()
    url = page.url
    return parse_post_html(html, url)
