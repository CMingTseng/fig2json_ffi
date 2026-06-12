package com.github.kreako.fig2json

import kotlinx.cinterop.*
import platform.Foundation.*
import platform.posix.memcpy
import com.github.kreako.fig2json.native.*

actual class NativeConverter {
    @OptIn(ExperimentalForeignApi::class)
    actual fun convert(figData: ByteArray): String {
        return memScoped {
            val pinned = figData.pin()
            val resultPtr = fig2json_convert(
                pinned.addressOf(0).reinterpret(),
                figData.size.toULong()
            )
            val result = resultPtr?.toKString() ?: "Error: Failed to convert"
            fig2json_free_string(resultPtr)
            pinned.unpin()
            result
        }
    }

    @OptIn(ExperimentalForeignApi::class)
    actual fun readFile(path: String): ByteArray {
        val data = NSData.dataWithContentsOfFile(path) ?: return ByteArray(0)
        return data.toByteArray()
    }

    @OptIn(ExperimentalForeignApi::class, BetaInteropApi::class)
    actual fun writeFile(path: String, data: String) {
        NSString.create(string = data).writeToFile(path, true, NSUTF8StringEncoding, null)
    }
}

@OptIn(ExperimentalForeignApi::class)
fun NSData.toByteArray(): ByteArray {
    val size = length.toInt()
    val result = ByteArray(size)
    if (size > 0) {
        result.usePinned { pinned ->
            memcpy(pinned.addressOf(0), bytes, length)
        }
    }
    return result
}
