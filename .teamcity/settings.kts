import jetbrains.buildServer.configs.kotlin.v2019_2.*
import jetbrains.buildServer.configs.kotlin.v2019_2.buildFeatures.PullRequests
import jetbrains.buildServer.configs.kotlin.v2019_2.buildFeatures.commitStatusPublisher
import jetbrains.buildServer.configs.kotlin.v2019_2.buildFeatures.pullRequests
import jetbrains.buildServer.configs.kotlin.v2019_2.buildSteps.*
import jetbrains.buildServer.configs.kotlin.v2019_2.triggers.vcs

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

version = "2021.2"

project {

    buildType(Build)
    buildType(Python39windows)
    buildType(Python310windows)
    buildType(Python27linux)
    buildType(Python37linux)
    buildType(Python38linux)
    buildType(Python39linux)
    buildType(Python310linux)
    buildType(Pypy2linux)
    buildType(Pypy37linux)
    buildType(Pypy3linux)

    template(LinuxTeamcityMessagesTemplate)
    template(WindowsTeamcityMessagesTemplate)
}

object LinuxTeamcityMessagesTemplate : Template({
    name = "LinuxTeamcityMessagesTemplate"

    vcs {
        root(DslContext.settingsRoot)
    }

    features {
        pullRequests {
            vcsRootExtId = "${DslContext.settingsRoot.id}"
            provider = github {
                authType = vcsRoot()
                filterAuthorRole = PullRequests.GitHubRoleFilter.EVERYBODY
            }
        }
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

    features {
        pullRequests {
            vcsRootExtId = "${DslContext.settingsRoot.id}"
            provider = github {
                authType = vcsRoot()
                filterAuthorRole = PullRequests.GitHubRoleFilter.EVERYBODY
            }
        }
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
        script {
            name = "Test"
            scriptContent = """python %RESOLVED_DIR%\setup.py test"""
            dockerImage = "%PYTHON_DOCKER_IMAGE%"
            dockerImagePlatform = ScriptBuildStep.ImagePlatform.Windows
        }
    }

})


object Build : BuildType({
    name = "Build"

    type = Type.COMPOSITE

    vcs {
        root(DslContext.settingsRoot)

        showDependenciesChanges = true
    }

    triggers {
        vcs {

        }
    }

    features {
        pullRequests {
            vcsRootExtId = "${DslContext.settingsRoot.id}"
            provider = github {
                authType = vcsRoot()
                filterAuthorRole = PullRequests.GitHubRoleFilter.EVERYBODY
            }
        }

        commitStatusPublisher {
            vcsRootExtId = "${DslContext.settingsRoot.id}"
            publisher = github {
                githubUrl = "https://api.github.com"
                authType = personalToken {
                    token = "credentialsJSON:629f6262-fd6d-4ee3-845d-5ac1be62d64e"
                }
            }
        }
    }



    dependencies {
        snapshot(Python39windows) {}
        snapshot(Python310windows) {}
        snapshot(Python27linux) {}
        snapshot(Python37linux) {}
        snapshot(Python38linux) {}
        snapshot(Python39linux) {}
        snapshot(Python310linux) {}
        snapshot(Pypy2linux) {}
        snapshot(Pypy37linux) {}
        snapshot(Pypy3linux) {}
    }

})


object Python39windows : BuildType({
    templates(WindowsTeamcityMessagesTemplate)
    name = "Python 3.9 (Windows)"

    params {
        param("PYTHON_DOCKER_IMAGE", "python:3.9")
    }
})

object Python310windows : BuildType({
    templates(WindowsTeamcityMessagesTemplate)
    name = "Python 3.10 (Windows)"

    params {
        param("PYTHON_DOCKER_IMAGE", "python:3.10")
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

object Python39linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Python 3.9 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "python")
        param("PYTHON_DOCKER_IMAGE", "python:3.9")
    }
})

object Python310linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Python 3.10 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "python")
        param("PYTHON_DOCKER_IMAGE", "python:3.10")
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

object Pypy37linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Pypy 3.7 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "pypy")
        param("PYTHON_DOCKER_IMAGE", "pypy:3.7")
    }

})
