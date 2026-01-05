use std::process::{Command, Stdio};
use std::path::PathBuf;
use tauri::{AppHandle, Manager};

use std::io::{BufRead, BufReader};
use tauri::Emitter;

#[tauri::command]
pub async fn start_scraping(
    app_handle: AppHandle,
    mode: String,
    data: String,
    max_pages: Option<u32>,
) -> Result<(), String> {
    // 현재 디렉토리 가져오기
    let app_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| e.to_string())?;
    
    // Python 실행 파일 경로
    let python_path = if cfg!(target_os = "windows") {
        PathBuf::from(".venv\\Scripts\\python.exe")
    } else {
        PathBuf::from(".venv/bin/python")
    };
    
    // Python 스크립트 경로
    let script_path = PathBuf::from("python/main.py");
    
    // 인자 구성
    let mut args = vec![
        "-u".to_string(), // Unbuffered output
        script_path.to_str().unwrap().to_string(),
        mode.clone(),
        data.clone(),
    ];
    
    if let Some(pages) = max_pages {
        args.push(pages.to_string());
    }
    
    // 비동기 스레드에서 실행
    let app_handle_clone = app_handle.clone();
    // 프로젝트 루트 경로 (개발 환경용 하드코딩, 실제 배포 시 resource_dir로 변경 필요)
    let project_root = PathBuf::from(r"C:\Users\neo24\Desktop\cursor\fmkorea");

    std::thread::spawn(move || {
        let mut child = Command::new(python_path)
            .args(&args)
            .current_dir(&project_root) // CWD 명시적 설정
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .expect("Failed to spawn python process");

        if let Some(stdout) = child.stdout.take() {
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                if let Ok(line) = line {
                    // 로그 이벤트 전송
                    let _ = app_handle_clone.emit("scraping-log", line);
                }
            }
        }
        
        let _ = child.wait();
        // 완료 이벤트 전송
        let _ = app_handle_clone.emit("scraping-complete", "done");
    });
    
    Ok(())
}

#[tauri::command]
pub async fn open_explorer(path: String) -> Result<(), String> {
    use std::process::Command;
    
    #[cfg(target_os = "windows")]
    {
        // 파일이 존재하면 선택하고, 아니면 그냥 폴더를 염
        let p = std::path::Path::new(&path);
        if p.exists() && p.is_file() {
            Command::new("explorer")
                .arg("/select,")
                .arg(&path)
                .spawn()
                .map_err(|e| e.to_string())?;
        } else {
             Command::new("explorer")
                .arg(&path)
                .spawn()
                .map_err(|e| e.to_string())?;
        }
    }
    
    Ok(())
}

#[tauri::command]
pub fn get_app_dir(app_handle: AppHandle) -> Result<String, String> {
    let app_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| e.to_string())?;
    
    Ok(app_dir.to_string_lossy().to_string())
}
