#!/usr/bin/env sh
set -eu

OMJ_REPO_ARCHIVE_ROOT="${OMJ_REPO_ARCHIVE_ROOT:-https://github.com/rlaope/oh-my-hermes/archive/refs}"
OMJ_CHANNEL="${OMJ_CHANNEL:-preview}"
OMJ_VERSION="${OMJ_VERSION:-}"
OMJ_PACKAGE_URL="${OMJ_PACKAGE_URL:-}"
OMJ_SOURCE_REF="${OMJ_SOURCE_REF:-}"
OMJ_PYTHON="${OMJ_PYTHON:-python3}"
OMJ_PIP_ARGS_WAS_SET="${OMJ_PIP_ARGS+x}"
OMJ_PIP_ARGS="${OMJ_PIP_ARGS:-}"
OMJ_INSTALL_MODE="${OMJ_INSTALL_MODE:-venv}"
OMJ_HOME_DIR="${HOME:-}"
if [ -z "${OMJ_VENV_DIR+x}" ]; then
  if [ -n "${XDG_DATA_HOME:-}" ]; then
    OMJ_VENV_DIR="$XDG_DATA_HOME/omj/venv"
  elif [ -n "$OMJ_HOME_DIR" ]; then
    OMJ_VENV_DIR="$OMJ_HOME_DIR/.local/share/omj/venv"
  else
    OMJ_VENV_DIR=""
  fi
fi
if [ -z "${OMJ_BIN_DIR+x}" ]; then
  if [ -n "$OMJ_HOME_DIR" ]; then
    OMJ_BIN_DIR="$OMJ_HOME_DIR/.local/bin"
  else
    OMJ_BIN_DIR=""
  fi
fi
OMJ_LINK_COMMAND="${OMJ_LINK_COMMAND:-1}"
OMJ_FORCE_LINK="${OMJ_FORCE_LINK:-0}"
OMJ_RUN_SETUP="${OMJ_RUN_SETUP:-0}"
OMJ_AUTO_APPLY="${OMJ_AUTO_APPLY:-1}"
OMJ_RUN_DOCTOR="${OMJ_RUN_DOCTOR:-1}"
OMJ_WITH_PLUGIN="${OMJ_WITH_PLUGIN:-0}"
OMJ_WITH_MCP="${OMJ_WITH_MCP:-0}"
OMJ_PROFILE_PACKS="${OMJ_PROFILE_PACKS:-}"
OMJ_SETUP_PROFILES="${OMJ_SETUP_PROFILES:-}"
OMJ_DEFAULT_EXECUTOR="${OMJ_DEFAULT_EXECUTOR:-}"
OMJ_SCOPE="${OMJ_SCOPE:-}"
OMJ_SETUP_ARGS="${OMJ_SETUP_ARGS:-}"
OMJ_LANG_RAW="${OMJ_LANG:-${OMJ_LANGUAGE:-}}"
OMJ_LANG_WAS_SET=0
if [ -n "$OMJ_LANG_RAW" ]; then
  OMJ_LANG_WAS_SET=1
fi
OMJ_RUNTIME_PYTHON="$OMJ_PYTHON"
OMJ_COMMAND_HINT=""
OMJ_INSTALL_STEP_COUNT=2
if [ "$OMJ_INSTALL_MODE" = "python" ]; then
  OMJ_INSTALL_STEP_COUNT=1
fi
OMJ_EXPOSE_STEP=$((OMJ_INSTALL_STEP_COUNT + 1))
OMJ_SETUP_STEP=$((OMJ_EXPOSE_STEP + 1))
OMJ_DOCTOR_STEP=$((OMJ_SETUP_STEP + 1))
OMJ_TOTAL_STEPS=$OMJ_EXPOSE_STEP
if [ "$OMJ_RUN_SETUP" = "1" ]; then
  OMJ_TOTAL_STEPS=$OMJ_DOCTOR_STEP
fi

say() {
  printf '%s\n' "$*"
}

use_color() {
  [ -t 1 ] && [ -z "${NO_COLOR:-}" ]
}

color() {
  if use_color; then
    printf '\033[%sm%s\033[0m' "$1" "$2"
  else
    printf '%s' "$2"
  fi
}

say_header() {
  printf '%s\n' "$(color '1;36' "$1")"
  if [ -n "${2:-}" ]; then
    printf '%s\n' "$2"
  fi
  printf '\n'
}

say_step() {
  printf '%s %s\n' "$(color '1;36' "$1")" "$2"
}

say_ok() {
  printf '      %s %s\n' "$(color '1;32' '[ok]')" "$1"
}

say_note() {
  printf '      %s %s\n' "$(color '1;33' '[note]')" "$1"
}

say_fail() {
  printf '      %s %s\n' "$(color '1;31' '[failed]')" "$1"
}

step_label() {
  printf '[%s/%s]' "$1" "$OMJ_TOTAL_STEPS"
}

normalize_omj_lang() {
  OMJ_LANG_KEY="$(printf '%s' "$1" | tr 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 'abcdefghijklmnopqrstuvwxyz')"
  case "$OMJ_LANG_KEY" in
    ""|en|eng|english)
      printf 'en'
      ;;
    ko|kr|kor|korean)
      printf 'ko'
      ;;
    ja|jp|jpn|japanese)
      printf 'ja'
      ;;
    zh|cn|zho|chi|chinese)
      printf 'zh'
      ;;
    *)
      printf 'omj installer: unsupported OMJ_LANG %s (expected en, ko, ja, or zh).\n' "$1" >&2
      exit 1
      ;;
  esac
}

OMJ_LANG="$(normalize_omj_lang "$OMJ_LANG_RAW")"

msg() {
  case "$OMJ_LANG:$1" in
    ko:installer_title) printf 'OMJ 설치 관리자' ;;
    ko:installer_subtitle) printf '시스템 Python 패키지를 건드리지 않고 oh-my-jeo를 설치합니다.' ;;
    ko:channel) printf '채널' ;;
    ko:mode) printf '모드' ;;
    ko:step_create_venv) printf '격리된 Python 환경 생성:' ;;
    ko:step_install_package) printf 'OMJ 패키지 설치' ;;
    ko:step_install_python) printf '선택한 Python에 OMJ 패키지 설치' ;;
    ko:step_expose_command) printf 'omj 명령어 연결' ;;
    ko:step_setup) printf '관리 Hermes 스킬 설정(명시적 선택)' ;;
    ko:step_doctor) printf '설치 확인' ;;
    ko:done) printf '완료' ;;
    ko:installed) printf 'oh-my-jeo 설치가 완료되었습니다.' ;;
    ko:next_path) printf '다음: '\''omj setup'\''으로 Hermes에 연결한 뒤, '\''omj doctor'\''로 확인하세요.' ;;
    ko:next_command_path) printf '다음: '\''%s setup'\''으로 Hermes에 연결한 뒤, '\''%s doctor'\''로 확인하세요. 또는 해당 디렉터리를 PATH에 추가하세요.' "$2" "$2" ;;
    ja:installer_title) printf 'OMJ インストーラー' ;;
    ja:installer_subtitle) printf 'システム Python パッケージを変更せずに oh-my-jeo をインストールします。' ;;
    ja:channel) printf 'チャンネル' ;;
    ja:mode) printf 'モード' ;;
    ja:step_create_venv) printf '分離された Python 環境を作成:' ;;
    ja:step_install_package) printf 'OMJ パッケージをインストール' ;;
    ja:step_install_python) printf '選択した Python に OMJ パッケージをインストール' ;;
    ja:step_expose_command) printf 'omj コマンドを公開' ;;
    ja:step_setup) printf '管理 Hermes スキルを設定（明示的に選択）' ;;
    ja:step_doctor) printf 'インストールを検証' ;;
    ja:done) printf '完了' ;;
    ja:installed) printf 'oh-my-jeo のインストールが完了しました。' ;;
    ja:next_path) printf '次に '\''omj setup'\'' で Hermes に接続し、'\''omj doctor'\'' で確認してください。' ;;
    ja:next_command_path) printf '次に '\''%s setup'\'' で Hermes に接続し、'\''%s doctor'\'' で確認してください。または、そのディレクトリを PATH に追加してください。' "$2" "$2" ;;
    zh:installer_title) printf 'OMJ 安装器' ;;
    zh:installer_subtitle) printf '在不改动系统 Python 包的情况下安装 oh-my-jeo。' ;;
    zh:channel) printf '频道' ;;
    zh:mode) printf '模式' ;;
    zh:step_create_venv) printf '创建隔离 Python 环境:' ;;
    zh:step_install_package) printf '安装 OMJ 包' ;;
    zh:step_install_python) printf '将 OMJ 包安装到所选 Python' ;;
    zh:step_expose_command) printf '公开 omj 命令' ;;
    zh:step_setup) printf '设置托管 Hermes 技能（显式选择）' ;;
    zh:step_doctor) printf '验证安装' ;;
    zh:done) printf '完成' ;;
    zh:installed) printf 'oh-my-jeo 已安装。' ;;
    zh:next_path) printf '下一步：运行 '\''omj setup'\'' 连接 Hermes，然后运行 '\''omj doctor'\'' 验证。' ;;
    zh:next_command_path) printf '下一步：运行 '\''%s setup'\'' 连接 Hermes，然后运行 '\''%s doctor'\'' 验证；也可以把该目录加入 PATH。' "$2" "$2" ;;
    *)
      case "$1" in
        installer_title) printf 'OMJ installer' ;;
        installer_subtitle) printf 'Install oh-my-jeo without touching system Python packages.' ;;
        channel) printf 'Channel' ;;
        mode) printf 'Mode' ;;
        step_create_venv) printf 'Create isolated Python environment at' ;;
        step_install_package) printf 'Install OMJ package' ;;
        step_install_python) printf 'Install OMJ package into selected Python' ;;
        step_expose_command) printf 'Expose the omj command' ;;
        step_setup) printf 'Set up managed Hermes skills (explicit opt-in)' ;;
        step_doctor) printf 'Verify installation' ;;
        done) printf 'done' ;;
        installed) printf 'oh-my-jeo is installed.' ;;
        next_path) printf 'Next: run '\''omj setup'\'' to connect OMJ to Hermes, then '\''omj doctor'\'' to verify.' ;;
        next_command_path) printf 'Next: run '\''%s setup'\'' to connect OMJ to Hermes, then '\''%s doctor'\'' to verify, or add its directory to PATH.' "$2" "$2" ;;
        *) printf '%s' "$1" ;;
      esac
      ;;
  esac
}

run_step() {
  OMJ_STEP_PREFIX="$1"
  OMJ_STEP_LABEL="$2"
  shift 2
  say_step "$OMJ_STEP_PREFIX" "$OMJ_STEP_LABEL"
  if OMJ_STEP_OUTPUT="$("$@" 2>&1)"; then
    say_ok "$(msg done)"
    return 0
  fi
  say_fail "$OMJ_STEP_LABEL"
  if [ -n "$OMJ_STEP_OUTPUT" ]; then
    printf '%s\n' "$OMJ_STEP_OUTPUT" | sed 's/^/      /'
  fi
  exit 1
}

run_omj() {
  "$OMJ_RUNTIME_PYTHON" -m omj.cli "$@"
}

find_omj_command() {
  if [ -n "$OMJ_COMMAND_HINT" ] && [ -e "$OMJ_COMMAND_HINT" ]; then
    printf '%s\n' "$OMJ_COMMAND_HINT"
    return 0
  fi
  if command -v omj >/dev/null 2>&1; then
    command -v omj
    return 0
  fi
  "$OMJ_RUNTIME_PYTHON" - "$OMJ_BIN_DIR" "$OMJ_VENV_DIR/bin" <<'PY'
import os
import shutil
import site
import sys
import sysconfig

found = shutil.which("omj")
if found:
    print(found)
    raise SystemExit(0)

names = ["omj.exe"] if os.name == "nt" else ["omj"]
schemes = [sysconfig.get_default_scheme()]
schemes.append("nt_user" if os.name == "nt" else "posix_user")

dirs = []
for directory in sys.argv[1:]:
    if directory and directory not in dirs:
        dirs.append(directory)

for scheme in schemes:
    try:
        path = sysconfig.get_path("scripts", scheme)
    except Exception:
        path = ""
    if path and path not in dirs:
        dirs.append(path)

user_base = getattr(site, "USER_BASE", "")
if user_base:
    user_bin = os.path.join(user_base, "Scripts" if os.name == "nt" else "bin")
    if user_bin not in dirs:
        dirs.append(user_bin)

for directory in dirs:
    for name in names:
        candidate = os.path.join(directory, name)
        if os.path.exists(candidate):
            print(candidate)
            raise SystemExit(0)
PY
}

link_omj_command() {
  if [ "$OMJ_LINK_COMMAND" != "1" ]; then
    return 0
  fi
  if [ -z "$OMJ_BIN_DIR" ]; then
    say "omj installer: OMJ_BIN_DIR is not set, so no omj command link was created."
    return 0
  fi
  OMJ_SOURCE_COMMAND="$OMJ_VENV_DIR/bin/omj"
  if [ ! -e "$OMJ_SOURCE_COMMAND" ]; then
    return 0
  fi
  mkdir -p "$OMJ_BIN_DIR"
  OMJ_TARGET_COMMAND="$OMJ_BIN_DIR/omj"
  if [ -e "$OMJ_TARGET_COMMAND" ] || [ -L "$OMJ_TARGET_COMMAND" ]; then
    OMJ_EXISTING_LINK="$(readlink "$OMJ_TARGET_COMMAND" 2>/dev/null || true)"
    if [ "$OMJ_EXISTING_LINK" = "$OMJ_SOURCE_COMMAND" ]; then
      OMJ_COMMAND_HINT="$OMJ_TARGET_COMMAND"
      return 0
    fi
    if [ "$OMJ_FORCE_LINK" = "1" ]; then
      ln -sf "$OMJ_SOURCE_COMMAND" "$OMJ_TARGET_COMMAND"
      OMJ_COMMAND_HINT="$OMJ_TARGET_COMMAND"
      return 0
    fi
    say "omj installer: $OMJ_TARGET_COMMAND already exists, so it was not replaced."
    say "Set OMJ_FORCE_LINK=1 to replace it, or use: $OMJ_SOURCE_COMMAND"
    OMJ_COMMAND_HINT="$OMJ_SOURCE_COMMAND"
    return 0
  fi
  ln -s "$OMJ_SOURCE_COMMAND" "$OMJ_TARGET_COMMAND"
  OMJ_COMMAND_HINT="$OMJ_TARGET_COMMAND"
}

install_into_venv() {
  if [ -z "$OMJ_VENV_DIR" ]; then
    say "omj installer: HOME or XDG_DATA_HOME is required for default venv install."
    say "Set OMJ_VENV_DIR to an explicit directory and retry."
    exit 1
  fi
  run_step "$(step_label 1)" "$(msg step_create_venv) $OMJ_VENV_DIR" "$OMJ_PYTHON" -m venv "$OMJ_VENV_DIR"
  OMJ_RUNTIME_PYTHON="$OMJ_VENV_DIR/bin/python"
  run_step "$(step_label 2)" "$(msg step_install_package)" sh -c '
    # Intentional shell splitting: OMJ_PIP_ARGS is an advanced operator escape hatch.
    # shellcheck disable=SC2086
    PIP_DISABLE_PIP_VERSION_CHECK=1 "$1" -m pip install --disable-pip-version-check -q --force-reinstall $2 --upgrade "$3"
  ' sh "$OMJ_RUNTIME_PYTHON" "$OMJ_PIP_ARGS" "$OMJ_PACKAGE_URL"
  OMJ_COMMAND_HINT="$OMJ_VENV_DIR/bin/omj"
  link_omj_command
}

install_into_python() {
  OMJ_DIRECT_PIP_ARGS="$OMJ_PIP_ARGS"
  if [ -z "$OMJ_PIP_ARGS_WAS_SET" ]; then
    OMJ_DIRECT_PIP_ARGS="--user"
  fi
  run_step "$(step_label 1)" "$(msg step_install_python)" sh -c '
    # Intentional shell splitting: OMJ_DIRECT_PIP_ARGS is an advanced operator escape hatch.
    # shellcheck disable=SC2086
    PIP_DISABLE_PIP_VERSION_CHECK=1 "$1" -m pip install --disable-pip-version-check -q --force-reinstall $2 --upgrade "$3"
  ' sh "$OMJ_PYTHON" "$OMJ_DIRECT_PIP_ARGS" "$OMJ_PACKAGE_URL"
  OMJ_RUNTIME_PYTHON="$OMJ_PYTHON"
}

if ! command -v "$OMJ_PYTHON" >/dev/null 2>&1; then
  say "omj installer: '$OMJ_PYTHON' was not found."
  say "Set OMJ_PYTHON to a Python 3.11+ executable and retry."
  exit 1
fi

if [ -z "$OMJ_PACKAGE_URL" ]; then
  case "$OMJ_CHANNEL" in
    preview)
      OMJ_PACKAGE_URL="$OMJ_REPO_ARCHIVE_ROOT/heads/main.zip"
      if [ -z "$OMJ_SOURCE_REF" ]; then
        OMJ_SOURCE_REF="main"
      fi
      ;;
    stable)
      if [ -z "$OMJ_VERSION" ]; then
        say "omj installer: OMJ_CHANNEL=stable requires OMJ_VERSION, for example OMJ_VERSION=1.0.1."
        exit 1
      fi
      case "$OMJ_VERSION" in
        v*) OMJ_TAG="$OMJ_VERSION" ;;
        *) OMJ_TAG="v$OMJ_VERSION" ;;
      esac
      OMJ_PACKAGE_URL="$OMJ_REPO_ARCHIVE_ROOT/tags/$OMJ_TAG.zip"
      if [ -z "$OMJ_SOURCE_REF" ]; then
        OMJ_SOURCE_REF="$OMJ_TAG"
      fi
      ;;
    local)
      say "omj installer: OMJ_CHANNEL=local requires OMJ_PACKAGE_URL to point at a local archive or path accepted by pip."
      exit 1
      ;;
    *)
      say "omj installer: unsupported OMJ_CHANNEL '$OMJ_CHANNEL' (expected preview, stable, or local)."
      exit 1
      ;;
  esac
elif [ -z "$OMJ_SOURCE_REF" ]; then
  case "$OMJ_CHANNEL" in
    local) OMJ_SOURCE_REF="local" ;;
    stable)
      if [ -n "$OMJ_VERSION" ]; then
        case "$OMJ_VERSION" in
          v*) OMJ_SOURCE_REF="$OMJ_VERSION" ;;
          *) OMJ_SOURCE_REF="v$OMJ_VERSION" ;;
        esac
      else
        OMJ_SOURCE_REF="custom-url"
      fi
      ;;
    preview) OMJ_SOURCE_REF="main" ;;
    *) OMJ_SOURCE_REF="custom-url" ;;
  esac
fi

say_header "$(msg installer_title)" "$(msg installer_subtitle)"
say_note "$(msg channel): $OMJ_CHANNEL"
say_note "Source ref: $OMJ_SOURCE_REF"
say_note "$(msg mode): $OMJ_INSTALL_MODE"
case "$OMJ_INSTALL_MODE" in
  venv)
    install_into_venv
    ;;
  python)
    install_into_python
    ;;
  *)
    say "omj installer: unsupported OMJ_INSTALL_MODE '$OMJ_INSTALL_MODE' (expected venv or python)."
    exit 1
    ;;
esac

OMJ_COMMAND_PATH="$(find_omj_command || true)"
if [ -n "$OMJ_COMMAND_PATH" ]; then
  say_step "$(step_label "$OMJ_EXPOSE_STEP")" "$(msg step_expose_command)"
  say_ok "$OMJ_COMMAND_PATH"
  if ! command -v omj >/dev/null 2>&1; then
    OMJ_COMMAND_DIR="$(dirname "$OMJ_COMMAND_PATH")"
    say_note "'$OMJ_COMMAND_DIR' is not on PATH for this shell."
    say_note "Add it with: export PATH=\"$OMJ_COMMAND_DIR:\$PATH\""
    say_note "Until then, use: $OMJ_COMMAND_PATH setup"
  fi
else
  say "omj installer: installed the package, but could not locate the omj command."
  say "Use '$OMJ_RUNTIME_PYTHON -m omj.cli setup' as a fallback and check the selected Python scripts directory."
fi

if [ "$OMJ_RUN_SETUP" = "1" ]; then
  set -- setup --channel "$OMJ_CHANNEL" --package-url "$OMJ_PACKAGE_URL" --source-ref "$OMJ_SOURCE_REF" --command-package-updated

  if [ "$OMJ_LANG_WAS_SET" = "1" ]; then
    set -- "$@" --language "$OMJ_LANG"
  fi

  if [ "$OMJ_CHANNEL" = "local" ] && [ -d "$OMJ_PACKAGE_URL" ]; then
    set -- "$@" --source "$OMJ_PACKAGE_URL"
  fi

  if [ "$OMJ_AUTO_APPLY" = "0" ]; then
    set -- "$@" --skip-apply
  fi

  if [ -n "$OMJ_VERSION" ]; then
    set -- "$@" --version "$OMJ_VERSION"
  fi

  if [ "$OMJ_WITH_PLUGIN" = "1" ]; then
    set -- "$@" --with-plugin
  fi

  if [ "$OMJ_WITH_MCP" = "1" ]; then
    set -- "$@" --with-mcp
  fi

  if [ -n "$OMJ_SCOPE" ]; then
    set -- "$@" --scope "$OMJ_SCOPE"
  fi

  if [ -n "$OMJ_PROFILE_PACKS" ]; then
    for OMJ_PROFILE_PACK in $(printf '%s' "$OMJ_PROFILE_PACKS" | tr ',' ' '); do
      set -- "$@" --profile-pack "$OMJ_PROFILE_PACK"
    done
  fi

  if [ -n "$OMJ_SETUP_PROFILES" ]; then
    for OMJ_SETUP_PROFILE in $(printf '%s' "$OMJ_SETUP_PROFILES" | tr ',' ' '); do
      set -- "$@" --profile "$OMJ_SETUP_PROFILE"
    done
  fi

  if [ -n "$OMJ_DEFAULT_EXECUTOR" ]; then
    set -- "$@" --default-executor "$OMJ_DEFAULT_EXECUTOR"
  fi

  if [ -n "$OMJ_SETUP_ARGS" ]; then
    # Intentional shell splitting: this is an advanced escape hatch for operators
    # who need to pass current omj setup flags before install.sh grows a stable
    # first-class environment variable for them.
    # shellcheck disable=SC2086
    set -- "$@" $OMJ_SETUP_ARGS
  fi

  say_step "$(step_label "$OMJ_SETUP_STEP")" "$(msg step_setup)"
  run_omj "$@"

  if [ "$OMJ_RUN_DOCTOR" = "0" ]; then
    say_note "Skipped doctor check because OMJ_RUN_DOCTOR=0."
  else
    say_step "$(step_label "$OMJ_DOCTOR_STEP")" "$(msg step_doctor)"
    if [ -n "$OMJ_SCOPE" ]; then
      run_omj --scope "$OMJ_SCOPE" doctor
    else
      run_omj doctor
    fi
  fi
elif [ "$OMJ_AUTO_APPLY" = "0" ] || [ "$OMJ_WITH_PLUGIN" = "1" ] || [ "$OMJ_WITH_MCP" = "1" ] || [ -n "$OMJ_SCOPE" ] || [ -n "$OMJ_PROFILE_PACKS" ] || [ -n "$OMJ_SETUP_PROFILES" ] || [ -n "$OMJ_DEFAULT_EXECUTOR" ] || [ -n "$OMJ_SETUP_ARGS" ] || [ "$OMJ_RUN_DOCTOR" = "0" ]; then
  say_note "Setup options were not applied because install.sh now installs the command only by default."
  say_note "Run 'omj setup' with those choices explicitly, or set OMJ_RUN_SETUP=1 for advanced one-shot bootstrap."
fi

printf '\n'
say "$(color '1;36' "$(msg installed)")"
if command -v omj >/dev/null 2>&1; then
  say "$(msg next_path)"
elif [ -n "$OMJ_COMMAND_PATH" ]; then
  say "$(msg next_command_path "$OMJ_COMMAND_PATH")"
else
  say "Next: run '$OMJ_PYTHON -m omj.cli setup' to connect OMJ to Hermes, then '$OMJ_PYTHON -m omj.cli doctor' to verify."
fi
