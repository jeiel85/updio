use tauri::{AppHandle, Emitter, Manager};
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone)]
struct ProgressPayload {
    current: u32,
    total: u32,
    percentage: f64,
    message: String,
}

#[derive(Serialize, Clone)]
struct FinishedPayload {
    code: Option<i32>,
    error: Option<String>,
}

fn find_sidecar_binary(app: &AppHandle, name: &str) -> String {
    if let Ok(resource_dir) = app.path().resource_dir() {
        // Dev mode: resource_dir is src-tauri/, binaries are in binaries/ subdir with triple suffix
        let dev_path = resource_dir
            .join("binaries")
            .join(format!("{}-x86_64-pc-windows-msvc.exe", name));
        if dev_path.exists() {
            return dev_path.to_string_lossy().to_string();
        }

        // Release mode: Tauri strips the triple suffix during bundling
        let release_path = resource_dir.join(format!("{}.exe", name));
        if release_path.exists() {
            return release_path.to_string_lossy().to_string();
        }
    }

    // Fallback: check next to the app executable (some NSIS layouts)
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            let p = dir.join(format!("{}.exe", name));
            if p.exists() {
                return p.to_string_lossy().to_string();
            }
        }
    }

    name.to_string()
}

#[tauri::command]
async fn start_upscale(
    app: AppHandle,
    input: String,
    output: String,
    scale: u32,
    model: String,
) -> Result<(), String> {
    let ffmpeg_path = find_sidecar_binary(&app, "ffmpeg");
    let ffprobe_path = find_sidecar_binary(&app, "ffprobe");

    let sidecar_command = app
        .shell()
        .sidecar("vibe-engine")
        .map_err(|e| e.to_string())?
        .args([
            "--input", &input,
            "--output", &output,
            "--scale", &scale.to_string(),
            "--model", &model,
            "--ffmpeg", &ffmpeg_path,
            "--ffprobe", &ffprobe_path,
        ]);

    let (mut rx, _child) = sidecar_command
        .spawn()
        .map_err(|e| e.to_string())?;

    tauri::async_runtime::spawn(async move {
        let mut stderr_buf: Vec<String> = Vec::new();

        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    let line_str = String::from_utf8_lossy(&line);
                    if let Ok(payload) = serde_json::from_str::<ProgressPayload>(&line_str) {
                        let _ = app.emit("upscale-progress", payload);
                    }
                }
                CommandEvent::Stderr(line) => {
                    let s = String::from_utf8_lossy(&line).trim().to_string();
                    if !s.is_empty() {
                        stderr_buf.push(s);
                    }
                }
                CommandEvent::Terminated(payload) => {
                    let code = payload.code;
                    let error = if code != Some(0) {
                        if !stderr_buf.is_empty() {
                            Some(stderr_buf.join("\n"))
                        } else {
                            Some(format!("Process exited with code {:?}", code))
                        }
                    } else {
                        None
                    };
                    let _ = app.emit("upscale-finished", FinishedPayload { code, error });
                }
                _ => {}
            }
        }
    });

    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .setup(|_app| {
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![start_upscale])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
