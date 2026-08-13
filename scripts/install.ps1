# DevGuard 一键安装引导（Windows PowerShell）。
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 <目标目录> [setup_scaffold.py 参数...]
#   irm <raw-url>/scripts/install.ps1 | iex   （在已克隆的 devguard 仓目录内执行）
#
# 职责：探测 Python >= 3.10 → 定位 devguard 仓 → 原样透传参数调用
# scripts/setup_scaffold.py。失败闭合：不自动安装 Python、不静默降级、
# 不自动 clone 仓库。
#
# devguard 仓定位顺序：
#   1. -Repo <路径>（安装器自身参数，会被消费、不透传）
#   2. 环境变量 DEVGUARD_REPO
#   3. 脚本所在目录的上一级（本地执行时）
#   4. 当前工作目录
#
# Python 探测顺序：DEVGUARD_PYTHON（若设置，强制使用）→ py -3 → python。
[CmdletBinding()]
param(
    [string]$Repo = "",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Passthrough = @()
)

$ErrorActionPreference = 'Stop'
$MinMajor = 3
$MinMinor = 10

function Write-PythonGuidance {
    @'
未找到 Python >= 3.10。请先安装再重试（安装器不会自动安装 Python）：
  - winget:       winget install Python.Python.3.12
  - 官网安装包:    https://www.python.org/downloads/（勾选 "Add python.exe to PATH"）
  - macOS/Linux:  使用 scripts/install.sh（curl | bash）
'@ | Write-Host
}

function Write-RepoGuidance {
    @'
未找到 devguard 仓（缺少 scripts/setup_scaffold.py）。请任选其一：
  1. git clone https://github.com/xiangbianpangde/devguard.git
     然后在仓内执行：powershell -File scripts/install.ps1 <目标目录> [参数...]
  2. 指定既有仓路径：install.ps1 -Repo <devguard 路径> <目标目录> [参数...]
     或设置环境变量 DEVGUARD_REPO=<devguard 路径>
'@ | Write-Host
}

function Get-PythonVersion([string]$Command, [string[]]$Prefix) {
    try {
        $out = & $Command @Prefix -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>$null
        if ($LASTEXITCODE -eq 0 -and $out -match '^\d+\.\d+') { return $out.Trim() }
    } catch { }
    return $null
}

function Test-MinVersion([string]$Version) {
    $parts = $Version.Split('.')
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    return ($major -gt $MinMajor) -or ($major -eq $MinMajor -and $minor -ge $MinMinor)
}

# 1) 探测 Python >= 3.10（$PyCmd 为命令 + 前缀参数的数组）
$PyCmd = $null
if ($env:DEVGUARD_PYTHON) {
    $ver = Get-PythonVersion $env:DEVGUARD_PYTHON @()
    if (-not $ver) {
        Write-Host "ERROR: DEVGUARD_PYTHON=$env:DEVGUARD_PYTHON 不可执行或不是 Python"; exit 1
    }
    if (-not (Test-MinVersion $ver)) {
        Write-Host "ERROR: DEVGUARD_PYTHON=$env:DEVGUARD_PYTHON 版本为 ${ver}，需要 >= ${MinMajor}.${MinMinor}"; exit 1
    }
    $PyCmd = @($env:DEVGUARD_PYTHON)
} else {
    $candidates = @(@('py', @('-3')), @('python', @()))
    foreach ($cand in $candidates) {
        if (-not (Get-Command $cand[0] -ErrorAction SilentlyContinue)) { continue }
        $ver = Get-PythonVersion $cand[0] $cand[1]
        if ($ver -and (Test-MinVersion $ver)) {
            $PyCmd = @($cand[0]) + $cand[1]
            break
        }
    }
    if (-not $PyCmd) {
        Write-PythonGuidance
        exit 1
    }
}

# 1.5) ensurepip 预检（2026-08-13 蓝队方案③：fail-closed，提前报错）
$pyPrefixCheck = @()
if ($PyCmd.Count -gt 1) { $pyPrefixCheck = @($PyCmd[1..($PyCmd.Count - 1)]) }
& $PyCmd[0] @pyPrefixCheck -m ensurepip --version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'ERROR: ensurepip 不可用（无法创建带 pip 的虚拟环境）。请先修复 Python 安装（重新运行 Python 安装包并勾选 pip / Repair）。'
    exit 1
}

# 2) 定位 devguard 仓
if (-not $Repo -and $env:DEVGUARD_REPO) { $Repo = $env:DEVGUARD_REPO }
if (-not $Repo -and $PSScriptRoot) {
    $parent = Split-Path -Parent $PSScriptRoot
    if (Test-Path (Join-Path $parent 'scripts/setup_scaffold.py')) { $Repo = $parent }
}
if (-not $Repo -and (Test-Path (Join-Path (Get-Location) 'scripts/setup_scaffold.py'))) {
    $Repo = (Get-Location).Path
}
if (-not $Repo -or -not (Test-Path (Join-Path $Repo 'scripts/setup_scaffold.py'))) {
    Write-RepoGuidance
    exit 1
}

# 3) 透传调用（退出码原样传递）
Write-Host "DevGuard installer: python=$($PyCmd -join ' ') repo=$Repo"
$pyPrefix = @()
if ($PyCmd.Count -gt 1) { $pyPrefix = @($PyCmd[1..($PyCmd.Count - 1)]) }
& $PyCmd[0] @pyPrefix (Join-Path $Repo 'scripts/setup_scaffold.py') @Passthrough
exit $LASTEXITCODE
