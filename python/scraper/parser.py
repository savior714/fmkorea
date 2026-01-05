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
        
        # 제목 추출 - h1.np_18px 또는 span.np_18px_span
        title_elem = soup.select_one('h1.np_18px') or soup.select_one('span.np_18px_span')
        title = title_elem.get_text(strip=True) if title_elem else "제목 없음"
        
        # 본문 추출 - div.xe_content (텍스트 + 이미지)
        content_elem = soup.select_one('.xe_content')
        content = ""
        if content_elem:
            # 텍스트 추출
            text_content = content_elem.get_text(strip=True, separator='\n')
            
            # 이미지 URL도 추출 (이미지 기반 게시물 대응)
            images = content_elem.find_all('img')
            image_urls = [img.get('src') for img in images if img.get('src')]
            
            content = text_content
            if image_urls:
                content += "\n\n[이미지]\n" + "\n".join(image_urls)
        
        # 작성일 추출 - span.date.m_no
        date_elem = soup.select_one('span.date.m_no')
        date = date_elem.get_text(strip=True) if date_elem else ""
        
        # 조회수 추출 - .rd_hd .side.fr 영역의 첫 번째 span
        views = 0
        views_elem = soup.select_one('.rd_hd .side.fr span:nth-child(1) b')
        if views_elem:
            views_text = views_elem.get_text(strip=True)
            views_match = re.search(r'(\d+)', views_text.replace(',', ''))
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
        # 작성자 - a.member_plate
        author_elem = soup.select_one('a.member_plate')
        if author_elem:
            metadata['author'] = author_elem.get_text(strip=True)
        
        # 댓글 수 - .rd_hd .side.fr 영역의 세 번째 span
        comment_elem = soup.select_one('.rd_hd .side.fr span:nth-child(3) b')
        if comment_elem:
            comment_text = comment_elem.get_text(strip=True)
            comment_match = re.search(r'(\d+)', comment_text.replace(',', ''))
            if comment_match:
                metadata['comments'] = int(comment_match.group(1))
        
        # 추천 수 - a.vote_label
        vote_elem = soup.select_one('a.vote_label')
        if vote_elem:
            vote_text = vote_elem.get_text(strip=True)
            vote_match = re.search(r'(\d+)', vote_text.replace(',', ''))
            if vote_match:
                metadata['votes'] = int(vote_match.group(1))
        
    except Exception as e:
        print(f"메타데이터 추출 에러: {e}")
    
    return metadata
