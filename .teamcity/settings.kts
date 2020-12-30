import jetbrains.buildServer.configs.kotlin.v2019_2.*
import jetbrains.buildServer.configs.kotlin.v2019_2.buildSteps.*

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

    buildType(Build)
    buildType(Python27windows)
    buildType(Python37windows)
    buildType(Python38windows)
    buildType(Python27linux)
    buildType(Python37linux)
    buildType(Python38linux)
    buildType(Pypy2linux)
    buildType(Pypy3linux)

    template(LinuxTeamcityMessagesTemplate)
    template(WindowsTeamcityMessagesTemplate)
}

object LinuxTeamcityMessagesTemplate : Template({
    name = "LinuxTeamcityMessagesTemplate"

    vcs {
        root(DslContext.settingsRoot)
    }

    steps {
        python {
            name = "Test"
            pythonVersion = customPython {
                executable = "%PYTHON_EXECUTABLE%"
            }
            command = file {
                filename = "setup.py"
                scriptArguments = "test"
            }
            dockerImage = "%PYTHON_DOCKER_IMAGE%"
            dockerImagePlatform = PythonBuildStep.ImagePlatform.Linux
        }
    }

})


object WindowsTeamcityMessagesTemplate : Template({
    name = "WindowsTeamcityMessagesTemplate"

    vcs {
        root(DslContext.settingsRoot)
    }

    params {
        param("RESOLVED_DIR", "RESOLVED_DIR_DEFAULT")
    }

    steps {
        python {
            name = "Resolving working dir for Docker"
            command = script {
                content = """
                    resolved = r"%teamcity.build.workingDir%"
                    print("##teamcity[setParameter name='RESOLVED_DIR' value='{}']".format(resolved.replace("Z:\\", "C:\\")))
                """.trimIndent()
            }
        }
        python {
            name = "Test"
            command = custom {
                arguments = """%RESOLVED_DIR%\setup.py test"""
            }
            dockerImage = "%PYTHON_DOCKER_IMAGE%"
            dockerImagePlatform = PythonBuildStep.ImagePlatform.Windows
        }
    }

})


object Build : BuildType({
    name = "Build"

    type = Type.COMPOSITE

    vcs {
        showDependenciesChanges = true
    }

    dependencies {
        snapshot(Python27windows) {}
        snapshot(Python37windows) {}
        snapshot(Python38windows) {}
        snapshot(Python27linux) {}
        snapshot(Python37linux) {}
        snapshot(Python38linux) {}
        snapshot(Pypy2linux) {}
        snapshot(Pypy3linux) {}
    }

})


object Python27windows : BuildType({
    templates(WindowsTeamcityMessagesTemplate)
    name = "Python 2.7 (Windows)"

    params {
        param("PYTHON_DOCKER_IMAGE", "python:2.7")
    }
})


object Python37windows : BuildType({
    templates(WindowsTeamcityMessagesTemplate)
    name = "Python 3.7 (Windows)"

    params {
        param("PYTHON_DOCKER_IMAGE", "python:3.7")
    }
})


object Python38windows : BuildType({
    templates(WindowsTeamcityMessagesTemplate)
    name = "Python 3.8 (Windows)"

    params {
        param("PYTHON_DOCKER_IMAGE", "python:3.8")
    }
})


object Python27linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Python 2.7 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "python")
        param("PYTHON_DOCKER_IMAGE", "python:2.7")
    }
})


object Python37linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Python 3.7 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "python")
        param("PYTHON_DOCKER_IMAGE", "python:3.7")
    }
})


object Python38linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Python 3.8 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "python")
        param("PYTHON_DOCKER_IMAGE", "python:3.8")
    }
})

object Pypy2linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Pypy 2 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "pypy")
        param("PYTHON_DOCKER_IMAGE", "pypy:2")
    }

})

object Pypy3linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Pypy 3 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "pypy")
        param("PYTHON_DOCKER_IMAGE", "pypy:3")
    }

})
