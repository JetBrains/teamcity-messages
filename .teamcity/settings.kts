import jetbrains.buildServer.configs.kotlin.v2019_2.*
import jetbrains.buildServer.configs.kotlin.v2019_2.buildSteps.ScriptBuildStep
import jetbrains.buildServer.configs.kotlin.v2019_2.buildSteps.gradle
import jetbrains.buildServer.configs.kotlin.v2019_2.buildSteps.script

/*
The settings script is an entry point for defining a TeamCity
project hierarchy. The script should contain a single call to the
project() function with a Project instance or an init function as
an argument.

VcsRoots, BuildTypes, Templates, and subprojects can be
registered inside the project using the vcsRoot(), buildType(),
template(), and subProject() methods respectively.

To debug settings scripts in command-line, run the

    mvnDebug org.jetbrains.teamcity:teamcity-configs-maven-plugin:generate

command and attach your debugger to the port 8000.

To debug in IntelliJ Idea, open the 'Maven Projects' tool window (View
-> Tool Windows -> Maven Projects), find the generate task node
(Plugins -> teamcity-configs -> teamcity-configs:generate), the
'Debug' option is available in the context menu for the task.
*/

version = "2020.2"

project {

    buildType(Python27linux)
    buildType(Python36linux)
    buildType(Python37linux)
    buildType(Python37windows)
    buildType(Python38windows)
    buildType(Test)
    buildType(PyPy3linux)
    buildType(Python38linux)
    buildType(PyPy2linux)

    template(LinuxTeamcityMessages)
    template(WindowsTeamcityMessages)
}

object PyPy2linux : BuildType({
    templates(LinuxTeamcityMessages)
    name = "pypy2_linux"

    params {
        param("PYTHON_IMAGE", "pypy:2")
    }
})

object PyPy3linux : BuildType({
    templates(LinuxTeamcityMessages)
    name = "pypy3_linux"

    params {
        param("PYTHON_IMAGE", "pypy:3")
    }
})

object Python27linux : BuildType({
    templates(LinuxTeamcityMessages)
    name = "python_27_linux"

    params {
        param("PYTHON_IMAGE", "python:2.7")
    }
})

object Python36linux : BuildType({
    templates(LinuxTeamcityMessages)
    name = "python_36_linux"

    params {
        param("PYTHON_IMAGE", "python:3.6")
    }
})

object Python37linux : BuildType({
    templates(LinuxTeamcityMessages)
    name = "python_37_linux"

    params {
        param("PYTHON_IMAGE", "python:3.7")
    }
})

object Python37windows : BuildType({
    templates(WindowsTeamcityMessages)
    name = "python_37_windows"

    params {
        param("system.PYTHON_VERSION", "3.7.7")
    }
})

object Python38linux : BuildType({
    templates(LinuxTeamcityMessages)
    name = "python_38_linux"

    params {
        param("PYTHON_IMAGE", "python:3.8")
    }
})

object Python38windows : BuildType({
    templates(WindowsTeamcityMessages)
    name = "python_38_windows"

    params {
        param("system.PYTHON_VERSION", "3.8.2")
    }
})

object Test : BuildType({
    name = "Test"

    type = BuildTypeSettings.Type.COMPOSITE

    vcs {
        showDependenciesChanges = true
    }

    dependencies {
        snapshot(PyPy2linux) {
        }
        snapshot(PyPy3linux) {
        }
        snapshot(Python27linux) {
        }
        snapshot(Python36linux) {
        }
        snapshot(Python37linux) {
        }
        snapshot(Python37windows) {
        }
        snapshot(Python38linux) {
        }
        snapshot(Python38windows) {
        }
    }
})

object LinuxTeamcityMessages : Template({
    name = "linux-teamcity-messages"

    vcs {
        root(DslContext.settingsRoot)
    }

    steps {
        script {
            name = "Test"
            id = "RUNNER_TEST"
            scriptContent = """
                python -V
                echo "Install"
                pip install flake8 virtualenv pytest
                echo "Running flake"
                flake8 --ignore=E501,W504 --exclude=tests/guinea-pigs;
                echo "Test"
                python setup.py test
            """.trimIndent()
            dockerImagePlatform = ScriptBuildStep.ImagePlatform.Linux
            dockerImage = "%PYTHON_IMAGE%"
        }
    }
})

object WindowsTeamcityMessages : Template({
    name = "windows-teamcity-messages"

    params {
        param("env.PYTHON_HOME", "???")
    }

    vcs {
        root(DslContext.settingsRoot)
    }

    steps {
        gradle {
            name = "Setup python"
            id = "TEMPLATE_RUNNER_1"
            tasks = "buildBinaries"
            buildFile = "build.gradle"
            workingDir = "distributive"
        }
        script {
            name = "Test"
            id = "TEMPLATE_RUNNER_2"
            scriptContent = """
                echo "Install"
                %env.PYTHON_HOME%\python.exe -m pip install --upgrade setuptools
                echo "Build"
                %env.PYTHON_HOME%\python.exe setup.py sdist
                echo "Test"
                %env.PYTHON_HOME%\python.exe setup.py test
            """.trimIndent()
        }
    }

    requirements {
        contains("teamcity.agent.jvm.os.name", "Windows", "RQ_1")
    }
})
