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
    // 디버그: 함수 호출 확인
    println!("🔍 [RUST] start_scraping called with mode={}, data={}, max_pages={:?}", mode, data, max_pages);
    let _ = app_handle.emit("scraping-log", format!("🔍 [RUST] start_scraping called with mode={}, data={}", mode, data));
    
    // 리소스 디렉토리 가져오기 (프로덕션) 또는 개발 경로 사용
    let (python_path, script_path, project_root) = if cfg!(debug_assertions) {
        // 개발 모드: 로컬 .venv 사용
        let project_root = PathBuf::from(r"C:\Users\savio\OneDrive\바탕 화면\develop\fmkorea");
        let python_path = if cfg!(target_os = "windows") {
            project_root.join(".venv").join("Scripts").join("python.exe")
        } else {
            project_root.join(".venv").join("bin").join("python")
        };
        let script_path = project_root.join("python").join("main.py");
        (python_path, script_path, project_root)
    } else {
        // 프로덕션 모드: 번들된 리소스 사용
        let resource_dir = app_handle
            .path()
            .resource_dir()
            .map_err(|e| e.to_string())?;
        
        let python_path = if cfg!(target_os = "windows") {
            resource_dir.join("python-embed").join("python.exe")
        } else {
            resource_dir.join("python-embed").join("python")
        };
        let script_path = resource_dir.join("python").join("main.py");
        let project_root = resource_dir.clone();
        (python_path, script_path, project_root)
    };
    
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

    std::thread::spawn(move || {
        let mut child = match Command::new(&python_path)
            .args(&args)
            .current_dir(&project_root) // CWD 명시적 설정
            .env("PYTHONIOENCODING", "utf-8") // UTF-8 인코딩 강제
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
        {
            Ok(child) => child,
            Err(e) => {
                let error_msg = format!("Failed to spawn python process: {}. Python path: {:?}, Project root: {:?}", e, python_path, project_root);
                let _ = app_handle_clone.emit("scraping-log", error_msg);
                return;
            }
        };

        // stdout 처리
        let app_handle_stdout = app_handle_clone.clone();
        if let Some(stdout) = child.stdout.take() {
            std::thread::spawn(move || {
                let reader = BufReader::new(stdout);
                for line in reader.lines() {
                    if let Ok(line) = line {
                        // 로그 이벤트 전송
                        let _ = app_handle_stdout.emit("scraping-log", line);
                    }
                }
            });
        }
        
        // stderr 처리 (에러 메시지도 UI에 표시)
        let app_handle_stderr = app_handle_clone.clone();
        if let Some(stderr) = child.stderr.take() {
            std::thread::spawn(move || {
                let reader = BufReader::new(stderr);
                for line in reader.lines() {
                    if let Ok(line) = line {
                        // stderr도 로그로 전송
                        let _ = app_handle_stderr.emit("scraping-log", format!("[ERROR] {}", line));
                    }
                }
            });
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
