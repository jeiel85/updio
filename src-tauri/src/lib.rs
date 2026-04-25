use tauri::{AppHandle, Emitter};
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

#[tauri::command]
async fn start_upscale(
    app: AppHandle,
    input: String,
    output: String,
    scale: u32,
    model: String,
) -> Result<(), String> {
    let sidecar_command = app
        .shell()
        .sidecar("vibe-engine")
        .map_err(|e| e.to_string())?
        .args([
            "--input", &input, 
            "--output", &output, 
            "--scale", &scale.to_string(), 
            "--model", &model
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
                    // Emit raw stderr for direct display (already contains the error message)
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
