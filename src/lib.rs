use std::ffi::CString;
use std::os::raw::{c_char, c_uchar};
use fig2json::convert;

// --- JNI API for Android/JVM ---
#[cfg(any(target_os = "android", target_os = "linux", target_os = "macos", target_os = "windows"))]
#[allow(non_snake_case)]
pub mod jni_api {
    use super::*;
    use jni::objects::{JClass, JByteArray};
    use jni::sys::jstring;
    use jni::JNIEnv;

    #[no_mangle]
    pub extern "system" fn Java_com_github_kreako_fig2json_NativeConverter_convertNative(
        env: JNIEnv,
        _class: JClass,
        fig_data: JByteArray,
    ) -> jstring {
        let bytes = match env.convert_byte_array(&fig_data) {
            Ok(b) => b,
            Err(_) => {
                return env.new_string("Error: Failed to read byte array from Java").unwrap().into_raw();
            }
        };

        match convert(&bytes, None) {
            Ok(json) => {
                let json_str = serde_json::to_string(&json).unwrap_or_else(|_| "Error: Failed to serialize JSON".to_string());
                env.new_string(json_str).unwrap().into_raw()
            }
            Err(e) => {
                let response = format!("Error: {}", e);
                env.new_string(response).unwrap().into_raw()
            }
        }
    }
}

// --- C API for iOS/Native ---
#[allow(non_snake_case)]
pub mod c_api {
    use super::*;

    #[no_mangle]
    pub extern "C" fn fig2json_convert(
        data: *const c_uchar,
        len: usize,
    ) -> *mut c_char {
        let bytes = unsafe { std::slice::from_raw_parts(data, len) };

        match convert(bytes, None) {
            Ok(json) => {
                let json_str = serde_json::to_string(&json).unwrap_or_else(|_| "Error: Failed to serialize JSON".to_string());
                CString::new(json_str).unwrap().into_raw()
            }
            Err(e) => {
                let response = format!("Error: {}", e);
                CString::new(response).unwrap().into_raw()
            }
        }
    }

    #[no_mangle]
    pub extern "C" fn fig2json_free_string(s: *mut c_char) {
        if s.is_null() { return; }
        unsafe { drop(CString::from_raw(s)) };
    }
}
