package com.github.kreako.fig2json

expect class NativeConverter() {
    fun convert(figData: ByteArray): String
    fun readFile(path: String): ByteArray
    fun writeFile(path: String, data: String)
}
