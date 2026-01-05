"""
FM Korea HTML 파싱 모듈
BeautifulSoup을 사용한 게시물 데이터 추출
"""

from bs4 import BeautifulSoup
from typing import Dict, Optional
import re


def parse_post_html(html: str, url: str) -> Optional[Dict]:
    """
    HTML에서 게시물 데이터 추출
    
    Args:
        html: HTML 문자열
        url: 게시물 URL
    
    Returns:
        게시물 데이터 딕셔너리 또는 None
    """
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # 제목 추출
        title_elem = soup.select_one('h1.np_18px, h1.title, .document_title')
        title = title_elem.get_text(strip=True) if title_elem else "제목 없음"
        
        # 본문 추출
        content_elem = soup.select_one('.rd_body, .document_content, article')
        content = content_elem.get_text(strip=True) if content_elem else ""
        
        # 작성일 추출
        date_elem = soup.select_one('.date, .time, .regdate')
        date = date_elem.get_text(strip=True) if date_elem else ""
        
        # 조회수 추출
        views_elem = soup.select_one('.m_no')
        views = 0
        if views_elem:
            views_text = views_elem.get_text(strip=True)
            views_match = re.search(r'(\d+)', views_text)
            if views_match:
                views = int(views_match.group(1))
        
        # 메타데이터
        metadata = extract_metadata(soup)
        
        return {
            "url": url,
            "title": title,
            "content": content,
            "date": date,
            "views": views,
            "metadata": metadata
        }
        
    except Exception as e:
        print(f"파싱 에러: {e}")
        return None


def extract_metadata(soup: BeautifulSoup) -> Dict:
    """
    추가 메타데이터 추출
    
    Args:
        soup: BeautifulSoup 객체
    
    Returns:
        메타데이터 딕셔너리
    """
    metadata = {}
    
    try:
        # 작성자
        author_elem = soup.select_one('.nick, .author, .username')
        if author_elem:
            metadata['author'] = author_elem.get_text(strip=True)
        
        # 댓글 수
        comment_elem = soup.select_one('.comment_count, .cmt')
        if comment_elem:
            comment_text = comment_elem.get_text(strip=True)
            comment_match = re.search(r'(\d+)', comment_text)
            if comment_match:
                metadata['comments'] = int(comment_match.group(1))
        
        # 추천 수
        vote_elem = soup.select_one('.voted_count, .like')
        if vote_elem:
            vote_text = vote_elem.get_text(strip=True)
            vote_match = re.search(r'(\d+)', vote_text)
            if vote_match:
                metadata['votes'] = int(vote_match.group(1))
        
    except Exception as e:
        print(f"메타데이터 추출 에러: {e}")
    
    return metadata
