import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.kotlin.multiplatform.library)
}

kotlin {
    jvm()
    androidLibrary {
        namespace = "com.github.kreako.fig2json"
        compileSdk = 37
        minSdk = 21
        compilerOptions {
            jvmTarget = JvmTarget.JVM_11
        }
    }

    iosArm64()
    iosSimulatorArm64()

    targets.withType<org.jetbrains.kotlin.gradle.plugin.mpp.KotlinNativeTarget>().forEach { target ->
        target.compilations.getByName("main") {
            val fig2json by cinterops.creating {
                definitionFile.set(project.file("src/nativeInterop/cinterop/fig2json.def"))
                includeDirs(project.file("include"))
            }
        }
    }

    targets.all {
        compilations.all {
            compileTaskProvider.configure {
                compilerOptions {
                    freeCompilerArgs.add("-Xexpect-actual-classes")
                }
            }
        }
    }

    sourceSets {
        val jvmMain by getting {
            resources.srcDir("src/jvmMain/resources")
        }
    }
}
