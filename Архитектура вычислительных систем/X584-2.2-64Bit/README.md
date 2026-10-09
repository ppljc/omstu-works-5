**English** | [Русский](README-ru.md)

# X584

X584 is a graphical simulator of Soviet-era [K584VM1](https://ru.wikipedia.org/wiki/%D0%9C%D0%B8%D0%BA%D1%80%D0%BE%D0%BF%D1%80%D0%BE%D1%86%D0%B5%D1%81%D1%81%D0%BE%D1%80%D0%BD%D0%B0%D1%8F_%D1%81%D0%B5%D0%BA%D1%86%D0%B8%D1%8F#%D0%A1%D0%B5%D1%80%D0%B8%D1%8F_584) 4-bit slice microprocessor (a clone of [Texas Instruments SBP0400](https://en.wikipedia.org/wiki/Texas_Instruments_SBP0400)).

![Screenshot](Screenshot.png?raw=true)

## Features

* Simulation of 4 microprocessor slices that are cascaded to form 16-bit microprocessor.
* Drag-and-drop editing of microcode.
* Support for full 9-bit microinstruction set.
* Displaying and editing current microprocessor state.
* Integrated debugger with support for step-by-step execution and breakpoints.
* Conditional execution via control flow statements.

## Installation

Download the latest release of X584 from the [Releases](https://github.com/kodemeister/X584/releases) page and run the Windows installer for automatic setup. You can also download the ZIP archive, unpack it to any folder, and run `X584.exe`.

## Building from Source

### Prerequisites

1. Install RAD Studio 12.
2. Install Microsoft HTML Help Workshop.
> [!NOTE]
> It looks like Microsoft removed HTML Help Workshop from their website. You can still download it from the [web archive](https://web.archive.org/web/20200918004813/https://download.microsoft.com/download/0/A/9/0A939EF6-E31C-430F-A3DF-DFAE7960D564/htmlhelp.exe) or install it via Chocolatey.
3. Add the installation directory of HTML Help Workshop (typically `C:\Program Files (x86)\HTML Help Workshop`) to your `PATH` environment variable.
4. Install Inno Setup 6.
5. Add the installation directory of Inno Setup (typically `C:\Program Files (x86)\Inno Setup 6`) to your `PATH` environment variable.

### Building Microsoft Office 2000 Components

First, you need to compile the Microsoft Office 2000 components from source using modern Clang-enhanced C++ compilers. This is necessary because the existing Microsoft Office 2000 components provided with RAD Studio only support the legacy 32-bit `BCC32` compiler.

1. Open `Dependencies\Office2K\Office2K.cbproj` in RAD Studio.
2. In the main menu, select `Component > Install Packages...`. Uncheck the package `Embarcadero C++Builder Office 2000 Servers Package`, then click `Save`.
3. In the `Projects` window, select the `Windows 32-bit` target platform and the `Release` build configuration.
4. Right-click on `Office2K.bpl` and select `Install` from the context menu.
5. If you also want to build the 64-bit version of X584, select the `Windows 64-bit` or `Windows 64-bit (Modern)` target platform and the desired build configuration. Right-click on `Office2K.bpl` and select `Build` from the context menu.

The compiled packages will be installed to the shared directory `C:\Users\Public\Documents\Embarcadero\Studio\23.0`.

### Building X584

1. Open `X584.cbproj` in RAD Studio.
2. RAD Studio may display an error message indicating that it cannot load either the `Office2K` or `bcboffice2k290` package due to a conflict between them. Click `Yes` to continue.
3. In the `Projects` window, select the desired target platform and build configuration, then build the project.

The compiled executable and CHM help file will be located in the `<platform>\<configuration>` directory, e.g., `Win32\Debug`.

### Building the Installer

1. Build the project for the desired target platform using the `Release` build configuration.
2. Run the `Installer\Build.bat` script.

The generated installer will be located in the `<platform>\Release` directory, e.g., `Win32\Release`.
