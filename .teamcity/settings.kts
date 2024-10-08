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
    buildType(Python312windows)
    buildType(Python39linux)
    buildType(Python310linux)
    buildType(Python311linux)
    buildType(Python312linux)
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
            command = pytest()
            environment = venv {
                requirementsFile = "requirements.txt"
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
        python {
            name = "Test"
            workingDir = "%RESOLVED_DIR%"
            command = pytest()
            environment = venv {
                requirementsFile = "requirements.txt"
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
        snapshot(Python312windows) {}
        snapshot(Python39linux) {}
        snapshot(Python310linux) {}
        snapshot(Python311linux) {}
        snapshot(Python312linux) {}
        snapshot(Pypy3linux) {}
    }

})

object Python312windows : BuildType({
    templates(WindowsTeamcityMessagesTemplate)
    name = "Python 3.12 (Windows)"

    params {
        param("PYTHON_DOCKER_IMAGE", "python:3.12")
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

object Python311linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Python 3.11 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "python")
        param("PYTHON_DOCKER_IMAGE", "python:3.11")
    }
})

object Python312linux : BuildType({
    templates(LinuxTeamcityMessagesTemplate)
    name = "Python 3.12 (Linux)"

    params {
        param("PYTHON_EXECUTABLE", "python")
        param("PYTHON_DOCKER_IMAGE", "python:3.12")
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
