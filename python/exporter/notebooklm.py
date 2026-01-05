"""
NotebookLM 호환 Markdown 변환 모듈
수집된 게시물을 NotebookLM에 업로드 가능한 형태로 변환
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def convert_post_to_markdown(post: Dict) -> str:
    """
    게시물 데이터를 Markdown 형식으로 변환
    
    Args:
        post: 게시물 데이터 딕셔너리
    
    Returns:
        Markdown 형식 문자열
    """
    md_lines = []
    
    # 제목
    title = post.get('title', '제목 없음')
    md_lines.append(f"# {title}\n")
    
    # 메타데이터
    md_lines.append("## 메타데이터\n")
    md_lines.append(f"- **URL**: {post.get('url', 'N/A')}")
    md_lines.append(f"- **작성일**: {post.get('date', 'N/A')}")
    md_lines.append(f"- **조회수**: {post.get('views', 0):,}")
    
    metadata = post.get('metadata', {})
    if metadata.get('author'):
        md_lines.append(f"- **작성자**: {metadata['author']}")
    if metadata.get('comments'):
        md_lines.append(f"- **댓글 수**: {metadata['comments']}")
    if metadata.get('votes'):
        md_lines.append(f"- **추천 수**: {metadata['votes']}")
    
    md_lines.append("")
    
    # 본문
    md_lines.append("## 본문\n")
    content = post.get('content', '')
    md_lines.append(content)
    
    md_lines.append("\n---\n")
    
    return "\n".join(md_lines)


def export_to_notebooklm(
    data_dir: str = "data/raw",
    output_dir: str = "data/notebooklm",
    combine: bool = True
) -> List[str]:
    """
    수집된 게시물을 NotebookLM 호환 Markdown으로 변환
    
    Args:
        data_dir: 원본 JSON 파일 디렉토리
        output_dir: Markdown 출력 디렉토리
        combine: True면 하나의 파일로 통합, False면 개별 파일
    
    Returns:
        생성된 파일 경로 리스트
    """
    data_path = Path(data_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # JSON 파일 로드
    json_files = sorted(data_path.glob("post_*.json"))
    
    if not json_files:
        print("⚠️  변환할 게시물이 없습니다.")
        return []
    
    print(f"📂 {len(json_files)}개 게시물 발견")
    
    posts = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                post = json.load(f)
                posts.append(post)
        except Exception as e:
            print(f"⚠️  파일 로드 실패 ({json_file.name}): {e}")
    
    # 최신순 정렬 (document_srl 기준 내림차순)
    import re
    def get_post_id(post):
        url = post.get('url', '')
        # document_srl=12345... 패턴 찾기
        match = re.search(r'document_srl=(\d+)', url)
        if match:
            return int(match.group(1))
        # /12345678 패턴 (단축 URL)
        match = re.search(r'/(\d{7,})', url)
        if match:
            return int(match.group(1))
        return 0

    posts.sort(key=get_post_id, reverse=True)
    print("✅ 게시물 최신순 정렬 완료")
    
    saved_files = []
    
    if combine:
        # 하나의 Markdown 파일로 통합
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_path / f"fmkorea_posts_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 헤더
            f.write(f"# FM Korea 게시물 모음\n\n")
            f.write(f"**수집 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**총 게시물 수**: {len(posts)}\n\n")
            f.write("---\n\n")
            
            # 각 게시물
            for idx, post in enumerate(posts, 1):
                f.write(f"<!-- 게시물 {idx}/{len(posts)} -->\n\n")
                f.write(convert_post_to_markdown(post))
                f.write("\n")
        
        saved_files.append(str(output_file))
        print(f"✅ 통합 파일 생성: {output_file.name}")
        print(f"📊 총 {len(posts)}개 게시물 포함")
        
    else:
        # 개별 Markdown 파일로 저장
        for idx, post in enumerate(posts, 1):
            # 파일명: 제목의 처음 30자 + 해시
            title = post.get('title', 'untitled')
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:30]
            url_hash = post.get('url', '').split('/')[-1][:8]
            filename = f"{idx:03d}_{safe_title}_{url_hash}.md"
            
            output_file = output_path / filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(convert_post_to_markdown(post))
            
            saved_files.append(str(output_file))
        
        print(f"✅ {len(saved_files)}개 개별 파일 생성")
    
    print(f"📁 저장 위치: {output_path.absolute()}")
    print(f"\n💡 NotebookLM 사용법:")
    print(f"   1. https://notebooklm.google.com 접속")
    print(f"   2. 'New notebook' 생성")
    print(f"   3. 'Upload' 버튼으로 생성된 Markdown 파일 업로드")
    print(f"   4. 자유롭게 질문하여 투자 패턴 분석")
    
    return saved_files


def create_analysis_guide(output_dir: str = "data/notebooklm") -> str:
    """
    NotebookLM 분석 가이드 파일 생성
    
    Args:
        output_dir: 출력 디렉토리
    
    Returns:
        생성된 파일 경로
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    guide_file = output_path / "분석_가이드.md"
    
    guide_content = """# NotebookLM 투자 패턴 분석 가이드

이 문서는 수집된 FM Korea 게시물을 NotebookLM으로 분석하는 방법을 안내합니다.

## 📌 추천 질문 예시

### 투자 철학 분석
- "이 작성자의 주요 투자 철학은 무엇인가요?"
- "가치투자와 모멘텀 투자 중 어느 쪽에 가까운가요?"
- "장기투자와 단기투자 중 어떤 성향인가요?"

### 매매 패턴 분석
- "주로 어떤 시점에 매수하나요?"
- "손절과 익절 기준은 무엇인가요?"
- "매수 후 평균 보유 기간은 얼마나 되나요?"

### 섹터 및 종목 분석
- "가장 자주 언급하는 산업 섹터는 무엇인가요?"
- "반복적으로 언급하는 종목이 있나요?"
- "최근 관심을 보이는 새로운 섹터가 있나요?"

### 리스크 관리
- "리스크 관리 전략은 무엇인가요?"
- "분산투자를 선호하나요, 집중투자를 선호하나요?"
- "시장 하락 시 어떻게 대응하나요?"

### 시계열 분석
- "투자 성향이 시간에 따라 변화했나요?"
- "최근 3개월과 이전 기간의 투자 패턴 차이는?"
- "특정 시장 이벤트에 어떻게 반응했나요?"

### 심리 및 태도
- "투자에 대한 전반적인 태도는 어떤가요? (낙관적/신중함/공격적 등)"
- "다른 투자자들의 의견을 어떻게 받아들이나요?"
- "실패한 투자에 대해 어떻게 회고하나요?"

## 💡 분석 팁

1. **구체적으로 질문하기**: "투자 성향은?" 보다 "가치투자 성향이 있나요?"가 더 좋은 답변을 얻습니다.

2. **후속 질문하기**: NotebookLM의 답변을 바탕으로 더 깊이 파고들 수 있습니다.

3. **비교 질문하기**: "A와 B 중 어느 것을 선호하나요?" 형태의 질문이 효과적입니다.

4. **인용 확인하기**: NotebookLM은 답변에 출처를 표시하므로 원문을 확인할 수 있습니다.

5. **요약 요청하기**: "전체 내용을 3가지 핵심 포인트로 요약해주세요" 같은 요청도 가능합니다.

## 🎯 분석 결과 활용

- 투자 스타일 벤치마킹
- 리스크 관리 전략 학습
- 섹터 트렌드 파악
- 매매 타이밍 인사이트 도출

---

**주의**: 이 분석은 학습 및 연구 목적으로만 사용하세요. 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.
"""
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"📖 분석 가이드 생성: {guide_file.name}")
    
    return str(guide_file)


if __name__ == "__main__":
    import sys
    
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    combine = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else True
    
    print("\n" + "="*50)
    print("📝 NotebookLM 형식으로 변환 중...")
    print("="*50 + "\n")
    
    # Markdown 변환
    files = export_to_notebooklm(data_dir, combine=combine)
    
    # 분석 가이드 생성
    create_analysis_guide()
    
    print(f"\n✅ 변환 완료! {len(files)}개 파일 생성됨")
