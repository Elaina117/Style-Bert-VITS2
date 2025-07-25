import subprocess
import sys
from typing import Any, Callable

from style_bert_vits2.logging import logger

# <<< 変更点: SAFE_STDOUTは使わないので削除、またはコメントアウト >>>
# from style_bert_vits2.utils.stdout_wrapper import SAFE_STDOUT


def run_script_with_log(
    cmd: list[str], ignore_warning: bool = False
) -> tuple[bool, str]:
    """
    指定されたコマンドを実行し、そのログを記録する。
    <<< 改造: 子プロセスの出力をリアルタイムで表示するように変更 >>>
    """

    logger.info(f"Running: {' '.join(cmd)}")
    
    # <<< START: ここからが変更箇所 >>>
    # subprocess.runからsubprocess.Popenに変更して、出力をリアルタイムで処理する
    process = subprocess.Popen(
        # is_windows()のような判定がないため、Windows環境ではsys.executableを先頭に追加する
        # Colab (Linux)では不要だが、汎用性のために追加
        [sys.executable] + cmd if sys.platform == "win32" else cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # 標準エラーも標準出力にマージする
        text=True,
        encoding="utf-8",
        bufsize=1,  # 1行ずつのバッファリングを強制
    )
    
    assert process.stdout is not None
    output_message = ""
    
    # 1行ずつリアルタイムで読み込んで表示する
    for line in iter(process.stdout.readline, ""):
        # tqdmのバーと混ざらないように、先頭と末尾の空白を削除
        line_stripped = line.strip()
        if line_stripped:
            # 標準のprint関数で直接コンソールに出力
            print(line_stripped, flush=True)
        output_message += line
    
    process.wait()
    # <<< END: 変更箇所はここまで >>>

    if process.returncode != 0:
        logger.error(f"Error: {' '.join(cmd)}\n{output_message}")
        return False, output_message
    elif output_message and not ignore_warning:
        logger.warning(f"Warning: {' '.join(cmd)}\n{output_message}")
        return True, output_message
    logger.success(f"Success: {' '.join(cmd)}")

    return True, ""


def second_elem_of(
    original_function: Callable[..., tuple[Any, Any]]
) -> Callable[..., Any]:
    """
    与えられた関数をラップし、その戻り値の 2 番目の要素のみを返す関数を生成する。

    Args:
        original_function (Callable[..., tuple[Any, Any]])): ラップする元の関数

    Returns:
        Callable[..., Any]: 元の関数の戻り値の 2 番目の要素のみを返す関数
    """

    def inner_function(*args, **kwargs) -> Any:  # type: ignore
        return original_function(*args, **kwargs)[1]

    return inner_function