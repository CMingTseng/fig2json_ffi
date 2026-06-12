package com.github.kreako.fig2json

import java.io.File

actual class NativeConverter {
    actual fun convert(figData: ByteArray): String {
        return convertNative(figData)
    }

    actual fun readFile(path: String): ByteArray {
        return File(path).readBytes()
    }

    actual fun writeFile(path: String, data: String) {
        File(path).writeText(data)
    }

    private external fun convertNative(figData: ByteArray): String

    companion object {
        init {
            System.loadLibrary("fig2json")
        }
    }
}
