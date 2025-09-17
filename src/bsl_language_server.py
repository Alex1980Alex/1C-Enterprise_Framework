"""
Provides BSL (Business System Language / 1C:Enterprise) specific instantiation of the LanguageServer class.
Contains various configurations and settings specific to BSL/1C development.
Uses the 1C-syntax/bsl-language-server implementation.
"""

import dataclasses
import logging
import os
import pathlib
import shutil
import threading
import uuid
from pathlib import PurePath

from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.ls_logger import LanguageServerLogger
from solidlsp.ls_utils import FileUtils, PlatformUtils
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings


@dataclasses.dataclass
class BslRuntimeDependencyPaths:
    """
    Stores the paths to the runtime dependencies of BSL Language Server
    """

    jre_path: str
    jre_home_path: str
    bsl_ls_jar_path: str


class BslLanguageServer(SolidLanguageServer):
    """
    The BslLanguageServer class provides a BSL/1C:Enterprise specific implementation of the LanguageServer class
    using the 1C-syntax/bsl-language-server implementation.
    """

    def __init__(
        self, config: LanguageServerConfig, logger: LanguageServerLogger, repository_root_path: str, solidlsp_settings: SolidLSPSettings
    ):
        """
        Creates a new BslLanguageServer instance initializing the language server settings appropriately.
        This class is not meant to be instantiated directly. Use LanguageServer.create() instead.
        """
        runtime_dependency_paths = self._setup_runtime_dependencies(logger, config, solidlsp_settings)
        self.runtime_dependency_paths = runtime_dependency_paths

        # Create workspace directory for BSL Language Server
        ws_dir = str(
            PurePath(
                solidlsp_settings.ls_resources_dir,
                "BslLanguageServer",
                "workspaces",
                uuid.uuid4().hex,
            )
        )
        os.makedirs(ws_dir, exist_ok=True)

        jre_path = self.runtime_dependency_paths.jre_path
        bsl_ls_jar = self.runtime_dependency_paths.bsl_ls_jar_path

        for static_path in [jre_path, bsl_ls_jar]:
            assert os.path.exists(static_path), f"Required path does not exist: {static_path}"

        # Set up Java environment
        proc_env = {"JAVA_HOME": self.runtime_dependency_paths.jre_home_path}
        proc_cwd = repository_root_path

        # Construct command to run BSL Language Server
        cmd = " ".join([f'"{jre_path}"', "-jar", f'"{bsl_ls_jar}"', "--stdio"])

        self.service_ready_event = threading.Event()

        super().__init__(
            config, logger, repository_root_path, ProcessLaunchInfo(cmd, proc_env, proc_cwd), "bsl", solidlsp_settings=solidlsp_settings
        )

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # Ignore common 1C build directories and system folders
        return super().is_ignored_dirname(dirname) or dirname in [
            "Журналы",  # 1C logs
            "ЖурналРегистрации",  # 1C event log
            "ConfigSave",  # 1C config backup
            "ExtCompT",  # 1C external components temp
            "temp",  # General temp
            "tmp",  # General temp
            "logs",  # Logs
            ".dt",  # 1C database files
            ".1cd",  # 1C database files
        ]

    @classmethod
    def _setup_runtime_dependencies(
        cls, logger: LanguageServerLogger, config: LanguageServerConfig, solidlsp_settings: SolidLSPSettings
    ) -> BslRuntimeDependencyPaths:
        """
        Setup runtime dependencies for BSL Language Server and return the paths.
        Downloads JRE and BSL Language Server JAR if needed.
        """
        platform_id = PlatformUtils.get_platform_id()

        # Runtime dependencies configuration
        runtime_dependencies = {
            "adoptium-jre": {
                "linux-x64": {
                    "url": "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.5%2B11/OpenJDK21U-jre_x64_linux_hotspot_21.0.5_11.tar.gz",
                    "archiveType": "tar.gz",
                    "relative_extraction_path": "jdk-21.0.5+11-jre",
                    "jre_home_path": "jdk-21.0.5+11-jre",
                    "jre_path": "jdk-21.0.5+11-jre/bin/java",
                },
                "win-x64": {
                    "url": "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.5%2B11/OpenJDK21U-jre_x64_windows_hotspot_21.0.5_11.zip",
                    "archiveType": "zip",
                    "relative_extraction_path": "jdk-21.0.5+11-jre",
                    "jre_home_path": "jdk-21.0.5+11-jre",
                    "jre_path": "jdk-21.0.5+11-jre/bin/java.exe",
                },
                "osx-x64": {
                    "url": "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.5%2B11/OpenJDK21U-jre_x64_mac_hotspot_21.0.5_11.tar.gz",
                    "archiveType": "tar.gz",
                    "relative_extraction_path": "jdk-21.0.5+11-jre",
                    "jre_home_path": "jdk-21.0.5+11-jre/Contents/Home",
                    "jre_path": "jdk-21.0.5+11-jre/Contents/Home/bin/java",
                },
                "osx-arm64": {
                    "url": "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.5%2B11/OpenJDK21U-jre_aarch64_mac_hotspot_21.0.5_11.tar.gz",
                    "archiveType": "tar.gz",
                    "relative_extraction_path": "jdk-21.0.5+11-jre",
                    "jre_home_path": "jdk-21.0.5+11-jre/Contents/Home",
                    "jre_path": "jdk-21.0.5+11-jre/Contents/Home/bin/java",
                },
            },
            "bsl-language-server": {
                "platform-agnostic": {
                    "url": "https://github.com/1c-syntax/bsl-language-server/releases/download/v0.24.2/bsl-language-server-0.24.2-exec.jar",
                    "archiveType": "file",
                    "relative_extraction_path": "bsl-language-server-0.24.2-exec.jar",
                }
            },
        }

        # Setup JRE
        if platform_id.value not in runtime_dependencies["adoptium-jre"]:
            raise ValueError(f"BSL Language Server: Unsupported platform {platform_id.value}")

        jre_dependency = runtime_dependencies["adoptium-jre"][platform_id.value]
        jre_dir = str(PurePath(cls.ls_resources_dir(solidlsp_settings), "adoptium-jre"))
        os.makedirs(jre_dir, exist_ok=True)

        jre_home_path = str(PurePath(jre_dir, jre_dependency["jre_home_path"]))
        jre_path = str(PurePath(jre_dir, jre_dependency["jre_path"]))

        if not os.path.exists(jre_path):
            logger.log(f"Downloading JRE for BSL Language Server from {jre_dependency['url']}", logging.INFO)
            FileUtils.download_and_extract_archive(logger, jre_dependency["url"], jre_dir, jre_dependency["archiveType"])
            if os.path.exists(jre_path):
                os.chmod(jre_path, 0o755)

        assert os.path.exists(jre_home_path), f"JRE home not found at {jre_home_path}"
        assert os.path.exists(jre_path), f"JRE executable not found at {jre_path}"

        # Setup BSL Language Server JAR
        bsl_dependency = runtime_dependencies["bsl-language-server"]["platform-agnostic"]
        bsl_dir = str(PurePath(cls.ls_resources_dir(solidlsp_settings), "bsl-language-server"))
        os.makedirs(bsl_dir, exist_ok=True)

        bsl_ls_jar_path = str(PurePath(bsl_dir, bsl_dependency["relative_extraction_path"]))

        if not os.path.exists(bsl_ls_jar_path):
            logger.log(f"Downloading BSL Language Server from {bsl_dependency['url']}", logging.INFO)
            FileUtils.download_and_extract_archive(logger, bsl_dependency["url"], bsl_dir, bsl_dependency["archiveType"])

        assert os.path.exists(bsl_ls_jar_path), f"BSL Language Server JAR not found at {bsl_ls_jar_path}"

        return BslRuntimeDependencyPaths(
            jre_path=jre_path,
            jre_home_path=jre_home_path,
            bsl_ls_jar_path=bsl_ls_jar_path,
        )

    def _get_initialize_params(self, repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize parameters for the BSL Language Server.
        """
        if not os.path.isabs(repository_absolute_path):
            repository_absolute_path = os.path.abspath(repository_absolute_path)

        repo_uri = pathlib.Path(repository_absolute_path).as_uri()

        initialize_params = {
            "locale": "ru",  # BSL Language Server supports Russian locale
            "rootPath": repository_absolute_path,
            "rootUri": repo_uri,
            "capabilities": {
                "workspace": {
                    "applyEdit": True,
                    "workspaceEdit": {
                        "documentChanges": True,
                        "resourceOperations": ["create", "rename", "delete"],
                        "failureHandling": "textOnlyTransactional",
                    },
                    "didChangeConfiguration": {"dynamicRegistration": True},
                    "didChangeWatchedFiles": {"dynamicRegistration": True},
                    "symbol": {
                        "dynamicRegistration": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                    "executeCommand": {"dynamicRegistration": True},
                    "workspaceFolders": True,
                },
                "textDocument": {
                    "publishDiagnostics": {
                        "relatedInformation": True,
                        "versionSupport": False,
                        "tagSupport": {"valueSet": [1, 2]},
                    },
                    "synchronization": {"dynamicRegistration": True, "willSave": True, "willSaveWaitUntil": True, "didSave": True},
                    "completion": {
                        "dynamicRegistration": True,
                        "contextSupport": True,
                        "completionItem": {
                            "snippetSupport": True,
                            "commitCharactersSupport": True,
                            "documentationFormat": ["markdown", "plaintext"],
                            "deprecatedSupport": True,
                        },
                    },
                    "hover": {"dynamicRegistration": True, "contentFormat": ["markdown", "plaintext"]},
                    "signatureHelp": {"dynamicRegistration": True},
                    "definition": {"dynamicRegistration": True, "linkSupport": True},
                    "references": {"dynamicRegistration": True},
                    "documentSymbol": {
                        "dynamicRegistration": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                        "hierarchicalDocumentSymbolSupport": True,
                    },
                    "codeAction": {"dynamicRegistration": True},
                    "formatting": {"dynamicRegistration": True},
                    "rangeFormatting": {"dynamicRegistration": True},
                },
            },
            "initializationOptions": {
                "language": "ru",  # Set Russian language for diagnostics
                "diagnosticLanguage": "ru",
                "traceLevel": "off",  # Can be "off", "messages", "verbose"
            },
            "processId": os.getpid(),
            "workspaceFolders": [
                {
                    "uri": repo_uri,
                    "name": os.path.basename(repository_absolute_path),
                }
            ],
        }

        return initialize_params

    def _start_server(self):
        """
        Starts the BSL Language Server and waits for initialization to complete.
        """

        def execute_client_command_handler(params):
            return []

        def do_nothing(params):
            return

        def window_log_message(msg):
            """
            Monitor BSL Language Server's log messages.
            """
            message_text = msg.get("message", "")
            self.logger.log(f"LSP: window/logMessage: {message_text}", logging.INFO)

            # Look for signals that indicate the server is ready
            if any(
                phrase in message_text.lower()
                for phrase in ["server started", "initialization complete", "ready", "сервер запущен", "инициализация завершена"]
            ):
                self.logger.log("BSL Language Server ready signal detected", logging.INFO)
                self.service_ready_event.set()
                self.completions_available.set()

        def register_capability_handler(params):
            """Handle capability registration from BSL Language Server"""
            if "registrations" in params:
                for registration in params["registrations"]:
                    if registration["method"] == "textDocument/completion":
                        self.completions_available.set()
            return

        # Set up notification handlers
        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_request("workspace/executeClientCommand", execute_client_command_handler)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        self.logger.log("Starting BSL Language Server process", logging.INFO)
        self.server.start()

        # Send proper initialization parameters
        initialize_params = self._get_initialize_params(self.repository_root_path)

        self.logger.log(
            "Sending initialize request from LSP client to BSL server and awaiting response",
            logging.INFO,
        )
        init_response = self.server.send.initialize(initialize_params)
        self.logger.log(f"Received initialize response from BSL server: {init_response}", logging.INFO)

        # Verify that the server supports our required features
        assert "textDocumentSync" in init_response["capabilities"]

        # Check for completion provider (may be registered dynamically)
        if "completionProvider" in init_response["capabilities"]:
            self.completions_available.set()

        # Complete the initialization handshake
        self.server.notify.initialized({})

        # Wait for BSL Language Server to complete its initialization
        self.logger.log("Waiting for BSL Language Server to complete initialization...", logging.INFO)
        if self.service_ready_event.wait(timeout=10.0):
            self.logger.log("BSL Language Server initialization complete, server ready", logging.INFO)
        else:
            self.logger.log("Timeout waiting for BSL server ready signal, proceeding anyway", logging.WARNING)
            # Fallback: assume server is ready after timeout
            self.service_ready_event.set()
            self.completions_available.set()
