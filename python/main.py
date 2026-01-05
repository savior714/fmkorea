"""
FM Korea 투자 패턴 분석 CLI
Tauri에서 호출되는 메인 스크립트
"""

import asyncio
import json
import sys
from pathlib import Path
from scraper import collect_posts_by_member, collect_posts


async def main():
    """메인 실행 함수"""
    
    # 커맨드 라인 인자 파싱
    if len(sys.argv) < 3:
        print(json.dumps({"error": "사용법: python main.py <mode> <data>"}))
        sys.exit(1)
    
    mode = sys.argv[1]  # "member" 또는 "urls"
    data = sys.argv[2]  # 회원번호 또는 URL 리스트 (JSON)
    
    # 출력 디렉토리 설정
    output_dir = Path(__file__).parent.parent / "data" / "raw"
    
    try:
        if mode == "member":
            # 회원번호로 검색
            member_id = data
            max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            
            print(json.dumps({"status": "회원번호로 게시물 검색 중...", "progress": 0}))
            sys.stdout.flush()
            
            # 게시물 URL 수집
            urls = await collect_posts_by_member(
                member_id=member_id,
                max_pages=max_pages,
                progress_callback=lambda msg, prog: print_progress(msg, prog)
            )
            
            if not urls:
                print(json.dumps({"error": "게시물을 찾을 수 없습니다"}))
                sys.exit(1)
            
            # 게시물 상세 수집 (개별 파일로 저장)
            saved_files = await collect_posts(
                urls=urls,
                output_dir=str(output_dir),
                progress_callback=lambda msg, prog: print_progress(msg, prog)
            )
            
        elif mode == "urls":
            # 직접 URL 입력
            urls = json.loads(data)
            
            print(json.dumps({"status": "게시물 수집 중...", "progress": 0}))
            sys.stdout.flush()
            
            saved_files = await collect_posts(
                urls=urls,
                output_dir=str(output_dir),
                progress_callback=lambda msg, prog: print_progress(msg, prog)
            )
        
        else:
            print(json.dumps({"error": f"알 수 없는 모드: {mode}"}))
            sys.exit(1)
        
        # NotebookLM 형식으로 자동 변환
        print(json.dumps({"status": "NotebookLM 형식으로 변환 중...", "progress": 95}))
        sys.stdout.flush()
        
        from exporter import export_to_notebooklm, create_analysis_guide
        
        notebooklm_files = export_to_notebooklm(
            data_dir=str(output_dir),
            output_dir=str(output_dir.parent / "notebooklm"),
            combine=True  # 하나의 파일로 통합
        )
        
        # 분석 가이드 생성
        guide_file = create_analysis_guide(str(output_dir.parent / "notebooklm"))
        
        # 최종 결과 출력 (파일 경로만 반환, 메모리 절약)
        print(json.dumps({
            "status": "완료",
            "progress": 100,
            "saved_files": saved_files,
            "total_files": len(saved_files),
            "output_dir": str(output_dir.absolute()),
            "notebooklm_files": notebooklm_files,
            "guide_file": guide_file
        }, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


def print_progress(message: str, progress: float):
    """진행률 출력 (Tauri가 파싱)"""
    print(json.dumps({
        "status": message,
        "progress": int(progress)
    }, ensure_ascii=False))
    sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
