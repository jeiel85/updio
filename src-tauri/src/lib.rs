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
struct ErrorPayload {
    message: String,
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

    // Final fallback: hope it's in PATH
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
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    let line_str = String::from_utf8_lossy(&line);
                    if let Ok(payload) = serde_json::from_str::<ProgressPayload>(&line_str) {
                        let _ = app.emit("upscale-progress", payload);
                    }
                }
                CommandEvent::Stderr(line) => {
                    let line_str = String::from_utf8_lossy(&line);
                    let _ = app.emit("upscale-error", ErrorPayload { message: line_str.to_string() });
                }
                CommandEvent::Terminated(payload) => {
                    let _ = app.emit("upscale-finished", payload.code);
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
