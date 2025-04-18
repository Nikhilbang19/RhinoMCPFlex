# RhinoMCP - Rhino Model Context Protocol Integration

RhinoMCP connects Rhino and Grasshopper to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control Rhino + Grasshopper. This integration enables prompt-assisted 3D modeling, scene creation, and manipulation.

## Features

#### Rhino
- **Two-way communication**: Connect Claude AI to Rhino through a socket-based server.
- **Object manipulation and management**: Create and modify 3D objects in Rhino including metadata.
- **Layer management**: View and interact with Rhino layers.
- **Scene inspection**: Get detailed information about the current Rhino scene (incl. screencapture).
- **Code execution**: Run arbitrary Python code in Rhino from Claude.

#### Grasshopper
- **Code execution**: Run arbitrary Python code in Grasshopper from Claude - includes the generation of gh components.
- **Gh canvas inspection**: Get detailed information about your Grasshopper definition, including component graph and parameters.
- **Component management**: Update script components, modify parameters, and manage code references.
- **External code integration**: Link script components to external Python files for better code organization.
- **Real-time feedback**: Get component states, error messages, and runtime information.
- **Non-blocking communication**: Stable two-way communication via HTTP server.

## Components

The system consists of two main components:

1.  **Rhino-side Script (`rhino_mcp/rhino_mcp_client.py`)**: A Python script that runs inside Rhino to create a socket server that receives and executes commands.
2.  **MCP Server (`rhino_mcp/rhino_mcp/server.py`)**: A Python server that implements the Model Context Protocol and connects to the Rhino script.

## Installation

### Prerequisites

- Rhino 7 or newer
- Python 3.10 or newer
- Conda (recommended for environment management)

### Setting up the Environment

1.  **Create Environment**: If using Conda, create a new environment:
    ```bash
    conda create -n rhino_mcp python=3.10
    conda activate rhino_mcp
    ```
2.  **Install Dependencies**: Run the provided installation script:
    ```bash
    install_rhino_mcp.bat
    ```
    This will install required Python packages and the `rhino-mcp` package itself in editable mode.

### Running the System

1.  **Start Rhino Script**:
    - Open Rhino 7.
    - Open the Python Editor (`Tools` > `Python Script` > `Run..`).
    - Navigate to and select `rhino_mcp_client.py`.
    - Verify you see startup messages in the Python Editor console.

2.  **Start Grasshopper Integration (Optional)**:
    - Open Grasshopper in Rhino.
    - Open the `rhino_mcp/grasshopper_mcp_client.gh` file. This starts the HTTP server component.

3.  **Configure Claude Desktop / Cursor IDE**:
    - Add the MCP server configuration to your Claude Desktop or Cursor IDE settings.

    **For Claude Desktop (`claude_desktop_config.json`)**:
    ```json
    {
      "mcpServers": {
        "rhino": {
          "command": "/path/to/your/conda/envs/rhino_mcp/bin/python",
          "args": [
            "-m",
            "rhino_mcp.server"
          ]
        }
      }
    }
    ```

    **For Cursor IDE (`~/.cursor/mcp.json`)**:
    ```json
    {
      "mcpServers": {
        "rhino": {
          "command": "/path/to/your/conda/envs/rhino_mcp/bin/python",
          "args": [
            "-m",
            "rhino_mcp.server"
          ]
        }
      }
    }
    ```
    *Replace `/path/to/your/conda/envs/rhino_mcp/bin/python` with the actual full path to the Python interpreter in your `rhino_mcp` environment.*

4.  **Start Claude**: Once configured, Claude Desktop/Cursor will automatically start the MCP server when needed and connect to Rhino/Grasshopper.

### Managing the Connection

- To stop the Rhino script server:
  - In the Rhino Python Editor, type `stop_server()` and press Enter.
  - You should see "RhinoMCP server stopped" in the output.

## Troubleshooting

-   **Connection issues**:
    -   Ensure the Rhino script is running (check Python Editor output).
    -   Verify port 9876 (Rhino) and 9999 (Grasshopper) are not in use.
    -   Check that both Rhino and Claude Desktop/Cursor IDE are running.
-   **Script not starting**:
    -   Make sure you're using Rhino 7 or newer.
    -   Check the Python Editor for any error messages.
-   **Package not found / ModuleNotFoundError**:
    -   Ensure you ran `install_rhino_mcp.bat` successfully.
    -   Verify your `rhino_mcp` conda environment (if used) is activated.
    -   Confirm the Python path in the Claude/Cursor config points to the correct environment.

## Limitations

-   The `execute_rhino_code` and `execute_code_in_gh` tools allow running arbitrary Python code. Use with caution.
-   Grasshopper integration requires the HTTP server component (`grasshopper_mcp_client.gh`) to be running in Grasshopper.
-   External code references in Grasshopper require careful file path management.

## Extending

To add new functionality:

1.  Add new command handlers and functions in `rhino_mcp_client.py` and the `RhinoTools`/`GrasshopperTools` classes in the server code.
2.  Register corresponding MCP tools in `server.py` with appropriate descriptions.

## License

This project is open source and available under the MIT License. 