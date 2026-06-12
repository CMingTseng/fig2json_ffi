package com.github.kreako.fig2json

import java.io.File
import java.nio.file.Files
import java.nio.file.StandardCopyOption

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
            loadNativeLibrary()
        }

        private fun loadNativeLibrary() {
            try {
                System.loadLibrary("fig2json")
            } catch (e: UnsatisfiedLinkError) {
                try {
                    loadFromResources()
                } catch (ex: Exception) {
                    println("Failed to load native library: ${ex.message}")
                }
            }
        }

        private fun loadFromResources() {
            val osName = System.getProperty("os.name").lowercase()
            val (ext, prefix) = when {
                osName.contains("win") -> "dll" to ""
                osName.contains("mac") -> "dylib" to "lib"
                else -> "so" to "lib"
            }
            val fileName = "${prefix}fig2json.$ext"
            
            // Try different ways to load the resource
            val inputStream = NativeConverter::class.java.getResourceAsStream("/$fileName")
                ?: NativeConverter::class.java.classLoader.getResourceAsStream(fileName)
                ?: Thread.currentThread().contextClassLoader.getResourceAsStream(fileName)
                ?: throw RuntimeException("Library $fileName not found in resources. OS: $osName")

            val tempDir = Files.createTempDirectory("fig2json-native")
            val tempFile = tempDir.resolve(fileName)
            Files.copy(inputStream, tempFile, StandardCopyOption.REPLACE_EXISTING)
            System.load(tempFile.toAbsolutePath().toString())
        }
    }
}
